from models.send.helper_functions.budgetSummary_data import create_dataframe, currency_update_dataframe

def get_insert_data(budgets, categories, uCurrency):
  df = create_dataframe(budgets, categories, uCurrency)
  return df.to_dict(orient='records')

def currency_response(budgetsSummary, cleintCurrency):
   response = currency_update_dataframe(budgetsSummary, cleintCurrency)
   return response