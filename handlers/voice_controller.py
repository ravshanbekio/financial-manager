from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv
import json
import requests
import os

from buttons import button
from texts import specifyDebtText, specifyTransactionText
from utils.gpt_agent import finance_prompt
from utils.utils import add_data
from stt import convert_to_text

load_dotenv()

voice_controller_router = Router()
BOT_TOKEN = os.getenv("BOT_TOKEN")
FRONTEND_URL = os.getenv("FRONTEND_URL")

@voice_controller_router.message(F.voice)
async def voice_controller(message: Message):
    msg = await message.answer("✅ Bajarilmoqda...")
    
    # 1. Get voice file info from Telegram
    file_info = await message.bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    voice_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    # 2. Download the audio file
    response = requests.get(voice_url)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ogg_file = f"voice_{timestamp}.ogg"
    with open(ogg_file, "wb") as f:
        f.write(response.content)
        
    text_result = await convert_to_text(ogg_file)
    await msg.edit_text(text="⏳ Tayyorlanmoqda...")

    structured = json.loads(await finance_prompt(text=text_result)['transcript'])
    if isinstance(structured, dict):
        structured = [structured]
    for item in structured:
        if item.get("error_code") == 400 or item.get('amount') == 0:
            await msg.delete()
            return message.answer("Kontekstni aniqlab bo'lmadi. Iltimos, to'g'rilab qayta yuboring.")
        else: 
            pass
    
    data = await add_data(chat_id=message.chat.id, data=structured)
    if data.get('response') == "warning":
        warning_text = f"""
        *⚠️ Sizning xarajatlaringiz limitdan oshib ketdi!*
        
Ortiqcha summa: {data['excess_amount']:,.2f} so'm
Limit: {data['limit']:,} so'm
        """.replace(",", " ")
        await message.answer(warning_text, parse_mode="Markdown")
    if data.get("warning") is not None:
        await message.answer(data.get("warning"))
        
    main_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                  text="📝 O'zgartirish",
                  web_app=WebAppInfo(url=f"{FRONTEND_URL}/update?chat_id={message.chat.id}")
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