from database.deps import createAdminClient, DATABASE_ID, CATEGORY_COLLECTION_ID
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.query import Query
from datetime import datetime
from models.send.category import get_insert_data
import secrets

class CategoryDao:
  def __init__(self, db):
    self.db = db
    self.db_id = DATABASE_ID
    self.collection_id = CATEGORY_COLLECTION_ID

  def save(self, data, user_data):
    data = get_insert_data(data.category, user_data,)
    
    for row in data:
      try:
        result = self.db.create_document(
            database_id= self.db_id,
            collection_id= self.collection_id,
            document_id=secrets.token_hex(8),
            data=row,
        )
      except:
          print("Not valid to save")

  def get_all_categories(self):
    all_docs = []
    limit = 100
    offset = 0
    
    while True:
        results = self.db.list_documents(
            database_id=self.db_id,
            collection_id=self.collection_id,
            queries=[
                Query.order_desc("name"),  # Sort by "name" in descending order
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

  
  def get_all_category_name(self):
    all_docs = []
    limit = 100
    offset = 0

    while True:
        results = self.db.list_documents(
            database_id=self.db_id,
            collection_id=self.collection_id,
            queries=[
                Query.order_asc("name"),  # Sort by "name" ascending
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

    # Extract (name, $id) tuples and get unique pairs
    category = [(doc['name'], doc['$id']) for doc in all_docs]
    unique_category = list(set(category))

    # Optional: sort again by name after uniqueness
    unique_category.sort(key=lambda x: x[0])

    return unique_category

  