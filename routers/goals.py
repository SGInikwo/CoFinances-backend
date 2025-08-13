from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Union, List, Dict
from models.send.transactions import TransactionResponse
from models.receive.goals import GoalsRequest
import httpx
from database.deps import createAdminClient, createSessionClient, DATABASE_ID, TRANSACTION_COLLECTION_ID, ENDPOINT, PROJECT_ID, USER_COLLECTION_ID
from database.goals_dao import GoalsDao
from fastapi.security import HTTPBearer
from appwrite.services.databases import Databases

router = APIRouter(
  prefix="/goals",
  tags=["goals"]
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
async def forecast(requests: GoalsRequest, user: list = Depends(validate_jwt)):
  GoalsDao(user[2]).save(data=requests, user_data=user)
  return "OK"

@router.get("/", status_code=200)
async def forecast(user: list = Depends(validate_jwt)):
  response = GoalsDao(user[2]).get_goals(user_data=user)
  return response

@router.post("/update_goals-{clientCurrency}", status_code=200)
async def forecast(clientCurrency, user: list = Depends(validate_jwt)):
  GoalsDao(user[2]).update_currency(cleintCurrency=int(clientCurrency), user_data=user)
  return "OK"