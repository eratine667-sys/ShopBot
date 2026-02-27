import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from config import BOT_TOKEN, ADMIN_ID
from database import init_db, add_product, get_products_by_category, get_product, delete_product, add_user
from keyboards import *
from states import ProductStates, UserState

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

init_db()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(UserState.normal)
    add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"👋 Добро пожаловать в магазин!\n"
        f"Нажмите кнопку ниже чтобы перейти в магазин.",
        reply_markup=main_menu()
    )

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет доступа.")
        return
    await state.set_state(UserState.admin)
    await message.answer(
        "🔐 Админ-панель\nВыберите действие:",
        reply_markup=admin_panel()
    )

@dp.message(Command("user"))
async def cmd_user(message: types.Message, state: FSMContext):
    await state.set_state(UserState.normal)
    await message.answer(
        "👤 Вы в режиме пользователя",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "shop")
async def show_shop(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=shop_categories()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("cat_"))
async def show_category(callback: types.CallbackQuery):
    category = callback.data.replace("cat_", "")
    products = get_products_by_category(category)
    
    if not products:
        await callback.message.edit_text(
            f"В категории {category} пока нет товаров.",
            reply_markup=shop_categories()
        )
        await callback.answer()
        return
    
    text = f"📦 Категория: {category}\n\nВыберите товар:"
    await callback.message.edit_text(
        text,
        reply_markup=product_list(products, category)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("view_"))
async def view_product(callback: types.CallbackQuery):
    product_id = int(callback.data.replace("view_", ""))
    product = get_product(product_id)
    
    if not product:
        await callback.message.edit_text("Товар не найден.")
        await callback.answer()
        return
    
    text = f"""
🛍 {product['name']}

📝 {product['description']}

💰 Цена: {product['price']}₽
    """
    await callback.message.edit_text(
        text,
        reply_markup=product_actions(product_id)
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_cat")
async def back_to_cat(callback: types.CallbackQuery):
    await show_shop(callback)

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(callback: types.CallbackQuery):
    product_id = int(callback.data.replace("buy_", ""))
    product = get_product(product_id)
    
    if not product:
        await callback.message.edit_text("Товар не найден.")
        await callback.answer()
        return
    
    user_info = f"@{callback.from_user.username}" if callback.from_user.username else f"ID: {callback.from_user.id}"
    
    await bot.send_message(
        ADMIN_ID,
        f"🛒 Запрос на покупку!\n\n"
        f"Товар: {product['name']}\n"
        f"Категория: {product['category']}\n"
        f"Цена: {product['price']}₽\n\n"
        f"Покупатель: {user_info}"
    )
    
    await callback.message.edit_text(
        f"✅ Запрос на покупку отправлен!\n"
        f"Администратор свяжется с вами.",
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.message(F.text == "📦 Выставить товар")
async def add_product_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(ProductStates.waiting_for_category)
    await message.answer(
        "Введите категорию товара:\n"
        "(броня, расходники, талисманы, аккаунты)",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(ProductStates.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text.lower())
    await state.set_state(ProductStates.waiting_for_name)
    await message.answer("Введите название товара:")

@dp.message(ProductStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ProductStates.waiting_for_description)
    await message.answer("Введите описание товара:")

@dp.message(ProductStates.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ProductStates.waiting_for_price)
    await message.answer("Введите цену в рублях (только число):")

@dp.message(ProductStates.waiting_for_price)
async def process_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        data = await state.get_data()
        
        product_id = add_product(
            data['category'],
            data['name'],
            data['description'],
            price
        )
        
        await state.clear()
        await state.set_state(UserState.admin)
        
        await message.answer(
            f"✅ Товар успешно добавлен!\n"
            f"ID товара: {product_id}",
            reply_markup=admin_panel()
        )
    except ValueError:
        await message.answer("Пожалуйста, введите число.")

@dp.message(F.text == "❌ Отменить товар")
async def delete_product_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    products = []
    categories = ["броня", "расходники", "талисманы", "аккаунты"]
    for cat in categories:
        products.extend(get_products_by_category(cat))
    
    if not products:
        await message.answer("Нет товаров для удаления.")
        return
    
    await message.answer(
        "Выберите товар для удаления:",
        reply_markup=admin_delete_products(products)
    )

@dp.callback_query(F.data.startswith("del_"))
async def confirm_delete(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа")
        return
    
    product_id = int(callback.data.replace("del_", ""))
    product = get_product(product_id)
    
    if product:
        delete_product(product_id)
        await callback.message.edit_text(
            f"✅ Товар '{product['name']}' удален!",
            reply_markup=admin_panel()
        )
    await callback.answer()

@dp.callback_query(F.data == "done_delete")
async def done_delete(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа")
        return
    await callback.message.edit_text(
        "Админ-панель",
        reply_markup=admin_panel()
    )
    await callback.answer()

@dp.message(F.text == "👤 Выйти в пользовательский режим")
async def exit_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(UserState.normal)
    await message.answer(
        "👤 Вы перешли в режим пользователя",
        reply_markup=main_menu()
    )

@dp.message(F.text == "👑 Перейти в админку")
async def go_to_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет доступа к админке.")
        return
    await state.set_state(UserState.admin)
    await message.answer(
        "🔐 Админ-панель",
        reply_markup=admin_panel()
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
