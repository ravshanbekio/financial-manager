from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from utils.utils import update_limit, get_user
from buttons import BUTTONS_LIST, button

class LimitState(StatesGroup):
    ask_limit_amount = State()

limit_router = Router()

@limit_router.callback_query(F.data == "set_limit")
async def limit_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user = await get_user(chat_id=callback.message.chat.id)
    text = f"""*🔔 Xarajatlar limiti o‘rnatish!*

Limit — oylik xarajatlaringiz uchun chegara.  
Agar xarajatlaringiz ushbu limitdan oshib ketsa, bot sizni ogohlantiradi ⚠️ 


Masalan: agar siz 2 000 000 so‘m limit qo‘ysangiz,  
xarajatlaringiz shu summadan oshganda xabar olasiz.  

*Sizning hozirgi limitingiz:* {user['limit']:,} so'm
👇 Quyidagi tugmalardan birini tanlang yoki limit miqdorini qo'lda kiriting (so‘mda): 2 000 000
""".replace(",", " ")
    builder = InlineKeyboardBuilder()
    for i in range(1, 11):
        builder.button(
            text=f"{i} million so'm",
            callback_data=f"{i*1000000}"
        )
    builder.adjust(2)
    await state.set_state(LimitState.ask_limit_amount)
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())
    await callback.answer()
    
@limit_router.message(LimitState.ask_limit_amount, F.text.not_in(BUTTONS_LIST))
async def catch_limit(message: Message, state: FSMContext):
    main_button = await button(message.chat.id)
    sliced_message = message.text.replace(" ","")
    if sliced_message.isdigit():
        await update_limit(chat_id=message.chat.id, limit=int(sliced_message))
        text = """
        *✅ Limit o'rnatildi!* 
        """ 
        await message.answer(text, parse_mode="Markdown", reply_markup=main_button)
        await state.set_state(None)
    else:
        await message.answer("❌ Faqat son yuborishingiz kerak! Misol uchun: 1 000 000")
        
@limit_router.callback_query(F.data, F.data!="set_limit", F.data.not_contains("change_data_"))
async def handle_callback_limit(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    main_button = await button(callback.message.chat.id)
    limit = int(callback.data)
    await update_limit(chat_id=callback.message.chat.id, limit=limit)
    text = """
*✅ Limit o'rnatildi!* 
    """
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=main_button)
    await callback.answer()
    await state.set_state(None)