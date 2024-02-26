from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import DB_NAME
from utils.database import Database


db = Database(DB_NAME)


# Function for make inline keyboards from category names
def get_category_list() -> InlineKeyboardMarkup:
    categories = db.get_categories()
    rows = []
    for category in categories:
        rows.append([
            InlineKeyboardButton(
                text=category[1],
                callback_data=str(category[0])
            )
        ])
    kb_categories = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_categories


# Function for make inline keyboards from product names
def get_product_list(cat_id: int) -> InlineKeyboardMarkup:
    products = db.get_products(cat_id)
    rows = []
    for product in products:
        rows.append([
            InlineKeyboardButton(
                text=product[1],
                callback_data=str(product[0])
            )
        ])
    kb_products = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_products


left_right_k = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️",callback_data="left"),
     InlineKeyboardButton(text="➡️",callback_data="right")]
])

ads_10 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1",callback_data="1"),
     InlineKeyboardButton(text="2",callback_data="2"),
     InlineKeyboardButton(text="3",callback_data="3"),
     InlineKeyboardButton(text="4",callback_data="4"),
     InlineKeyboardButton(text="5",callback_data="5"),
     ],
     [
     InlineKeyboardButton(text="6",callback_data="6"),
     InlineKeyboardButton(text="7",callback_data="7"),
     InlineKeyboardButton(text="8",callback_data="8"),
     InlineKeyboardButton(text="9",callback_data="9"),
     InlineKeyboardButton(text="10",callback_data="10")
     ]
])

