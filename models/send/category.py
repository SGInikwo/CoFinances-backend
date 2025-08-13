from models.send.helper_functions.category_data import earliest_date_dataframe


def get_insert_data(requests, userCurrency):
    print("get_insert_data called with requests:", requests)
    data = []
    request_dict = dict(requests)
    request_data = {
        "name": request_dict["name"],
        "colour": request_dict["colour"],
    }
    data.append(request_data)

    return data