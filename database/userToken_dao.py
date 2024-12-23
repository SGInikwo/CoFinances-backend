from database.deps import createAdminClient, DATABASE_ID, USERTOKEN_COLLECTION_ID
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import secrets

from models.send.userToken import get_insert_data

client = createAdminClient()
db = Databases(client)

class UserToken:
  def __init__(self):
    self.db_id = DATABASE_ID
    self.collection_id = USERTOKEN_COLLECTION_ID


  def get_jwts(self):
    result = db.list_documents(
      database_id = self.db_id,
      collection_id = self.collection_id
    )

    for rsul in result["documents"]:
      rsul.pop("userId", None)
      rsul.pop('$permissions', None)

    # print(result['documents'])
    return result['documents']
  
  def get_jwt(self, user_data):
    result = db.get_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id=user_data
        )
    
    # print(result)
    return result["jwt"]
  
  def save(self, user_data):
    data = get_insert_data(user_data=user_data)

    # print(data)
    result = db.create_document(
          database_id= self.db_id,
          collection_id= self.collection_id,
          document_id=user_data[0],
          data=data,
        )
    return result
  
  def delete(self, user_data):
    result = db.delete_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= user_data[0],
        )

    return result
  
  def update(self, user_data):
    data = get_insert_data(user_data=user_data)
    result = db.update_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= user_data[0],
            data=data
        )

    return result