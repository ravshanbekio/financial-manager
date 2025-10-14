import aiohttp
from datetime import datetime

CBU_API_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"


async def get_exchange_rates():
    async with aiohttp.ClientSession() as session:
        async with session.get(CBU_API_URL) as response:
            data = await response.json()
            
            usd = next(item for item in data if item["Ccy"] == "USD")["Rate"]
            rub = next(item for item in data if item["Ccy"] == "RUB")["Rate"]
            
            return {
                "usd": float(usd),
                "rub": float(rub),
                "date": datetime.today().date().isoformat()
            }