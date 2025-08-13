from database.deps import createAdminClient, DATABASE_ID, BUDGETING_COLLECTION_ID
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.query import Query
from datetime import datetime
import secrets

from models.send.budget import currency_response, get_insert_data

class BudgetDAO:
  def __init__(self, db):
    self.db = db
    self.db_id = DATABASE_ID
    self.collection_id = BUDGETING_COLLECTION_ID
  
  def get_all_budgets(self):
    all_docs = []
    limit = 100
    offset = 0

    while True:
        results = self.db.list_documents(
            database_id=self.db_id,
            collection_id=self.collection_id,
            queries=[
                Query.order_desc("date"),
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

    dates = [doc['date'] for doc in all_docs]
    unique_dates = list(set(dates))

    return all_docs, unique_dates

  
  def get_budgets(self, user_data=None, month=None, year=None):
    all_docs = []
    limit=100
    offset = 0

    while True:
        results = self.db.list_documents(
            database_id=self.db_id,
            collection_id=self.collection_id,
            queries=[
                Query.order_desc("date"),
                Query.limit(limit), Query.offset(offset)
            ],
        )

        docs = results.get("documents", [])
        # Remove sensitive fields
        for doc in docs:
            doc.pop("userId", None)
            doc.pop("$permissions", None)
        
        all_docs.extend(docs)

        if len(docs) < limit:
            break
        offset += limit

    if not all_docs:
        return []

    # Extract the latest date in "YYYY-MM" format
    latest_date = datetime.strptime(all_docs[0]["date"], "%Y-%m").strftime("%Y-%m")

    if (month in [None, "null"] and year in [None, "null"]) or (month is None and year is None):
        target_date = latest_date
    else:
        if month is None or year is None:
            raise ValueError("Both month and year must be provided.")

        if not str(month).isdigit():
            try:
                month_number = datetime.strptime(month, "%B").month
                target_date = f"{year}-{month_number:02d}"
            except ValueError:
                raise ValueError(f"Invalid month name: {month}. Please provide full month name.")
        else:
            month_num = int(month)
            if not 1 <= month_num <= 12:
                raise ValueError(f"Invalid month number: {month}. Must be between 1 and 12.")
            target_date = f"{year}-{str(month_num).zfill(2)}"

    # Filter budgets by the target date
    budget_results = [
        doc
        for doc in all_docs
        if datetime.strptime(doc["date"], "%Y-%m").strftime("%Y-%m") == target_date
    ]

    return budget_results

  
  def update_currency(self, cleintCurrency, user_data):
    budgets = self.get_all_budgets()
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
  

  def save(self, data, user_data):
    from database.budgetSummary_dao import BudgetSummaryDao
    data = get_insert_data(data.budget, user_data,)

    for row in data[0]:
        if row["id"] == None:
            try:
                new_data = {k: v for k, v in row.items() if k not in ("id", "update")}
                result = self.db.create_document(
                        database_id= self.db_id,
                        collection_id= self.collection_id,
                        document_id=secrets.token_hex(8),
                        data=new_data,
                        permissions=[
                            Permission.read(Role.user(user_data[0])),
                            Permission.update(Role.user(user_data[0])),
                            Permission.delete(Role.user(user_data[0]))
                        ]
                    )
            except:
                print("Not valid to save")
        else:
            new_data = {k: v for k, v in row.items() if k not in ("id", "update", 'currency', 'originalCurrency', 'originalBudget', 'originalActual')}
            self.db.update_document(
                database_id= self.db_id,
                collection_id= self.collection_id,
                document_id= row["id"],
                data=new_data,
                permissions=[
                    Permission.read(Role.user(user_data[0])),
                    Permission.update(Role.user(user_data[0])),
                    Permission.delete(Role.user(user_data[0]))
                ]
            )
    
    self.update_currency(cleintCurrency=int(user_data[1]), user_data=user_data)
    
    for date in data[1]:
      BudgetSummaryDao(user_data[2]).push_data(user_data=user_data, month=date["month"], year=date["year"], all=False)
    return "ok"
        
  
  def update_currency(self, cleintCurrency, user_data):
    budgets = self.get_all_budgets()
    if budgets:
      responses = currency_response(budgets[0], cleintCurrency)
      for response in responses:
        response.pop("$databaseId", None)
        response.pop("$collectionId", None)

        self.db.update_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id= response["$id"],
            data=response
        )