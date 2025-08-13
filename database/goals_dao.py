from database.deps import DATABASE_ID, GOALS_COLLECTION_ID
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from database.transaction_dao import TransactionDao
from models.send.goals import  currency_response, get_insert_data
import secrets
from appwrite.query import Query


class GoalsDao:
  def __init__(self, db):
    self.db = db
    self.db_id = DATABASE_ID
    self.collection_id = GOALS_COLLECTION_ID
  

  def get_goals(self, user_data=None):
    all_goals = []
    limit = 100
    offset = 0

    while True:
        result = self.db.list_documents(
            database_id=self.db_id,
            collection_id=self.collection_id,
            queries=[Query.order_asc("date"), Query.limit(limit), Query.offset(offset)],
        )
        docs = result["documents"]
        for doc in docs:
            doc.pop("userId", None)
            doc.pop("$permissions", None)
        all_goals.extend(docs)

        if len(docs) < limit:
            break
        offset += limit

    return all_goals

  
  def update_currency(self, cleintCurrency, user_data):
    goals = self.get_goals()
    if goals:
      responses = currency_response(goals, cleintCurrency)
      for response in responses:
        response.pop("$databaseId", None)
        response.pop("$collectionId", None)

        self.db.update_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= response["$id"],
            data=response
        )
  
  def save(self, data, user_data):
    transactions = TransactionDao(user_data[2]).get_transactions()
    goals = self.get_goals()

    data = get_insert_data(data, transactions, goals, int(user_data[1]))

    existing_goals = self.get_goals()
    
    if existing_goals:
        results = [(entry['date'], entry['$id']) for entry in existing_goals]
        list_dates, list_ids = zip(*results) if results else ([], [])
    else:
      results = None
    for row in data:
      if results != None and row["date"] in list_dates:
        for result in results:
          if result[0] == row["date"]:
            self.db.update_document(
                  database_id= self.db_id,
                  collection_id= self.collection_id,
                  document_id= result[1],
                  data=row,
                  permissions=[
                      Permission.read(Role.user(user_data[0])),
                      Permission.update(Role.user(user_data[0])),
                      Permission.delete(Role.user(user_data[0]))
                  ]
              )
      else:
        try:
          result = self.db.create_document(
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
        except Exception as e:
          print("Not valid to save:", e)
    return "Ok"
