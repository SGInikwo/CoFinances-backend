from models.send.helper_functions.transactionSummary_data import create_dataframe, monthly_dataframe, summary_dataframe


def get_insert_data(transactions, uCurrency):
  df = create_dataframe(transactions, uCurrency)
  return df.to_dict(orient='records')


def custom_summary(transactions, month, year):
  response = summary_dataframe(transactions, month, year)
  return response


def list_of_months(summary):
  response = monthly_dataframe(summary)
  return response