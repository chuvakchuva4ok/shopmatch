"""
Основной файл запуска Telegram-бота.
Собирает все хендлеры и запускает приложение.
"""
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from config import TELEGRAM_BOT_TOKEN, ADMIN_IDS
from handlers.main_menu import get_handlers as get_main_menu_handlers, menu_button_handler, MAIN_MENU_KEYBOARD
from handlers.browse import get_handlers as get_browse_handlers
from handlers.sell import get_handlers as get_sell_handlers
from handlers.favorites import get_handlers as get_favorites_handlers
from handlers.catalog import get_handlers as get_catalog_handlers
from handlers.search import get_handlers as get_search_handlers
from handlers.faq import get_handlers as get_faq_handlers
from handlers.my_items import get_handlers as get_my_items_handlers
from handlers.admin import get_handlers as get_admin_handlers

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    """Инициализация после запуска бота."""
    logger.info("Бот запущен!")
    bot = application.bot
    await bot.set_my_commands([
        ("start", "Запустить бота"),
        ("sell", "Создать объявление"),
        ("myitems", "Мои объявления")
    ])
    if ADMIN_IDS:
        logger.info(f"Администраторы: {ADMIN_IDS}")
    else:
        logger.warning("ADMIN_IDS не настроены! Админские команды будут недоступны.")


async def shutdown_callback(application: Application):
    """Обработчик завершения работы."""
    logger.info("Бот остановлен.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок."""
    logger.error(f"Ошибка при обработке обновления: {context.error}")
    
    if ADMIN_IDS and context.error:
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"Ошибка в боте:\n\n{context.error}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление об ошибке админу {admin_id}: {e}")


def main():
    """Основная функция запуска бота."""
    # Проверяем токен
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_bot_token_here":
        logger.error("❌ TELEGRAM_BOT_TOKEN не настроен!")
        logger.error("Пожалуйста, укажите токен бота в файле .env")
        return
    
    # Создаём приложение
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    
    # Добавляем хендлеры
    # Главное меню
    for handler in get_main_menu_handlers():
        application.add_handler(handler)
    
    # Покупка (просмотр карточек)
    for handler in get_browse_handlers():
        application.add_handler(handler)
    
    # Продажа (создание объявлений)
    for handler in get_sell_handlers():
        application.add_handler(handler)
    
    # Мои объявления
    for handler in get_my_items_handlers():
        application.add_handler(handler)
    
    # Избранное
    for handler in get_favorites_handlers():
        application.add_handler(handler)
    
    # Каталог
    for handler in get_catalog_handlers():
        application.add_handler(handler)
    
    # Поиск
    for handler in get_search_handlers():
        application.add_handler(handler)
    
    # FAQ
    for handler in get_faq_handlers():
        application.add_handler(handler)
    
    # Админка
    for handler in get_admin_handlers():
        application.add_handler(handler)
    
    # Обработчик кнопок главного меню (только точные кнопки интерфейса)
    application.add_handler(
        MessageHandler(
            filters.Regex(r"^(?:🛍\s*)?Покупать$|^(?:⭐\s*)?Избранное$|^(?:❓\s*)?FAQ$|^(?:📌\s*)?Мои объявления$"),
            menu_button_handler
        ),
        group=2
    )
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("🤖 Запуск бота...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
