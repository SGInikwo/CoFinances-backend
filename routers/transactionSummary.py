from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Union, List, Dict
from models.send.transactions import TransactionResponse
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import httpx
from database.deps import createSessionClient, DATABASE_ID, TRANSACTION_COLLECTION_ID, ENDPOINT, PROJECT_ID, USER_COLLECTION_ID
from database.transactionSummary_dao import SummaryDao
from fastapi.security import HTTPBearer
from appwrite.services.databases import Databases

router = APIRouter(
  prefix="/summary",
  tags=["summary"]
)

security = HTTPBearer()

async def validate_jwt(authorization: str = Depends(security)):
  token = authorization.credentials  # Extract the token from the Authorization header
  # print(token)
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
async def forecast(user: list = Depends(validate_jwt)):
  
  SummaryDao().push_data(user_data=user)

  return "OK"

@router.get("/list", status_code=200)
async def forecast(user: list = Depends(validate_jwt)):
  
  all_summaries = SummaryDao().get_summary()

  return all_summaries


@router.get("/summary-{month}-{year}", status_code=200)
async def forecast(month, year, user: list = Depends(validate_jwt)):
  try:
    summary = SummaryDao().get_custom_summary(month, year)
  except:
    summary = None

  return summary

@router.get("/months", status_code=200)
async def forecast(user: list = Depends(validate_jwt)):
  
  try:
    months = SummaryDao().get_months(user)
  except:
    months = None

  return months
