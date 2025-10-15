import aiohttp
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CBU_API_URL = os.getenv("CBU_API_URL")


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