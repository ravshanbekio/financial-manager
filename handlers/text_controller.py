from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import StateFilter
from datetime import datetime
from dotenv import load_dotenv
import openai
import json
import os

from buttons import BUTTONS_LIST
from utils.utils import add_data
from texts import specifyTransactionText, specifyDebtText
from utils.gpt_agent import finance_prompt
from .limit import LimitState

load_dotenv()

text_controller_router = Router()

openai.api_key = os.getenv("OPENAI_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
FRONTEND_URL = os.getenv("FRONTEND_URL")

@text_controller_router.message(F.text.not_in(BUTTONS_LIST), ~StateFilter(LimitState.ask_limit_amount))
async def text_controller(message: Message):
    msg = await message.answer("✅ Bajarilmoqda...")
    structured = json.loads(await finance_prompt(text=message.text))
    if isinstance(structured, dict):
        structured = [structured]
    for item in structured:
        if item.get("error_code") == 400 or item.get('amount') == 0:
            await msg.delete()
            return message.answer("Kontekstni aniqlab bo'lmadi. Iltimos, to'g'rilab qayta yuboring.")
        else: 
            pass
    
    await msg.edit_text("⏳ Tayyorlanmoqda...")
        
    data = await add_data(chat_id=message.chat.id, data=structured)
    if data.get('response') == "warning":
        warning_text = f"""
        *⚠️ Sizning xarajatlaringiz limitdan oshib ketdi!*
        
Ortiqcha summa: {data['excess_amount']:,} so'm
Limit: {data['limit']:,} so'm
        """.replace(",", " ")
        await message.answer(warning_text, parse_mode="Markdown")
        
    main_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                  text="📝 O'zgartirish",
                  callback_data=f"change_data_"
              )  
            ],
            [
                InlineKeyboardButton(
                    text="📃 Hisobot",
                    web_app=WebAppInfo(url=f"{FRONTEND_URL}/dashboard?chat_id={message.chat.id}")
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
    
    await msg.delete()
    for object in structured:
        if object.get("type") in ["borrowed","lent"]:
            text = await specifyDebtText(
                type=object.get("type"),
                date=object.get("date"),
                amount=object.get("amount"),
                currency=object.get("currency"),
                description=object.get("description")
            )
        elif object.get("type") in ["income", "expense","investment"]:
            text = await specifyTransactionText(
                type=object['type'], 
                date=datetime.today().date(), 
                amount=object['amount'], 
                currency=object['currency'],
                description=object['description']
            )
            
        await message.answer(text, parse_mode="Markdown", reply_markup=main_button)
