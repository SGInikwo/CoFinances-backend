from database.deps import createAdminClient, DATABASE_ID, BUDGETSUMMARY_COLLECTION_ID
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.query import Query
from models.send.budgetSmmary import get_insert_data
import secrets
from models.send.budgetSmmary import currency_response

class BudgetSummaryDao:
  def __init__(self, db):
    self.db = db
    self.db_id = DATABASE_ID
    self.collection_id = BUDGETSUMMARY_COLLECTION_ID

  
  def get_summary(self):
    all_docs = []
    limit = 100
    offset = 0

    while True:
        results = self.db.list_documents(
            database_id=self.db_id,
            collection_id=self.collection_id,
            queries=[
                Query.order_desc("date"),  # Sort by "date" descending
                Query.limit(limit), Query.offset(offset)
            ],
        )

        docs = results["documents"]
        for doc in docs:
            doc.pop("userId", None)
            doc.pop("$permissions", None)

        all_docs.extend(docs)

        if len(docs) < limit:
            break

        offset += limit

    return all_docs

  
  def update_currency(self, cleintCurrency, user_data):
    budgets = self.get_summary()
    if budgets:
      responses = currency_response(budgets, cleintCurrency)
      for response in responses:
        response.pop("$databaseId", None)
        response.pop("$collectionId", None)

        self.db.update_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= response["$id"],
            data=response
        )
  
  def push_data(self, user_data, month=None, year=None, all=False):
    from database.budget_dao import BudgetDAO
    from database.category_dao import CategoryDao

    if all==True:
      budgets = BudgetDAO(user_data[2]).get_budgets(user_data=user_data[0])
    else:
      budgets = BudgetDAO(user_data[2]).get_budgets(user_data=user_data[0], month=month, year=year)

    categories = CategoryDao(user_data[2]).get_all_category_name()

    if budgets:
      data = get_insert_data(budgets, categories, user_data[1])
      print(f"Data budget summary: {data}")

      exist_summary = self.get_summary()

      if exist_summary:
        results = [(entry['date'], entry['categoryId']["$id"], entry['$id']) for entry in exist_summary]
        list_dates, list_transId, list_ids = zip(*results) if results else ([], [], [])
      else:
        results = None
      for row in data:
        if results != None and row["date"] in list_dates and row["categoryId"] in list_transId:
          for result in results:
            if result[0] == row["date"] and result[1] == row["categoryId"]:
              self.db.update_document(
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
          self.db.create_document(
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