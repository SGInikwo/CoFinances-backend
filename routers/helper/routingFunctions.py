from fastapi import Depends
from database.deps import createAdminClient, createSessionClient, DATABASE_ID, USER_COLLECTION_ID
from fastapi.security import HTTPBearer
from appwrite.services.databases import Databases

security = HTTPBearer()

async def validate_jwt(authorization: str = Depends(security)):
  token = authorization.credentials  # Extract the token from the Authorization header

  adminClient = createAdminClient()
  userClient = createSessionClient().set_jwt(token)

  userDB = Databases(userClient)
  adminDB = Databases(adminClient)

  documents = userDB.list_documents(
    database_id=DATABASE_ID,
    collection_id=USER_COLLECTION_ID
  )

  userId = documents["documents"][0]["userId"]
  currency = documents["documents"][0]["currency"]
  return {
    "userId": userId,
    "currency": currency,
    "userDB": userDB,
    "adminDB": adminDB
}