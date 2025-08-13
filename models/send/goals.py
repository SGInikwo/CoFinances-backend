from models.send.helper_functions.goals_data import goals_dataframe, currency_update_dataframe

def get_insert_data(requests, transactions, goals, currency):
  requests = goals_dataframe(requests, transactions, goals, currency)
  print(f"requests: {requests}\n\n")
  return requests

def currency_response(transactions, cleintCurrency):
   response = currency_update_dataframe(transactions, cleintCurrency)
   return response