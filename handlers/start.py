from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from utils import create_user, get_user, add_data
from buttons import button

class IncomeState(StatesGroup):
    income_state = State()

start_router = Router()

@start_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """Start command"""
    user = await get_user(chat_id=message.chat.id)
    start_text = "✅ Boshlash uchun o'zingizdagi *budjet* miqdorini kiriting (so'mda): 1 000 000" if not user else ""
    if not user:
        await create_user(chat_id=message.chat.id, full_name=f"{message.chat.first_name} {message.chat.last_name}", 
                      username=message.chat.username)
        await state.set_state(IncomeState.income_state)
        
    text = f"""*Assalomu alaykum!* 👋  
Men — sizning shaxsiy *moliyaviy boshqaruv yordamchingiz*man.   

📊 Bu yerda siz:  
- Oylik daromad va xarajatlaringizni yozib borishingiz mumkin
- Harajatlaringizni toifalar bo‘yicha kuzatishingiz mumkin
- Qaysi yo‘nalishda ko‘proq mablag‘ ketayotganini bilib olasiz
- Moliyaviy rejalaringizni nazorat qilib, tejash imkoniyatini oshirasiz 💰  

{start_text}"""
    main_button = await button(chat_id=message.chat.id) if user else None
    await message.answer(text, parse_mode="Markdown", reply_markup=main_button)
    
    
@start_router.message(IncomeState.income_state)
async def handle_budget(message: Message, state: FSMContext):
    """Writing initial income"""
    sliced_message = message.text.replace(" ","")
    if sliced_message.isdigit():
        data = [
            {
                "category":"income",
                "amount":int(sliced_message),
                "amount_in_som":int(sliced_message),
                "clean_text":"budget"
            }
        ]
        await add_data(chat_id=message.chat.id, data=data)
        main_button = await button(chat_id=message.chat.id)
        await message.answer("✅ Tayyor. Endi botdan to'liq foydalanishingiz mumkin", reply_markup=main_button)
        await state.set_state(None)
        
    else:
        await message.answer("❌ Faqat son yuborishingiz kerak! Misol uchun (so'mda): 1 000 000")