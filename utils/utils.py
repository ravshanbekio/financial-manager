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
    debt_id = await db.fetchval(
        "INSERT INTO debts (user_id, description, amount, return_date, type) VALUES($1, $2, $3, $4, $5)",
        user_id, json.get('description'), json.get('amount_in_som'), datetime.strptime(json.get('return_date'), "%Y-%m-%d").date() if json.get('return_date') != '' else None, json.get("type")
    )
    await db.close()
    return debt_id
    
async def create_transaction(user_id: int, json: dict):
    db = await connect()
    transaction_id = await db.execute(
        "INSERT INTO transactions (user_id, description, amount, type, created_at, date, created_at) VALUES($1, $2, $3, $4, $5, $6, $7)",
        user_id, json.get('description'), json.get('amount_in_som'), json.get('type'), json.get("category"), json.get("date"), datetime.today().date()
    )
    await db.close()
    return transaction_id
    
async def add_data(chat_id: int, data: list):
    user = await get_user(chat_id=chat_id)
    updated_balance = user['balance']
    exceeded_amount = 0
    added_ids = []

    for json in data:
        if json.get("type") in ["borrowed", "lent"]:
            debt_id = await create_debt(user_id=user['id'], json=json)
            added_ids.append(debt_id)
            
            if json.get("type") == "borrowed":
                updated_balance += json.get("amount_in_som")
            elif json.get("type") == "lent":
                updated_balance -= json.get("amount_in_som")
                
            await update_user(user_id=user['id'], json={"balance": updated_balance})
            
        elif json.get("type") in ["income", "expense", "investment"]:
            transaction_id = await create_transaction(user_id=user['id'], json=json)
            added_ids.append(transaction_id)
            
            if json.get("type") == "income":
                updated_balance += json.get("amount_in_som")
            elif json.get("type") in ["expense", "investment"]:
                updated_balance -= json['amount_in_som']
                
            await update_user(user_id=user['id'], json={"balance": updated_balance})
            if updated_balance < user['limited_balance']:
                exceeded_amount += json['amount_in_som']
        else:
            pass

    return {
        "response": "warning" if updated_balance < user['limited_balance'] else "ok",
        "excess_amount": updated_balance - user['limited_balance'],
        "limit": user['limit'],
        "ids": added_ids
}
        
async def update_limit(chat_id: int, limit: int):
    user = await get_user(chat_id=chat_id)
    db = await connect()
    await db.execute(
        'UPDATE users SET "limit"=$1, "limited_balance"=$2 WHERE id=$3',
        limit, user['balance'] - limit, user['id']
    )
    await db.close()