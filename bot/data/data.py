"""
Модуль для работы с данными (товары, FAQ и избранное).
Все данные хранятся в JSON-файлах.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from config import ITEMS_FILE, FAQ_FILE, FAVORITES_FILE, DATA_DIR

logger = logging.getLogger(__name__)


def ensure_data_dir():
    """Убедиться, что директория данных существует."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filepath: Path, default: Any = None) -> Any:
    """Загрузить данные из JSON файла."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # Создаём файл с дефолтными данными
            save_json(filepath, default)
            return default
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка чтения JSON из {filepath}: {e}")
        return default
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении {filepath}: {e}")
        return default


def save_json(filepath: Path, data: Any) -> None:
    """Сохранить данные в JSON файл."""
    ensure_data_dir()
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка записи JSON в {filepath}: {e}")
        raise


# ==================== ТОВАРЫ ====================

def get_default_items() -> Dict[str, Any]:
    """Возвращает структуру товаров по умолчанию."""
    return {
        "items": []
    }


def get_items() -> List[Dict[str, Any]]:
    """Получить список всех товаров."""
    data = load_json(ITEMS_FILE, get_default_items())
    return data.get("items", [])


def get_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    """Получить товар по ID."""
    items = get_items()
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def save_items(items: List[Dict[str, Any]]) -> None:
    """Сохранить список товаров."""
    save_json(ITEMS_FILE, {"items": items})


def add_item(
    title: str,
    description: str,
    price: int,
    city: str,
    condition: str,
    seller_id: int,
    seller_username: str,
    photo_url: Optional[str] = None
) -> Dict[str, Any]:
    """Добавить новый товар."""
    items = get_items()
    # Генерируем новый ID
    new_id = max((item["id"] for item in items), default=0) + 1
    new_item = {
        "id": new_id,
        "title": title,
        "description": description,
        "price": price,
        "city": city,
        "condition": condition,
        "photo_url": photo_url,
        "seller_id": seller_id,
        "seller_username": seller_username,
        "created_at": datetime.now().isoformat(),
        "status": "available"
    }
    items.append(new_item)
    save_items(items)
    return new_item


def delete_item(item_id: int) -> bool:
    """Удалить товар по ID."""
    items = get_items()
    original_len = len(items)
    items = [item for item in items if item["id"] != item_id]
    if len(items) < original_len:
        save_items(items)
        return True
    return False


def search_items(query: str) -> List[Dict[str, Any]]:
    """Поиск товаров по названию и описанию."""
    query_lower = query.lower()
    items = get_items()
    results = []
    for item in items:
        if item["status"] == "available" and (
            query_lower in item["title"].lower() or 
            query_lower in item["description"].lower()
        ):
            results.append(item)
    return results


def get_available_items() -> List[Dict[str, Any]]:
    """Получить все доступные товары (не зарезервированные)."""
    items = get_items()
    return [item for item in items if item["status"] == "available"]


def get_user_items(seller_id: int) -> List[Dict[str, Any]]:
    """Получить все товары продавца."""
    items = get_items()
    return [item for item in items if item.get("seller_id") == seller_id]


# ==================== FAQ ====================

def get_default_faq() -> Dict[str, Any]:
    """Возвращает структуру FAQ по умолчанию."""
    return {
        "questions": [
            {
                "id": "delivery",
                "question": "Доставка",
                "answer": "Доставка осуществляется по всей России через СДЭК, Почту России или курьером.\n\nСтоимость доставки рассчитывается индивидуально.\nСрок доставки: 2-7 дней в зависимости от региона.\n\nВозможна самовывоз."
            },
            {
                "id": "payment",
                "question": "Оплата",
                "answer": "Принимаются следующие способы оплаты:\n\n• Наличные при встрече\n• Перевод на карту (Сбербанк, Тинькофф)\n• Безналичный расчёт (для юрлиц)"
            },
            {
                "id": "return",
                "question": "Возврат",
                "answer": "Возврат товара возможен в течение 14 дней при сохранении товарного вида и упаковки.\n\nТовары надлежащего качества, бывшие в употреблении, возврату не подлежат.\n\nПри обнаружении брака — полный возврат средств или обмен."
            },
            {
                "id": "contacts",
                "question": "Контакты",
                "answer": "Связаться со мной можно через чат в боте или прямо при просмотре объявления."
            },
            {
                "id": "warranty",
                "question": "Гарантия",
                "answer": "На все товары предоставляется гарантия:\n\n• Техника Apple — 1 год\n• Электроника — 6 месяцев\n• Аксессуары — 14 дней\n\nГарантийный случай — бесплатный ремонт или замена."
            }
        ]
    }


def get_faq() -> List[Dict[str, Any]]:
    """Получить список вопросов FAQ."""
    data = load_json(FAQ_FILE, get_default_faq())
    return data.get("questions", [])


def get_faq_answer(faq_id: str) -> Optional[str]:
    """Получить ответ на вопрос по ID."""
    faq_list = get_faq()
    for faq in faq_list:
        if faq["id"] == faq_id:
            return faq["answer"]
    return None


# ==================== ИЗБРАННОЕ ====================

def get_default_favorites() -> Dict[str, Any]:
    """Возвращает структуру избранного по умолчанию."""
    return {"favorites": {}}


def get_favorites() -> Dict[str, Any]:
    """Получить все избранные."""
    return load_json(FAVORITES_FILE, get_default_favorites())


def save_favorites(favorites: Dict[str, Any]) -> None:
    """Сохранить избранные."""
    save_json(FAVORITES_FILE, favorites)


def add_to_favorites(user_id: int, item_id: int) -> bool:
    """Добавить товар в избранное."""
    item = get_item_by_id(item_id)
    if not item:
        return False
    
    favorites_data = get_favorites()
    user_key = str(user_id)
    
    if user_key not in favorites_data["favorites"]:
        favorites_data["favorites"][user_key] = []
    
    if item_id not in favorites_data["favorites"][user_key]:
        favorites_data["favorites"][user_key].append(item_id)
        save_favorites(favorites_data)
        return True
    
    return False


def remove_from_favorites(user_id: int, item_id: int) -> bool:
    """Удалить товар из избранного."""
    favorites_data = get_favorites()
    user_key = str(user_id)
    
    if user_key in favorites_data["favorites"] and item_id in favorites_data["favorites"][user_key]:
        favorites_data["favorites"][user_key].remove(item_id)
        save_favorites(favorites_data)
        return True
    
    return False


def get_user_favorites(user_id: int) -> List[Dict[str, Any]]:
    """Получить избранные товары пользователя."""
    favorites_data = get_favorites()
    user_key = str(user_id)
    
    if user_key not in favorites_data["favorites"]:
        return []
    
    items = get_items()
    favorite_items = []
    for item_id in favorites_data["favorites"][user_key]:
        item = next((it for it in items if it["id"] == item_id), None)
        if item:
            favorite_items.append(item)
    
    return favorite_items


def is_favorite(user_id: int, item_id: int) -> bool:
    """Проверить, находится ли товар в избранном."""
    favorites_data = get_favorites()
    user_key = str(user_id)
    
    if user_key not in favorites_data["favorites"]:
        return False
    
    return item_id in favorites_data["favorites"][user_key]

