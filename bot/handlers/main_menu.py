"""
Главное меню бота.
Стартовое сообщение и основные кнопки навигации.
"""
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

logger = logging.getLogger(__name__)


# Основное меню с кнопками
MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🛍 Покупать"), KeyboardButton("➕ Продать")],
        [KeyboardButton("⭐ Избранное"), KeyboardButton("❓ FAQ")],
        [KeyboardButton("📌 Мои объявления")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user = update.effective_user
    
    welcome_text = (
        f"Привет, {user.first_name}!\n\n"
        f"Добро пожаловать в ShopMatch — простую площадку для покупки и продажи вещей.\n\n"
        f"Здесь вы можете:\n"
        f"• Просмотреть объявления\n"
        f"• Выставить свой товар на продажу\n"
        f"• Управлять своими объявлениями\n"
        f"• Сохранить интересные объявления\n\n"
        f"Начните с просмотра каталога или создайте объявление."
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=MAIN_MENU_KEYBOARD
    )


async def menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок главного меню."""
    text = update.message.text
    
    if text == "🛍 Покупать" or text == "Покупать":
        from handlers.browse import start_browsing
        await start_browsing(update, context)
    elif text == "⭐ Избранное" or text == "Избранное":
        from handlers.favorites import show_favorites
        await show_favorites(update, context)
    elif text == "➕ Продать" or text == "Продать":
        from handlers.sell import sell_start
        await sell_start(update, context)
    elif text == "📌 Мои объявления" or text == "Мои объявления":
        from handlers.my_items import show_my_items
        await show_my_items(update, context)
    elif text == "❓ FAQ" or text == "FAQ":
        from handlers.faq import show_faq
        await show_faq(update, context)


async def show_main_menu(update: Update | CallbackQueryHandler, context: ContextTypes.DEFAULT_TYPE):
    """Показать главное меню из callback запроса."""
    # Определяем тип обновления
    if hasattr(update, 'edit_message_text'):
        # Это callback query
        query = update
        await query.answer()
        
        user = query.from_user
        
        menu_text = (
            f"Привет, {user.first_name}!\n\n"
            f"<b>Главное меню</b>\n\n"
            f"Выберите действие:"
        )
        
        # Создаём инлайн-клавиатуру для главного меню
        keyboard = [
            [InlineKeyboardButton("🛒 Каталог", callback_data="show_catalog")],
            [InlineKeyboardButton("🔍 Поиск", callback_data="show_search")],
            [InlineKeyboardButton("📌 Мои объявления", callback_data="show_my_items")],
            [InlineKeyboardButton("❓ FAQ", callback_data="show_faq")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        # Это обычное сообщение - показываем клавиатуру
        await start_command(update, context)


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки главного меню в inline режиме."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "show_catalog":
        from handlers.catalog import show_catalog_from_callback
        await show_catalog_from_callback(query, context, page=0)
    elif data == "show_search":
        await query.edit_message_text(
            "<b>Поиск товаров</b>\n\n"
            "Для поиска используйте команду /search в чате.",
            parse_mode="HTML"
        )
    elif data == "show_my_items":
        from handlers.my_items import show_my_items
        await show_my_items(update, context)
    elif data == "show_faq":
        from handlers.faq import show_faq_from_callback
        await show_faq_from_callback(query, context)
    # В текущем варианте бронирования отключены


def get_handlers():
    """Получить список хендлеров для главного меню."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    return [
        CommandHandler("start", start_command),
        CallbackQueryHandler(main_menu_callback, pattern=r"^main_menu$"),
        CallbackQueryHandler(main_menu_callback, pattern=r"^show_catalog$"),
        CallbackQueryHandler(main_menu_callback, pattern=r"^show_search$"),
        CallbackQueryHandler(main_menu_callback, pattern=r"^show_my_items$"),
        CallbackQueryHandler(main_menu_callback, pattern=r"^show_faq$"),
    ]
