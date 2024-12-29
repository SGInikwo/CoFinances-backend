import os
from dotenv import load_dotenv

from appwrite.client import Client

load_dotenv()

PROJECT_ID = os.getenv('APPWRITE_PROJECT')
API_KEY = os.getenv('APPWRITE_KEY')
DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
USER_COLLECTION_ID = os.getenv('APPWRITE_USER_COLLECTION_ID')
CURRENCY_COLLECTION_ID = os.getenv('APPWRITE_CURRENCY_COLLECTION_ID')
USERTOKEN_COLLECTION_ID = os.getenv('APPWRITE_USERTOKEN_COLLECTION_ID')
TRANSACTION_COLLECTION_ID = os.getenv('APPWRITE_TRANSACTION_COLLECTION_ID')
TRANSACTIONSUMMARY_COLLECTION_ID = os.getenv('APPWRITE_TRANSACTIONSUMMARY_COLLECTION_ID')
ENDPOINT = os.getenv('APPWRITE_ENDPOINT')

def createSessionClient():
  client = Client()
  client.set_endpoint(ENDPOINT)
  client.set_project(PROJECT_ID)

  return client

def createAdminClient():
  client = Client()
  client.set_endpoint(ENDPOINT)
  client.set_project(PROJECT_ID)
  client.set_key(API_KEY)

  return client