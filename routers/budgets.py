from fastapi import APIRouter, HTTPException, Depends, Request
from database.deps import createAdminClient, createSessionClient, DATABASE_ID, TRANSACTION_COLLECTION_ID, ENDPOINT, PROJECT_ID, USER_COLLECTION_ID
from database.budget_dao import BudgetDAO
from fastapi.security import HTTPBearer
from appwrite.services.databases import Databases

from models.receive.budget import BudgetRequest

router = APIRouter(
  prefix="/budget",
  tags=["budget"]
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
async def forecast(requests: BudgetRequest, user: list = Depends(validate_jwt)):
  BudgetDAO(user[2]).save(data=requests, user_data=user)
  return "OK"

@router.get("/")
async def forecast(user: list = Depends(validate_jwt)):
  response = BudgetDAO(user[2]).get_all_budgets()
  return response

@router.post("/update_balances-{clientCurrency}", status_code=200)
async def forecast(clientCurrency, user: list = Depends(validate_jwt)):
  BudgetDAO(user[2]).update_currency(cleintCurrency=int(clientCurrency), user_data=user)
  return "OK"