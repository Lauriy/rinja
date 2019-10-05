import requests
import xlrd


def retrieve_general_market_data():
    # Data comes with 15 minutes of delay
    # url = f'https://www.nasdaqbaltic.com/statistics/en/shares?download=1&date={year}-{month}-{day}'
    url = f'https://www.nasdaqbaltic.com/statistics/en/shares?download=1'
    response = requests.get(url)
    parsed = xlrd.open_workbook(file_contents=response.content)
    worksheet = parsed.sheet_by_index(0)
    keys = worksheet.row_values(0)
    values = [worksheet.row_values(i) for i in range(1, worksheet.nrows)]
    dict_list = []
    for value in values:
        for inner_key, inner_value in enumerate(value):
            if inner_value == '':
                # This would cause so many headaches down the line otherwise
                value[inner_key] = None
        dict_list.append(dict(zip(keys, value)))

    return dict_list
