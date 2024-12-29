from models.send.helper_functions.transactionSummary_data import create_dataframe, summary_dataframe


def get_insert_data(transactions, uCurrency):
  df = create_dataframe(transactions, uCurrency)

  return df.to_dict(orient='records')


def custom_summary(transactions):
  response = summary_dataframe(transactions)

  return response