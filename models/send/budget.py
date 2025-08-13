from models.send.helper_functions.budget_data import currency_update_dataframe, earliest_date_dataframe, update_budget_actuals


def get_insert_data(requests, user_data):
   print(f"request: {requests}")
   data = []
   for request in requests:
      request_dict = dict(request)
      if request_dict["actual"] != 0.0:
         request_data = {
            "id": request_dict["id"],
            "category": request_dict["category"],
            "budget": request_dict["budget"],
            "actual": request_dict["actual"],
            "date": request_dict["date"],
            "originalBudget": request_dict["actual"],
            "originalActual": request_dict["budget"],
            "currency": int(user_data[1]),
            "originalCurrency": int(user_data[1]),
            "update": False
         }
         data.append(request_data)
      else:
         request_data = {
            "id": request_dict["id"],
            "category": request_dict["category"],
            "budget": request_dict["budget"],
            "actual": request_dict["actual"],
            "date": request_dict["date"],
            "originalBudget": request_dict["budget"],
            "originalActual": request_dict["actual"],
            "currency": int(user_data[1]),
            "originalCurrency": int(user_data[1]),
            "update": True
         }
         data.append(request_data)

      
   date = earliest_date_dataframe(data)

   data = update_budget_actuals(data, date, user_data)
   return data, date

def currency_response(budgets, cleintCurrency):
   response = currency_update_dataframe(budgets, cleintCurrency)
   return response