from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

BUTTONS_LIST = ["set_limit"]

async def button(chat_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📃 Hisobot",
                    web_app=WebAppInfo(url=f"https://finzo-frontend.work.gd/dashboard?chat_id={chat_id}")
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