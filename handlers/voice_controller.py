# from datetime import datetime
# from aiogram import Router, F
# from aiogram.types import Message
# from dotenv import load_dotenv
# import openai
# import json
# import requests
# import os
# import re
# import ast

# from buttons import button
# from texts import specify_text
# from utils.utils import add_data
# from utils.exchange_rate import get_exchange_rates
# from stt import convert_to_text

# load_dotenv()

# voice_controller_router = Router()
# openai.api_key = os.getenv("OPENAI_KEY")
# BOT_TOKEN = os.getenv("BOT_TOKEN")

# @voice_controller_router.message(F.voice)
# async def voice_controller(message: Message):
#     main_button = await button(message.chat.id)
#     msg = await message.answer("✅ Bajarilmoqda...")
    
#     # 1. Get voice file info from Telegram
#     file_info = await message.bot.get_file(message.voice.file_id)
#     file_path = file_info.file_path
#     voice_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

#     # 2. Download the audio file
#     response = requests.get(voice_url)
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     ogg_file = f"voice_{timestamp}.ogg"
#     with open(ogg_file, "wb") as f:
#         f.write(response.content)
        
#     text_result = await convert_to_text(ogg_file)
    
#     await msg.edit_text(text="⏳ Tayyorlanmoqda...")

#     need_rates = bool(re.search(r"\$|usd|dollar|dollr|do'llr|dollar|do'llar|rub|₽", text_result['transcript'].lower()))

#     usd_rate = None
#     rub_rate = None

#     if need_rates:
#         exchange_rate = await get_exchange_rates()
#         usd_rate = exchange_rate["usd"]
#         rub_rate = exchange_rate["rub"]
        
#     system_prompt = """
#     You are a financial text parser. 

#     Your job:
#     - Detect if there are one or more financial actions in the message.
#     - For each financial action:
#         - Extract the cleaned text.
#         - Extract the amount (number + currency).
#         - Detect the currency (so'm, USD, RUB).
#         - Decide if it’s income, expense, debt, loan, or investment.
#             * IMPORTANT: Do not just guess. Look at the **full context**, including previous words and sentence meaning, before deciding.
#             * If user says they "spent", "sotib oldim", "to'ladim", "oldim" → this is EXPENSE.
#             * If user says they "pul oldim", "ish haqi keldi", "pul keldi" → this is INCOME.
#             * If user says they "qarz oldim" or "qarz berdim" → classify correctly as LOAN (given) or DEBT (taken).
#             * If it is about "sarmoya", "investitsiya qildim", "kiritdim", "pul tikdim" → INVESTMENT.
#         - If it’s a debt, write its return date if user told it:
#             - If user says "ertaga" → return today + 1 day.
#             - If user says "indin" → return today + 2 days.
#             - If user says "bir haftadan keyin" → return today + 7 days.
#             - If user gives an exact date (e.g. 5-oktabr) → use that exact date.
#             - If no date given → default = today + 10 days.
#         - Always add an extra field `amount_in_som` where you convert the amount to so'm.
#             - If currency is so'm → amount_in_som = amount
#             - If currency is USD or RUB → use today’s provided rates to convert.

#     Currency rules:
#     - Conversion rates for today ({today}):
#         - 1 USD = {usd_rate} so'm
#         - 1 RUB = {rub_rate} so'm

#     Response rules:
#     - Always return a JSON array (list). 
#     - If there are multiple actions in the message, include ALL of them as separate objects in the array.
#     - If there is only one financial action, still wrap it inside an array with one object.
#     - If the message is not about money, return exactly:
#     [{{"clean_text":"Iltimos, qayta yuboring."}}]

#     Respond ONLY in ARRAY with this format:
#     [
#         {{
#             "clean_text": "",
#             "amount": 0,
#             "currency": "so'm/usd/rubl",
#             "amount_in_som": 0,
#             "category": "income/expense/debt/loan/investment",
#             "return_date": "..."
#         }}
#     ]
#     """.format(
#             today=datetime.today().date(),
#             usd_rate=usd_rate,
#             rub_rate=rub_rate
#         )
        
#     gpt_response = openai.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": text_result['transcript']}
#         ]
#     )
#     try:
#         structured = json.loads(gpt_response.choices[0].message.content)
#     except json.JSONDecodeError:
#         structured = ast.literal_eval(gpt_response.choices[0].message.content)
#     for i in structured:
#         if i['clean_text']=="Iltimos, qayta yuboring." or i['amount'] == 0:
#             await msg.delete()
#             return message.answer("Kontekstni aniqlab bo'lmadi. Iltimos, to'g'rilab qayta yuboring")
#         else:
#             pass
#     data = await add_data(chat_id=message.chat.id, data=structured)
#     if data.get('response') == "warning":
#         warning_text = f"""
#         *⚠️ Sizning xarajatlaringiz limitdan oshib ketdi!*
        
# Ortiqcha summa: {data['excess_amount']:,} so'm
# Limit: {data['limit']:,} so'm
#         """.replace(",", " ")
#         await message.answer(warning_text, parse_mode="Markdown")
        
#     if isinstance(structured, dict):
#         structured = [structured]
    
#     await msg.delete()
#     for object in structured:
#         text = await specify_text(category=object['category'], 
#                             date=datetime.today().date(), 
#                             amount=object['amount'], 
#                             currency=object['currency'],
#                             description=object['clean_text'], 
#                             return_date=object['return_date'])
#         await message.answer(text, parse_mode="Markdown", reply_markup=main_button)