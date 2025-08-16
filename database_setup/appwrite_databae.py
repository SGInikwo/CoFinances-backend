from appwrite.client import Client
from appwrite.services.databases import Databases
import json

import os
import secrets
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv('APPWRITE_PROJECT')
API_KEY = os.getenv('APPWRITE_KEY')
DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
ENDPOINT = os.getenv('APPWRITE_ENDPOINT')

# 🔹 Setup Appwrite client for the NEW project
client = Client()
client.set_endpoint(ENDPOINT)  # Change if self-hosted
client.set_project(PROJECT_ID)  # Your new project ID
client.set_key(API_KEY)  # API Key with database write access

databases = Databases(client)

# 🔹 Create a new database in the new project
# DATABASE_ID = secrets.token_hex(8)
# databases.create(database_id=DATABASE_ID, name="test_cofinances")

# 🔹 Load exported collections from the old project
with open("./collections/collections.json", "r") as f:
    collections_data = json.load(f)

# 🔹 Loop through each collection and recreate it
for col in collections_data.get("collections", []):
    col_id = col["$id"]
    col_name = col["name"]
    doc_security = col["documentSecurity"]
    enab = col["enabled"]
    print(f"Creating collection: {col_name}")

    # Create the collection
    databases.create_collection(
        database_id=DATABASE_ID,
        collection_id=col_id,
        name=col_name,
        permissions=col.get("permissions", []),
        document_security=doc_security,
        enabled=enab,
    )

    # Create each attribute
    for attr in col.get("attributes", []):
        print(f"Creating atribute: {attr['key']}")
        attr_type = attr["type"]
        key = attr["key"]
        required = attr["required"]
        default = attr.get("default")

        if attr_type == "string":
            databases.create_string_attribute(
                database_id=DATABASE_ID,
                collection_id=col_id,
                key=key,
                size=attr["size"],
                required=required,
                default=default
            )
        elif attr_type == "integer":
            databases.create_integer_attribute(
                database_id=DATABASE_ID,
                collection_id=col_id,
                key=key,
                required=required,
                min=int(attr.get("min", None)),
                max=int(attr.get("max", None)),
                default=default
            )
        elif attr_type == "boolean":
            databases.create_boolean_attribute(
                database_id=DATABASE_ID,
                collection_id=col_id,
                key=key,
                required=required,
                default=default
            )
        elif attr_type == "float":
            databases.create_float_attribute(
                database_id=DATABASE_ID,
                collection_id=col_id,
                key=key,
                required=required,
                min=float(attr.get("min", None)),
                max=float(attr.get("max", None)),
                default=default
            )
        elif attr_type == "email":
            databases.create_email_attribute(
                database_id=DATABASE_ID,
                collection_id=col_id,
                key=key,
                required=required,
                default=default
            )

print("✅ All collections recreated successfully!")
