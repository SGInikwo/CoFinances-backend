from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Union, List, Dict
from models.send.transactions import TransactionResponse
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import httpx
from database.deps import createSessionClient, DATABASE_ID, TRANSACTION_COLLECTION_ID, ENDPOINT, PROJECT_ID, USER_COLLECTION_ID
from database.userToken_dao import UserTokenDao
from fastapi.security import HTTPBearer
from appwrite.services.databases import Databases


router = APIRouter(
  prefix="/usertoken",
  tags=["usertoken"]
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
  # currency = documents["documents"][0]["currency"]
  return [userId, token]

@router.post("/")
async def forecast(user: list = Depends(validate_jwt)):
  
  response = UserTokenDao().save(user_data=user)

  return response

@router.post("/updateauth/")
async def forecast(user: list = Depends(validate_jwt)):
  
  response = UserTokenDao().update(user_data=user)

  return response

@router.delete("/{user_id}")
async def forecast(user_id: str):
  
  response = UserTokenDao().get_jwt(user_data=user_id)

  return response

@router.get("/{user_id}")
async def forecast(user_id: str):
  
  response = UserTokenDao().get_jwt(user_data=user_id)

  return response