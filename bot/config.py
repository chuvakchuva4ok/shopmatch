"""
Конфигурация бота.
Загружает переменные окружения и предоставляет доступ к настройкам.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Основной путь к директории проекта
BASE_DIR = Path(__file__).parent.absolute()

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Поддержка нескольких админов (разделены запятыми)
admin_ids_str = os.getenv("ADMIN_ID", "")
ADMIN_IDS = []
if admin_ids_str:
    try:
        ADMIN_IDS = [int(aid.strip()) for aid in admin_ids_str.split(",") if aid.strip()]
    except ValueError:
        print("Ошибка: ADMIN_ID содержит некорректные значения")

SELLER_CONTACT = os.getenv("SELLER_CONTACT", "@SellerName")

# Пути к файлам данных
DATA_DIR = BASE_DIR / "data"
PHOTO_DIR = DATA_DIR / "photos"  # Тестовые фото для прототипных объявлений можно поместить сюда
ITEMS_FILE = DATA_DIR / "items.json"
FAQ_FILE = DATA_DIR / "faq.json"
FAVORITES_FILE = DATA_DIR / "favorites.json"

# Настройки пагинации каталога
ITEMS_PER_PAGE = 5
