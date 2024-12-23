import secrets
import requests
import pandas as pd
from appwrite.client import Client
from appwrite.services.databases import Databases

from deps import createAdminClient, DATABASE_ID, CURRENCY_COLLECTION_ID


# Initialize Appwrite Client
client = createAdminClient()
db = Databases(client)


# Dictionary of currencies
currency = {"EUR": 0, "KRW": 1, "KES": 2, "GBP": 3}

# API base URL
api_url = "https://hexarate.paikama.co/api/rates/latest"

# Delete all existing documents in the collection
try:
    existing_documents = db.list_documents(database_id=DATABASE_ID, collection_id=CURRENCY_COLLECTION_ID).get("documents", [])
    for doc in existing_documents:
        doc_id = doc["$id"]
        db.delete_document(database_id=DATABASE_ID, collection_id=CURRENCY_COLLECTION_ID, document_id=doc_id)
        print(f"Deleted document {doc_id}")
except Exception as e:
    print(f"Error deleting documents: {e}")

# Initialize the exchange rate table
currencies = list(currency.keys())
exchange_table = pd.DataFrame(index=currencies, columns=currencies)

# Fetch exchange rates and populate the table
for base in currencies:
    for target in currencies:
        if base == target:
            exchange_table.loc[base, target] = 1.0  # Same currency exchange rate is 1
        else:
            # Call Hexarate API
            response = requests.get(f"{api_url}/{base}?target={target}")
            if response.status_code == 200:
                response_data = response.json()
                rate = response_data.get("data", {}).get("mid")  # Extract 'mid' from 'data'
                exchange_table.loc[base, target] = rate
            else:
                exchange_table.loc[base, target] = None  # Mark as None if request fails

# Save exchange rates to Appwrite database
for base in currencies:
    for target in currencies:
        rate = exchange_table.loc[base, target]
        if rate is not None:  # Only save valid rates
            document_data = {
                "base_currency": base,
                "target_currency": target,
                "exchange_rate": rate
            }
            try:
                db.create_document(
                    database_id=DATABASE_ID,
                    collection_id=CURRENCY_COLLECTION_ID,
                    document_id=secrets.token_hex(8),  # Auto-generate unique document IDs
                    data=document_data
                )
                print(f"Created rate {base} to {target}: {rate}")
            except Exception as e:
                print(f"Failed to create rate {base} to {target}: {e}")

# # Dictionary of currencies
# currency = {"EUR": 0, "KRW": 1, "KES": 2, "GBP": 3, "USD": 4}

# # API base URL
# api_url = "https://hexarate.paikama.co/api/rates/latest"

# # Initialize the exchange rate table
# currencies = list(currency.keys())
# exchange_table = pd.DataFrame(index=currencies, columns=currencies)

# # Fetch exchange rates and populate the table
# for base in currencies:
#     for target in currencies:
#         if base == target:
#             exchange_table.loc[base, target] = 1.0  # Same currency exchange rate is 1
#         else:
#             # Call Hexarate API
#             response = requests.get(f"{api_url}/{base}?target={target}")
#             if response.status_code == 200:
#                 response_data = response.json()
#                 rate = response_data.get("data", {}).get("mid")  # Extract 'mid' from 'data'
#                 exchange_table.loc[base, target] = rate
#             else:
#                 exchange_table.loc[base, target] = None  # Mark as None if request fails

# print(exchange_table)

# # Save or update exchange rates in Appwrite database
# for base in currencies:
#     for target in currencies:
#         rate = exchange_table.loc[base, target]
#         if rate is not None:  # Only process valid rates
#             document_data = {
#                 "base": base,
#                 "target": target,
#                 "rate": rate
#             }

#             # Check if the document already exists
#             query = [
#                 f'base="{base}"',
#                 f'target="{target}"'
#             ]
#             try:
#                 # existing_documents = db.list_documents(
#                 #     database_id=DATABASE_ID,
#                 #     collection_id=CURRENCY_COLLECTION_ID,
#                 #     queries=query
#                 # ).get("documents", [])

#                 # if existing_documents:
#                 #     # Update the existing document
#                 #     document_id = existing_documents[0]["$id"]
#                 #     db.update_document(
#                 #         database_id=DATABASE_ID,
#                 #         collection_id=CURRENCY_COLLECTION_ID,
#                 #         document_id=currency[base],
#                 #         data=document_data
#                 #     )
#                 #     print(f"Updated rate {base} to {target}: {rate}")
#                 # else:
#                 #     print("here I am")
#                 #     # Create a new document
#                   db.create_document(
#                       database_id=DATABASE_ID,
#                       collection_id=CURRENCY_COLLECTION_ID,
#                       document_id=secrets.token_hex(8),  # Auto-generate unique document IDs
#                       data=document_data
#                   )
#                   print(f"Created rate {base} to {target}: {rate}")
#             except Exception as e:
#                 print(f"Error processing rate {base} to {target}: {e}")
