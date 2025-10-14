async def specify_text(category, date, amount, currency, description, return_date = None):
    text = ""
    if category == "income":
        text = f"""
*✅ Hisobotga qo'shildi!*

*Kirim:*
*Sana:* {date}
*Summa:* {amount:,} {currency}
*Izoh:* {description}
        """.replace(",", " ")
    if category in ["expense", "loan", "investment"]:
        text = f"""
*✅ Chiqimlar ro'yxatiga qo'shildi!*

*Chiqim:*
*Sana:* {date}
*Summa:* {amount:,} {currency}
*Izoh:* {description}
        """.replace(",", " ")
    if category == "debt":
        text = f"""
*✅ Qarzlar ro'yxatiga qo'shildi!*

*Qarz:*
*Sana:* {date}
*Summa:* {amount:,} {currency}
*Izoh:* {description}
*Qaytarish sanasi:* {return_date if return_date is not None else ""}
        """.replace(",", " ")
    return text