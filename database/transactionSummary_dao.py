from database.deps import createAdminClient, DATABASE_ID, TRANSACTIONSUMMARY_COLLECTION_ID
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from models.send.transactionSummary_data import custom_summary, get_insert_data, list_of_months
# from database.transaction_dao import TransactionDao
import secrets
from appwrite.query import Query


client = createAdminClient()
db = Databases(client)

class SummaryDao:
  def __init__(self):
    self.db_id = DATABASE_ID
    self.collection_id = TRANSACTIONSUMMARY_COLLECTION_ID
  

  def get_summary(self, user_data=None):
    result = db.list_documents(
      database_id = self.db_id,
      collection_id = self.collection_id,
      queries=[
                Query.order_desc("date"),  # Sort by "name" in ascending order
            ]
    )
    for rsul in result["documents"]:
      rsul.pop("userId", None)
      rsul.pop('$permissions', None)
    return result['documents']
  

  def get_custom_summary(self, month=None, year=None):
    transactions = self.get_summary()
    response = custom_summary(transactions, month, year)
    return response
  
  
  def get_months(self, user_data):
    exist_summary = self.get_summary()
    months = list_of_months(exist_summary)
    return months

  
  def push_data(self, user_data, month=None, year=None, all=False):
    from database.transaction_dao import TransactionDao

    if all==False:
      transactions = TransactionDao().get_transactions(user_data=user_data[0])
    else:
      transactions = TransactionDao().get_transactions(user_data=user_data[0], month=month, year=year)

    data = get_insert_data(transactions, user_data[1])
    exist_summary = self.get_summary()

    for row in data:
      if exist_summary:
        results = [(entry['date'], entry['transactionId'], entry['$id']) for entry in exist_summary]

        for result in results:
          if result[0] == row["date"] and result[1] == row["transactionId"]:
            db.update_document(
                database_id= self.db_id,
                collection_id= self.collection_id,
                document_id= result[2],
                data=row,
                permissions=[
                    Permission.read(Role.user(user_data[0])),
                    Permission.update(Role.user(user_data[0])),
                    Permission.delete(Role.user(user_data[0]))
                ]
            )
      else:
        db.create_document(
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
    return "OK"
