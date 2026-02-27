import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from config import BOT_TOKEN
from keyboards import get_main_menu, get_catalog_menu

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Отправляет приветствие и показывает инлайн-кнопки"""
    user_name = message.from_user.first_name
    
    await message.answer(
        f"👋 Привет, {user_name}!\n\n"
        f"Я бот-помощник. Выберите действие:",
        reply_markup=get_main_menu()  # Показываем инлайн-кнопки
    )

# Обработчик нажатий на инлайн-кнопки
@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    """Обрабатывает все нажатия на инлайн-кнопки"""
    
    if callback.data == "catalog":
        await callback.message.edit_text(
            "📋 Вы выбрали каталог.\n"
            "Здесь будет список товаров или услуг.",
            reply_markup=get_catalog_menu()  # Можете добавить кнопку "Назад"
        )
        await callback.answer()  # Убираем "часики" на кнопке
        
    elif callback.data == "booking":
        await callback.message.edit_text(
            "📅 Вы выбрали бронирование.\n"
            "Здесь будет форма для записи.",
            reply_markup=get_catalog_menu()  # Пока то же меню с "Назад"
        )
        await callback.answer()
        
    elif callback.data == "back_to_main":
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=get_main_menu()
        )
        await callback.answer()

# Запуск бота (polling)
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
