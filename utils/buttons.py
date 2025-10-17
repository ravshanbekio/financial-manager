import os
from dotenv import load_dotenv
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")


BUTTONS_LIST = ["set_limit"]

async def button(chat_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📃 Hisobot",
                    web_app=WebAppInfo(url=f"{FRONTEND_URL}/dashboard?chat_id={chat_id}")
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚫 Limit o'rnatish",
                    callback_data="set_limit"
                )
            ]
        ]
    )