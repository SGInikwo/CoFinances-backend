import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import transaction, userToken

load_dotenv()

PUBLIC_SITE = os.getenv('NEXT_PUBLIC_SITE_URL')
PUBLIC_SITE1 = os.getenv('NEXT_PUBLIC_SITE_URL1')
PUBLIC_SITE2 = os.getenv('NEXT_PUBLIC_SITE_URL2')

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=[PUBLIC_SITE, PUBLIC_SITE1, PUBLIC_SITE2],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

app.include_router(transaction.router, prefix="/api")
app.include_router(userToken.router, prefix="/api")
