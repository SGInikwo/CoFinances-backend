from database.deps import createAdminClient, DATABASE_ID, CURRENCY_COLLECTION_ID
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import secrets
from appwrite.query import Query

from models.send.userToken import get_insert_data

client = createAdminClient()
db = Databases(client)

class Currency:
  def __init__(self):
    self.db_id = DATABASE_ID
    self.collection_id = CURRENCY_COLLECTION_ID

  
  def get_currency(self, user_data):
    currency = {0: "EUR", 1: "KRW", 2:  "KES", 3: "GBP", 4: "USD"}
    base = currency[user_data[0]]
    target = currency[user_data[1]]
    result = db.list_documents(
            database_id= self.db_id,
            collection_id= self.collection_id,
            queries=[
            Query.equal("base", base),  # Add double quotes around base
            Query.equal("target", target),  # Add double quotes around target
        ]
        )
    
    rate = result["documents"][0]["rate"]
    return rate
  
  # def save(self, user_data):
  #   data = get_insert_data(user_data=user_data)

  #   # print(data)
  #   result = db.create_document(
  #         database_id= self.db_id,
  #         collection_id= self.collection_id,
  #         document_id=user_data[0],
  #         data=data,
  #       )
  #   return result
  
  # def delete(self, user_data):
  #   result = db.delete_document(
  #           database_id= self.db_id,
  #           collection_id= self.collection_id,
  #           document_id= user_data[0],
  #       )

  #   return result
  
  # def update(self, user_data):
  #   data = get_insert_data(user_data=user_data)
  #   result = db.update_document(
  #           database_id= self.db_id,
  #           collection_id= self.collection_id,
  #           document_id= user_data[0],
  #           data=data
  #       )

  #   return result