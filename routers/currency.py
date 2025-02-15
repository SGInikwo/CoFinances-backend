from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Union, List, Dict
from models.send.transactions import TransactionResponse
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import httpx
from database.deps import createSessionClient, DATABASE_ID, TRANSACTION_COLLECTION_ID, ENDPOINT, PROJECT_ID, USER_COLLECTION_ID
from database.currency_dao import CurrencyDao
from fastapi.security import HTTPBearer
from appwrite.services.databases import Databases


router = APIRouter(
  prefix="/currency",
  tags=["currency"]
)

security = HTTPBearer()

async def validate_jwt(authorization: str = Depends(security)):
  token = authorization.credentials
  
  db = createSessionClient().set_jwt(token)

  databases = Databases(db)

  documents = databases.list_documents(
    database_id=DATABASE_ID,
    collection_id=USER_COLLECTION_ID
  )

  userId = documents["documents"][0]["userId"]
  # currency = documents["documents"][0]["currency"]
  return [userId, token]

# @router.post("/")
# async def forecast(user: list = Depends(validate_jwt)):
  
#   response = UserToken().save(user_data=user)

#   return response

@router.get("/{base}-{target}")
async def forecast(base: float, target: float):
  
  response = CurrencyDao().get_currency(user_data=[base, target])

  return response