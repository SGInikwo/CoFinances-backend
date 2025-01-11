from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Union, List, Dict
from models.send.transactions import TransactionResponse
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha, TransactionsRequest_ing, TransactionsRequest_revolut, TransactionsRequest_shinha
import httpx
from database.deps import createSessionClient, DATABASE_ID, TRANSACTION_COLLECTION_ID, ENDPOINT, PROJECT_ID, USER_COLLECTION_ID
from database.transaction_dao import TransactionDao
from fastapi.security import HTTPBearer
from appwrite.services.databases import Databases

router = APIRouter(
  prefix="/transactions",
  tags=["transaction"]
)

security = HTTPBearer()

async def validate_jwt(authorization: str = Depends(security)):
  token = authorization.credentials  # Extract the token from the Authorization header

  db = createSessionClient().set_jwt(token)

  databases = Databases(db)

  documents = databases.list_documents(
    database_id=DATABASE_ID,
    collection_id=USER_COLLECTION_ID
  )

  userId = documents["documents"][0]["userId"]
  currency = documents["documents"][0]["currency"]
  return [userId, currency]

@router.post("/", status_code=200)
async def forecast(requests: Union[TransactionsRequest_ing, TransactionsRequest_revolut, TransactionsRequest_shinha], user: list = Depends(validate_jwt)):
  TransactionDao().save(data=requests, user_data=user)
  return "OK"

@router.get("/list-{month}-{year}")
async def forecast(month, year, user: list = Depends(validate_jwt)):
  response = TransactionDao().get_transactions(user_data=user, month=month, year=year)
  return response

@router.get("/analysis-current-{month}-{year}")
async def forecast(month, year, user: list = Depends(validate_jwt)):
  response = TransactionDao().current_month_expenses(user_data=user, month=month, year=year)
  return response

@router.get("/analysis-past-{month}-{year}")
async def forecast(month, year, user: list = Depends(validate_jwt)):
  response = TransactionDao().past_month_expenses(user_data=user, month=month, year=year)
  return response

@router.post("/update_balances-{clientCurrency}", status_code=200)
async def forecast(clientCurrency, user: list = Depends(validate_jwt)):
  TransactionDao().update_currency(cleintCurrency=int(clientCurrency), user_data=user)
  return "OK"

@router.get("/current-expenses-{month}-{year}")
async def forecast(month, year, user: list = Depends(validate_jwt)):
  response = TransactionDao().get_transactions(user_data=user, month=month, year=year)
  return response


