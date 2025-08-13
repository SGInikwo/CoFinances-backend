from fastapi import APIRouter, Depends
from typing import Union
from models.send.transactions import TransactionResponse
from models.receive.transactions import TransactionsRequest_ing, TransactionsRequest_kb, TransactionsRequest_revolut, TransactionsRequest_shinha, TransactionsUpdateRequest
from database.deps import createAdminClient, createSessionClient, DATABASE_ID, TRANSACTION_COLLECTION_ID, ENDPOINT, PROJECT_ID, USER_COLLECTION_ID
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
async def forecast(requests: Union[TransactionsRequest_ing, TransactionsRequest_revolut, TransactionsRequest_shinha, TransactionsRequest_kb], user: list = Depends(validate_jwt)):
  TransactionDao(user[2]).save(data=requests, user_data=user)
  return "OK"

@router.get("/list-all")
async def forecast(user: list = Depends(validate_jwt)):
  response = TransactionDao(user[2]).get_all_transactions()
  return response

@router.get("/list-{month}-{year}")
async def forecast(month, year, user: list = Depends(validate_jwt)):
  response = TransactionDao(user[2]).get_transactions(user_data=user, month=month, year=year)
  return response

@router.get("/analysis-current-{month}-{year}")
async def forecast(month, year, user: list = Depends(validate_jwt)):
  response = TransactionDao(user[2]).current_month_expenses(user_data=user, month=month, year=year)
  return response

@router.get("/analysis-past-{month}-{year}")
async def forecast(month, year, user: list = Depends(validate_jwt)):
  response = TransactionDao(user[2]).past_month_expenses(user_data=user, month=month, year=year)
  return response

@router.post("/update_balances-{clientCurrency}", status_code=200)
async def forecast(clientCurrency, user: list = Depends(validate_jwt)):
  TransactionDao(user[2]).update_currency(cleintCurrency=int(clientCurrency), user_data=user)
  return "OK"

@router.get("/current-expenses-{month}-{year}")
async def forecast(month, year, user: list = Depends(validate_jwt)):
  response = TransactionDao(user[2]).get_transactions(user_data=user, month=month, year=year)
  return response

@router.post("/update_category", status_code=200)
async def forecast(requests: TransactionsUpdateRequest, user: list = Depends(validate_jwt)):
  TransactionDao(user[2]).update(data=requests, user_data=user)
  return "OK"


