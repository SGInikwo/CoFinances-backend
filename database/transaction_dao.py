from database.deps import createAdminClient, DATABASE_ID, TRANSACTION_COLLECTION_ID
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.query import Query
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import secrets
from datetime import datetime
from database.category_dao import CategoryDao
from database.transactionSummary_dao import SummaryDao
from database.budgetSummary_dao import BudgetSummaryDao

from models.send.transactions import currency_response, current_analysis, get_insert_data, past_analysis, update_category

# client = createAdminClient()
# db = Databases(client)

class TransactionDao:
  def __init__(self, db):
    self.db = db
    self.db_id = DATABASE_ID
    self.collection_id = TRANSACTION_COLLECTION_ID

  
  def get_all_transactions(self):
    all_docs = []
    limit = 100
    offset = 0
    while True:
        results = self.db.list_documents(
            database_id=self.db_id,
            collection_id=self.collection_id,
            queries=[
                Query.order_desc("date"), Query.limit(limit), Query.offset(offset)
            ],
        )
        docs = results["documents"]
        for d in docs:
            d.pop("userId", None)
            d.pop("$permissions", None)
        all_docs.extend(docs)
        if len(docs) < limit:
            break
        offset += limit
    return all_docs



  def get_transactions(self, user_data=None, month=None, year=None):
    all_docs = []
    limit = 100
    offset = 0

    # Step 1: Fetch all documents with pagination
    while True:
        results = self.db.list_documents(
            database_id=self.db_id,
            collection_id=self.collection_id,
            queries=[
                Query.order_desc("date"), Query.limit(limit), Query.offset(offset)
            ],
        )
        docs = results["documents"]
        for d in docs:
            d.pop("userId", None)
            d.pop("$permissions", None)
        all_docs.extend(docs)
        if len(docs) < limit:
            break
        offset += limit

    if not all_docs:
        return []

    # Step 2: Determine target_date (yyyy-mm)
    latest_date = datetime.strptime(all_docs[0]["date"], "%Y-%m-%d").strftime("%Y-%m")

    if month in [None, "null"] and year in [None, "null"]:
        target_date = latest_date
    elif not str(month).isdigit():
        try:
            month_number = datetime.strptime(str(month), "%B").month
            target_date = f"{year}-{month_number:02d}"
        except ValueError:
            raise ValueError(f"Invalid month: {month}. Please provide a valid full month name.")
    else:
        try:
            target_date = f"{year}-{str(month).zfill(2)}"
        except ValueError:
            raise ValueError(f"Invalid month: {month}. Please provide a valid full month number.")

    # Step 3: Filter docs by target_date
    transactions_results = [
        doc for doc in all_docs
        if datetime.strptime(doc["date"], "%Y-%m-%d").strftime("%Y-%m") == target_date
    ]

    return transactions_results

  
  def get_transaction(self, transaction_id):
    result = self.db.get_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id=transaction_id
        )
    return result
  

  def current_month_expenses(self, user_data=None, month=None, year=None):
    try:
      transactions = self.get_transactions(month=month, year=year)
      response = current_analysis(transactions)
    except:
       return None
    return response
  

  def past_month_expenses(self, user_data=None, month=None, year=None):
    try:
      transactions = self.get_all_transactions()
      response = past_analysis(transactions, month, year)
    except:
       return None
    return response
    

  def update_currency(self, cleintCurrency, user_data):
    transactions = self.get_all_transactions()
    if transactions:
      responses = currency_response(transactions, cleintCurrency)
      for response in responses:
        response.pop("$databaseId", None)
        response.pop("$collectionId", None)

        self.db.update_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= response["$id"],
            data=response
        )
    
  
  def update(self, data, user_data):
    responses = update_category(data.update)
    for response in responses:
      result = self.db.update_document(
              database_id= self.db_id,
              collection_id= self.collection_id,
              document_id= response["id"],
              data=response
          )
    return result
  

  def save(self, data, user_data):
    category = CategoryDao(user_data[2]).get_all_categories()

    data = get_insert_data(data.transactions, data.clientCurrency, user_data, category)

    for row in data[0]:
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
        # break
      except:
         print("Not valid to save")
    
    self.update_currency(cleintCurrency=int(user_data[1]), user_data=user_data)

    for date in data[1]:
      SummaryDao(user_data[2]).push_data(user_data=user_data, month=date["month"], year=date["year"], all=False)
      BudgetSummaryDao(user_data[2]).push_data(user_data=user_data, month=date["month"], year=date["year"], all=False)
    return result
  

  def delete(self, transaction_id):
    result = self.db.delete_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= transaction_id,
        )
    return result