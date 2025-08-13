import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import transaction, userToken, currency, transactionSummary, goals, budgets, budgetSummary, category

load_dotenv()

URLS = os.getenv("NEXT_PUBLIC_SITE_URL", "")
PUBLIC_SITE = [url.strip() for url in URLS.split(",") if url]


app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=PUBLIC_SITE,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

app.include_router(transaction.router, prefix="/api")
app.include_router(userToken.router, prefix="/api")
app.include_router(currency.router, prefix="/api")
app.include_router(transactionSummary.router, prefix="/api")
app.include_router(goals.router, prefix="/api")
app.include_router(budgets.router, prefix="/api")
app.include_router(budgetSummary.router, prefix="/api")
app.include_router(category.router, prefix="/api")
