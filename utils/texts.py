async def specifyTransactionText(type, date, amount, currency, description):
    text = ""
    if type == "income":
        text = f"""
*✅ Kirimlarga qo'shildi!*

*Sana:* {date}
*Summa:* {amount:,} {currency}
*Izoh:* {description}
        """.replace(",", " ")
    elif type == "expense":
        text = f"""
*✅ Chiqimlar ro'yxatiga qo'shildi!*

*Sana:* {date}
*Summa:* {amount:,} {currency}
*Izoh:* {description}
        """.replace(",", " ")
    elif type == "investment":
        text = f"""
*✅ Investitsiyalar ro'yxatiga qo'shildi!*

*Sana:* {date}
*Summa:* {amount:,} {currency}
*Izoh:* {description}
        """.replace(",", " ")
        
    return text

async def specifyDebtText(type, date, amount, currency, description, return_date = None):
    if type == "borrowed":
        text = f"""
*✅ Olingan qarzlar ro'yxatiga qo'shildi!*

*Sana:* {date if date is not None else "yozilmadi"}
*Summa:* {amount:,} {currency}
*Izoh:* {description}
*Qaytarish sanasi:* {return_date if return_date is not None else "yozilmadi"}
        """.replace(",", " ")
    elif type == "lent":
        text = f"""
*✅ Berilgan qarzlar ro'yxatiga qo'shildi!*

*Sana:* {date if date is not None else "yozilmadi"}
*Summa:* {amount:,} {currency}
*Izoh:* {description}
*Qaytarish sanasi:* {return_date if return_date is not None else "yozilmadi"}
        """.replace(",", " ")
        
    return text

async def WarningText(amount: int):
    text = f"⚠️ Sizda {amount:,} so'mdan kam mablag' qoldi. Chiqimlarni kamaytirishni tavsiya qilamiz".replace(","," ")
    return text