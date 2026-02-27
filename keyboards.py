from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_panel():
    kb = [
        [KeyboardButton(text="📦 Выставить товар")],
        [KeyboardButton(text="❌ Отменить товар")],
        [KeyboardButton(text="👤 Выйти в пользовательский режим")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def user_panel():
    kb = [
        [KeyboardButton(text="👑 Перейти в админку")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def main_menu():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🛍 Магазин", callback_data="shop"))
    return builder.as_markup()

def shop_categories():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🛡 Броня", callback_data="cat_броня"))
    builder.add(InlineKeyboardButton(text="🔧 Расходники", callback_data="cat_расходники"))
    builder.add(InlineKeyboardButton(text="🔮 Талисманы/сферы", callback_data="cat_талисманы"))
    builder.add(InlineKeyboardButton(text="👤 Аккаунты без КД", callback_data="cat_аккаунты"))
    builder.adjust(1)
    return builder.as_markup()

def product_list(products, category):
    builder = InlineKeyboardBuilder()
    for p in products:
        builder.add(InlineKeyboardButton(
            text=f"{p['name']} - {p['price']}₽",
            callback_data=f"view_{p['id']}"
        ))
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="shop"))
    builder.adjust(1)
    return builder.as_markup()

def product_actions(product_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="💰 Купить", callback_data=f"buy_{product_id}"))
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_cat"))
    builder.adjust(1)
    return builder.as_markup()

def admin_delete_products(products):
    builder = InlineKeyboardBuilder()
    for p in products:
        builder.add(InlineKeyboardButton(
            text=f"❌ {p['name']}",
            callback_data=f"del_{p['id']}"
        ))
    builder.add(InlineKeyboardButton(text="◀️ Готово", callback_data="done_delete"))
    builder.adjust(1)
    return builder.as_markup()
