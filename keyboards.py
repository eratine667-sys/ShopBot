from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:
    """
    Создает главное меню с двумя инлайн-кнопками:
    - Каталог
    - Броня
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки
    builder.add(InlineKeyboardButton(
        text="📋 Выберите каталог",
        callback_data="catalog"
    ))
    builder.add(InlineKeyboardButton(
        text="📅 Броня",
        callback_data="booking"
    ))
    
    # Располагаем кнопки в один ряд (или можно в два, убрав adjust)
    builder.adjust(1)  # По одной в ряду (будут друг под другом)
    # Если хотите в один ряд - замените на builder.adjust(2)
    
    return builder.as_markup()

# Если нужна клавиатура для подменю каталога
def get_catalog_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="back_to_main"
    ))
    return builder.as_markup()
