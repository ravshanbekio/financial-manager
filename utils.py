import asyncpg
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def connect():
    return await asyncpg.connect(DATABASE_URL)

async def create_user(chat_id: int, full_name: str = None, username: str = None, phone_number: str = None):
    db = await connect()
    await db.execute(
        "INSERT INTO users (chat_id, full_name, username, phone_number) VALUES($1, $2, $3, $4)",
        chat_id, full_name, username, phone_number
    )
    await db.close()
    
async def get_user(chat_id: int):
    db = await connect()
    try:
        user = await db.fetchrow(
            "SELECT * FROM users WHERE chat_id=$1",
            chat_id
        )
        return user
    finally:
        await db.close()
        
async def update_user(user_id: int, json: dict):
    db = await connect()
    await db.execute(
        "UPDATE users SET balance=$1 WHERE id=$2",
        json['balance'], user_id
    )
    await db.close()
        
async def create_debt(user_id: int, json: dict):
    db = await connect()
    await db.execute(
        "INSERT INTO debts (user_id, description, amount, return_date) VALUES($1, $2, $3, $4)",
        user_id, json['clean_text'], json['amount_in_som'], datetime.strptime(json['return_date'], "%Y-%m-%d").date() if json['return_date'] != '' else None
    )
    await db.close()
    
async def create_expense(user_id: int, json: dict):
    db = await connect()
    await db.execute(
        "INSERT INTO expenses (user_id, description, amount, category) VALUES($1, $2, $3, $4)",
        user_id, json['clean_text'], json['amount_in_som'], json['category'] 
    )
    await db.close()
    
async def create_income(user_id: int, json: dict):
    db = await connect()
    await db.execute(
        "INSERT INTO incomes (user_id, description, category, amount) VALUES($1, $2, $3, $4)",
        user_id, json['clean_text'], json['category'], json['amount_in_som']
    )
    await db.close()
        
async def add_data(chat_id: int, data: list):
    user = await get_user(chat_id=chat_id)
    updated_balance = user['balance']   # start with current balance
    exceeded_amount = 0

    for json in data:
        if json['category'] == "debt":
            await create_debt(user_id=user['id'], json=json)
            updated_balance -= json['amount_in_som']
            await update_user(user_id=user['id'], json={"balance": updated_balance})

        elif json['category'] in ["expense", "loan", "investment"]:
            await create_expense(user_id=user['id'], json=json)
            updated_balance -= json['amount_in_som']
            await update_user(user_id=user['id'], json={"balance": updated_balance})
            if updated_balance < user['limited_balance']:
                exceeded_amount += json['amount_in_som']

        elif json['category'] == "income":
            await create_income(user_id=user['id'], json=json)
            updated_balance += json['amount_in_som']
            await update_user(user_id=user['id'], json={"balance": updated_balance})

        else:
            pass

    return {
        "response": "warning" if updated_balance < user['limited_balance'] else "ok",
        "excess_amount": updated_balance - user['limited_balance'],
        "limit": user['limit']
}
        
async def update_limit(chat_id: int, limit: int):
    user = await get_user(chat_id=chat_id)
    db = await connect()
    await db.execute(
        'UPDATE users SET "limit"=$1, "limited_balance"=$2 WHERE id=$3',
        limit, user['balance'] - limit, user['id']
    )
    await db.close()