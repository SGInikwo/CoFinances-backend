from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Union, List, Dict
from models.send.transactions import TransactionResponse
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import httpx
from database.deps import createSessionClient, DATABASE_ID, TRANSACTION_COLLECTION_ID, ENDPOINT, PROJECT_ID, USER_COLLECTION_ID
from database.dao import TransactionDao
from fastapi.security import HTTPBearer
from appwrite.services.databases import Databases

router = APIRouter(
  prefix="/transactions",
  tags=["transaction"]
)

security = HTTPBearer()

async def validate_jwt(authorization: str = Depends(security)):
  token = authorization.credentials  # Extract the token from the Authorization header
  print(token)
  db = createSessionClient().set_jwt(token)

  databases = Databases(db)

  documents = databases.list_documents(
    database_id=DATABASE_ID,
    collection_id=USER_COLLECTION_ID
  )

  # print(documents)
  # print(documents["documents"][0]["userId"])

  userId = documents["documents"][0]["userId"]
  currency = documents["documents"][0]["currency"]
  return [userId, currency]

@router.post("/")
async def forecast(requests: Union[List[Transactions_ing], List[Transactions_revolut], List[Transactions_shinha]], user: list = Depends(validate_jwt)):

  # print(dict(requests[0]))
  
  data = TransactionDao().save(data=requests, user_data=user)


