from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Union, List, Dict
from models.send.transactions import TransactionResponse
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import httpx
from database.deps import createSessionClient, DATABASE_ID, TRANSACTION_COLLECTION_ID, ENDPOINT, PROJECT_ID, USER_COLLECTION_ID
from database.budgetSummary_dao import BudgetSummaryDao
from fastapi.security import HTTPBearer
from appwrite.services.databases import Databases

router = APIRouter(
  prefix="/budgetSummary",
  tags=["budgetSummary"]
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
  return [userId, currency, databases]


@router.post("/", status_code=200)
async def forecast(user: list = Depends(validate_jwt)):
  
  BudgetSummaryDao(user[2]).push_data(user_data=user)

  return "OK"

@router.get("/list", status_code=200)
async def forecast(user: list = Depends(validate_jwt)):
  
  all_summaries = BudgetSummaryDao(user[2]).get_summary()

  return all_summaries

@router.post("/update_balances-{clientCurrency}", status_code=200)
async def forecast(clientCurrency, user: list = Depends(validate_jwt)):
  BudgetSummaryDao(user[2]).update_currency(cleintCurrency=int(clientCurrency), user_data=user)
  return "OK"