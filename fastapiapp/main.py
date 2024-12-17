import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import transaction

load_dotenv()

PUBLIC_SITE = os.getenv('NEXT_PUBLIC_SITE_URL')

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=[PUBLIC_SITE],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

app.include_router(transaction.router, prefix="/api")
