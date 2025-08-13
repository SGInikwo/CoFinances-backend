from fastapi import APIRouter, Depends, Request
from typing import List, Union, Dict
from models.receive.category import CategoryRequest
from models.send.transactions import TransactionResponse
from models.receive.transactions import TransactionsRequest_ing, TransactionsRequest_kb, TransactionsRequest_revolut, TransactionsRequest_shinha
from database.deps import createAdminClient, createSessionClient, DATABASE_ID, TRANSACTION_COLLECTION_ID, ENDPOINT, PROJECT_ID, USER_COLLECTION_ID
from database.category_dao import CategoryDao
from fastapi.security import HTTPBearer
from appwrite.services.databases import Databases

router = APIRouter(
  prefix="/category",
  tags=["category"]
)

security = HTTPBearer()

async def validate_jwt(authorization: str = Depends(security)):
  token = authorization.credentials  # Extract the token from the Authorization header

  userClient = createSessionClient().set_jwt(token)
  adminClient = createAdminClient()

  userDB = Databases(userClient)
  adminDB = Databases(adminClient)

  documents = userDB.list_documents(
    database_id=DATABASE_ID,
    collection_id=USER_COLLECTION_ID
  )

  userId = documents["documents"][0]["userId"]
  currency = documents["documents"][0]["currency"]
  return [userId, currency, userDB, adminDB]

@router.post("/", status_code=200)
async def forecast(requests: CategoryRequest, user: list = Depends(validate_jwt)):
  CategoryDao(user[2]).save(data=requests, user_data=user)
  return "OK"

@router.get("/", status_code=200)
async def forecast(user: list = Depends(validate_jwt)):
  CategoryDao(user[2]).get_all_categories()
  return "OK"

@router.get("/category_name", status_code=200)
async def forecast(user: list = Depends(validate_jwt)):
  response = CategoryDao(user[2]).get_all_category_name()
  return response