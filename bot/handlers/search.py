"""
Хендлеры для поиска товаров.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from data.data import search_items

logger = logging.getLogger(__name__)


async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать поиск товара."""
    await update.message.reply_text(
        "🔍 <b>Поиск товаров</b>\n\n"
        "Введите ключевое слово для поиска (например: наушники, iPhone, часы):\n\n"
        "Ищем по названию и описанию товаров.",
        parse_mode="HTML"
    )
    return "WAITING_FOR_SEARCH_QUERY"


async def process_search_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработать поисковый запрос."""
    query_text = update.message.text.strip()
    
    if len(query_text) < 2:
        await update.message.reply_text(
            "❌ Слишком короткий запрос. Введите хотя бы 2 символа."
        )
        return "WAITING_FOR_SEARCH_QUERY"
    
    results = search_items(query_text)
    
    if not results:
        await update.message.reply_text(
            f"😔 По запросу \"{query_text}\" ничего не найдено.\n\n"
            "Попробуйте другой поисковый запрос или воспользуйтесь каталогом."
        )
        return "WAITING_FOR_SEARCH_QUERY"
    
    # Формируем результаты поиска
    text = f"🔍 <b>Результаты поиска по запросу \"{query_text}\"</b>\n\n"
    text += f"Найдено товаров: {len(results)}\n\n"
    
    keyboard = []
    for item in results[:10]:  # Ограничиваем 10 результатами
        status_emoji = "✅" if item["status"] == "available" else "🔒"
        price_formatted = f"{item['price']:,}".replace(",", " ")
        text += f"{status_emoji} <b>{item['title']}</b> — {price_formatted} ₽\n"
        keyboard.append([InlineKeyboardButton(
            f"👁 {item['title']}",
            callback_data=f"view_item_{item['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🛍 Весь каталог", callback_data="back_to_catalog")])
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    
    return "WAITING_FOR_SEARCH_QUERY"


async def search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки поиска."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("view_item_"):
        from handlers.catalog import show_item_card
        item_id = int(data.split("_")[-1])
        await show_item_card(query, context, item_id)
    elif data == "back_to_catalog":
        from handlers.catalog import show_catalog_from_callback
        await show_catalog_from_callback(query, context, page=0)
    elif data == "main_menu":
        from handlers.main_menu import show_main_menu
        await show_main_menu(query, context)


def get_handlers():
    """Получить список хендлеров для поиска."""
    from telegram.ext import ConversationHandler
    
    search_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("search", start_search)],
        states={
            "WAITING_FOR_SEARCH_QUERY": [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_search_query)
            ]
        },
        fallbacks=[],
        allow_reentry=True
    )
    
    return [
        search_conv_handler,
        CallbackQueryHandler(search_callback, pattern=r"^view_item_\d+"),
    ]
