from database.deps import createAdminClient, DATABASE_ID, TRANSACTION_COLLECTION_ID
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.query import Query
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import secrets
from datetime import datetime
from database.transactionSummary_dao import SummaryDao

from models.send.transactions import currency_response, current_analysis, get_insert_data, past_analysis

# client = createAdminClient()
# db = Databases(client)

class TransactionDao:
  def __init__(self, db):
    self.db = db
    self.db_id = DATABASE_ID
    self.collection_id = TRANSACTION_COLLECTION_ID

  
  def get_all_transactions(self):
    # Fetch documents from the database
    results = self.db.list_documents(
        database_id=self.db_id,
        collection_id=self.collection_id,
        queries=[
            Query.order_desc("date"),  # Sort by "date" in descending order
        ]
    )
    # Clean up sensitive fields
    for result in results["documents"]:
        result.pop("userId", None)
        result.pop("$permissions", None)
    return results["documents"]


  def get_transactions(self, user_data=None, month=None, year=None):
    # Fetch documents from the database
    results = self.db.list_documents(
        database_id=self.db_id,
        collection_id=self.collection_id,
        queries=[
            Query.order_desc("date"),  # Sort by "date" in descending order
        ]
    )
    # Clean up sensitive fields
    for result in results["documents"]:
        result.pop("userId", None)
        result.pop("$permissions", None)
    # Extract the latest date if no specific month and year are provided
    if not results["documents"]:
        return []  # Return an empty list if no documents are found

    latest_date = datetime.strptime(results["documents"][0]["date"], "%Y-%m-%d").strftime("%Y-%m")
    # Determine the target month and year
    if month in [None, "null"] and year in [None, "null"]:
        target_date = latest_date
    else:
        try:
            month_number = datetime.strptime(month, "%B").month
            target_date = f"{year}-{month_number:02d}"
        except ValueError:
            raise ValueError(f"Invalid month: {month}. Please provide a valid full month name.")

    # Filter transactions based on the target date
    transactions_results = [
        result
        for result in results["documents"]
        if datetime.strptime(result["date"], "%Y-%m-%d").strftime("%Y-%m") == target_date
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
    # print(response)
    return response
  

  def past_month_expenses(self, user_data=None, month=None, year=None):
    try:
      transactions = self.get_all_transactions()
      response = past_analysis(transactions, month, year)
    except:
       return None

    # print(response)
    return response
    
  

  def update_currency(self, cleintCurrency, user_data):
    transactions = self.get_all_transactions()
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
    
  
  def update(self, transaction_id, data):
    result = self.db.update_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= transaction_id,
            data=data
        )
    return result
  

  def save(self, data, user_data):
    data = get_insert_data(data.transactions, data.clientCurrency, user_data)

    for row in data[0]:
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
    for date in data[1]:
      SummaryDao(user_data[2]).push_data(user_data=user_data[0], month=date["month"], year=date["year"], all=False)
    return result
  

  def delete(self, transaction_id):
    result = self.db.delete_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= transaction_id,
        )
    return result