from database.deps import createAdminClient, DATABASE_ID, TRANSACTION_COLLECTION_ID
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.query import Query
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import secrets
from datetime import datetime

from models.send.transactions import get_insert_data

client = createAdminClient()
db = Databases(client)

class TransactionDao:
  def __init__(self):
    self.db_id = DATABASE_ID
    self.collection_id = TRANSACTION_COLLECTION_ID


  def get_transactions(self, user_data, month=None, year=None):
    results = db.list_documents(
      database_id = self.db_id,
      collection_id = self.collection_id,
      queries=[
                Query.order_desc("date"),  # Sort by "name" in ascending order
            ]
    )

    for rsul in results["documents"]:
      rsul.pop("userId", None)
      rsul.pop('$permissions', None)

    latest_date = datetime.strptime(results["documents"][0]["date"], "%Y-%m-%d").strftime("%Y-%m")
    if month == "null" and year == "null":
      transactions_results = [
        resutl
        for resutl in results['documents']
        if datetime.strptime(resutl["date"], "%Y-%m-%d").strftime("%Y-%m") == latest_date
      ]
      return transactions_results
    else:
      month_number = datetime.strptime(month, "%B").month
      transactions_results = [
        resutl
        for resutl in results['documents']
        if datetime.strptime(resutl["date"], "%Y-%m-%d").strftime("%Y-%m") == f"{year}-{month_number}"
      ]

      return transactions_results

  
  def get_transaction(self, transaction_id):
    result = db.get_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id=transaction_id
        )
    
    return result
  
  def save(self, data, user_data):
    data = get_insert_data(data, user_data)

    for row in data:
      result = db.create_document(
              database_id= self.db_id,
              collection_id= self.collection_id,
              document_id=secrets.token_hex(8),
              data=row,
              permissions=[
                Permission.read(Role.user(user_data[0])),
                Permission.update(Role.user(user_data[0])),
                Permission.delete(Role.user(user_data[0]))
              ]
          )
      
    return result
  
  def delete(self, transaction_id):
    result = db.delete_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= transaction_id,
        )

    return result
  
  def update(self, transaction_id, data):
    result = db.update_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= transaction_id,
            data=data
        )

    return result