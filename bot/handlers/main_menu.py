"""
Главное меню бота.
Стартовое сообщение и основные кнопки навигации.
"""
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

logger = logging.getLogger(__name__)


# Основное меню с кнопками
MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🛍 Каталог"), KeyboardButton("🔍 Поиск")],
        [KeyboardButton("❓ FAQ"), KeyboardButton("📋 Мои бронирования")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user = update.effective_user
    
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        f"Добро пожаловать в магазин электроники! 🎉\n\n"
        f"Здесь вы можете:\n"
        f"• 🛍 Просмотреть каталог товаров\n"
        f"• 🔍 Найти нужный товар\n"
        f"• ❓ Узнать ответы на частые вопросы\n"
        f"• 📋 Забронировать товар\n\n"
        f"Выберите действие в меню ниже 👇"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=MAIN_MENU_KEYBOARD
    )


async def menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок главного меню."""
    text = update.message.text
    
    if text == "🛍 Каталог":
        from handlers.catalog import show_catalog
        await show_catalog(update, context, page=0)
    elif text == "🔍 Поиск":
        from handlers.search import start_search
        await start_search(update, context)
    elif text == "❓ FAQ":
        from handlers.faq import show_faq
        await show_faq(update, context)
    elif text == "📋 Мои бронирования":
        from handlers.booking import my_bookings
        await my_bookings(update, context)


async def show_main_menu(update: Update | CallbackQueryHandler, context: ContextTypes.DEFAULT_TYPE):
    """Показать главное меню из callback запроса."""
    # Определяем тип обновления
    if hasattr(update, 'edit_message_text'):
        # Это callback query
        query = update
        await query.answer()
        
        user = query.from_user
        
        menu_text = (
            f"👋 Привет, {user.first_name}!\n\n"
            f"<b>Главное меню</b>\n\n"
            f"Выберите действие:"
        )
        
        # Создаём инлайн-клавиатуру для главного меню
        keyboard = [
            [InlineKeyboardButton("🛍 Каталог", callback_data="show_catalog")],
            [InlineKeyboardButton("🔍 Поиск", callback_data="show_search")],
            [InlineKeyboardButton("❓ FAQ", callback_data="show_faq")],
            [InlineKeyboardButton("📋 Мои бронирования", callback_data="my_bookings")]
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
            "🔍 <b>Поиск товаров</b>\n\n"
            "Для поиска используйте команду /search в чате.",
            parse_mode="HTML"
        )
    elif data == "show_faq":
        from handlers.faq import show_faq_from_callback
        await show_faq_from_callback(query, context)
    elif data == "my_bookings":
        from handlers.booking import my_bookings_callback
        await my_bookings_callback(query, context)


def get_handlers():
    """Получить список хендлеров для главного меню."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    return [
        CommandHandler("start", start_command),
        CallbackQueryHandler(main_menu_callback, pattern=r"^main_menu$"),
        CallbackQueryHandler(main_menu_callback, pattern=r"^show_catalog$"),
        CallbackQueryHandler(main_menu_callback, pattern=r"^show_search$"),
        CallbackQueryHandler(main_menu_callback, pattern=r"^show_faq$"),
    ]
