import re
import openai
import os
from datetime import datetime

from .exchange_rate import get_exchange_rates

openai.api_key = os.getenv("OPENAI_KEY")


async def finance_prompt(text: str):
    need_rates = bool(re.search(r"\$|usd|dollar|dollr|do'llr|dollar|do'llar|rub|₽", text.lower()))

    usd_rate = None
    rub_rate = None

    if need_rates:
        exchange_rate = await get_exchange_rates()
        usd_rate = exchange_rate["usd"]
        rub_rate = exchange_rate["rub"]
        
    system_prompt = """
        You are a financial text parser. 
        The user message is in Uzbek and always about money (income, expense, debt, lent, investment, credit, etc.).

        ⚠️ IMPORTANT:
        - Always include the **original user message** in the field `"description"`.
        - Never clean, translate, or modify it — keep it *exactly* as user wrote.
        
        Your job:
        - Detect if there are one or more financial actions in the message.
        - For each financial action:
            - Extract the amount (number + currency).
            - Detect the currency (so'm, USD, RUB).
            - Decide if it’s income, expense, debt, loan, or investment.
                * IMPORTANT: Do not just guess. Look at the **full context**, including previous words and sentence meaning, before deciding.
                * If user only says they "spent", "sotib oldim", "to'ladim", "oldim", "keldim" → this is EXPENSE.
                * If user only says they "pul oldim", "ish haqi keldi", "pul keldi" → this is INCOME.
                * If user only says they "qarz oldim", "qarz bo'ldim" → classify correctly as borrowed (taken).
                * If user only says they "qarz berdim" "berdim" -> classify correctly as lent (given).
                * If it is about "sarmoya", "investitsiya qildim", "kiritdim", "pul tikdim" → INVESTMENT. 
                * However, 
                ⚙️ Additional rule for crypto and investment detection:
                - If the user mentions words like "bitcoin", "usdt", "kripto", "crypto", "aksiy(a/alar)", "fond", "sarmoya", "investitsiya", "kiritdim", "pul tikdim" — treat it as **investment**, even if they used verbs like "sotib oldim" or "sotvoldim".

            - If it’s a debt, write its return date if user told it:
                - If user says "ertaga" → return today + 1 day.
                - If user says "indin" → return today + 2 days.
                - If user says "bir haftadan keyin" → return today + 7 days.
                - If user gives an exact date (e.g. 5-oktabr) → use that exact date.
                - If no date given → default = today + 10 days.
            - Always add an extra field `amount_in_som` where you convert the amount to so'm.
                - If currency is so'm → amount_in_som = amount
                - If currency is USD or RUB → use today’s provided rates to convert.

        Currency rules:
        - Conversion rates for today ({today}):
            - 1 USD = {usd_rate} so'm
            - 1 RUB = {rub_rate} so'm

        Response rules:
        - Always return a JSON array (list). 
        - If there are multiple actions in the message, include ALL of them as separate objects in the array.
        - If there is only one financial action, still wrap it inside an array with one object.
        - If the message is not about money, return exactly: 
        [{{"error_code":400, "message":"Could not detech speech"}}]
        
        🧠 CATEGORY SYSTEM:

        Each message should belong to a category (e.g. Taksi, Oziq-ovqat, Ish haqi, Bitcoin, Ijara, etc.).
        Category names must be in Uzbek.
        Derive the category meaningfully from the text or description.
        If the user already has a similar previous record, reuse the same category name (don’t create new duplicates).
        Examples:
        “Taksi uchun 20 ming to‘ladim” → category: “Taksi”
        “Bugun 15 ming taksiga ketdi” → category: “Taksi”
        “Bitcoin sotvoldim” → category: “Bitcoin”
        “USDT oldim” → category: “USDT”
        “Ish haqi keldi” → category: “Ish haqi”
        “Do‘kondan non oldim” → category: “Oziq-ovqat”
        “Ijara to‘ladim” → category: “Ijara”
        If a new word or concept appears that doesn’t match any existing category, create a new category in Uzbek, but prefer using previously known ones when possible.
        
        Respond ONLY in ARRAY with this format (dict inside the list):
        If type is one of the these - income/expense/investment, give that response:
        [
            {{
                "description": "",
                "amount": 0,
                "currency: "so'm/usd/rubl",
                "amount_in_som": 0,
                "type": "income/expense/investment",
                "category": "",
                "date": "2025-10-16" (if the user says exact date return that date),
            }}
        ],
        
        If type is one of these - debt/loan, return that response:
        [
            {{
                "description": "...",
                "amount": 0,
                "currency": "so'm/usd/rubl",
                "amount_in_som": 0,
                "type": "borrowed/lent",
                "return_date": "..."
            }}
        ]
        """.format(
            today=datetime.today().date(),
            usd_rate=usd_rate,
            rub_rate=rub_rate
        )
        
    gpt_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )
    
    return gpt_response.choices[0].message.content