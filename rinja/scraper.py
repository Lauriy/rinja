import decimal

import bs4
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


def _mine_table_for_data(table_bs4: bs4.BeautifulSoup):
    for row in table_bs4.select('tbody > tr'):
        columns = row.select('td')
        display_name = columns[0].get('data-sort-by').strip()
        ticker = columns[0].contents[4].strip().replace('\\t', '')
        category_spans = columns[1].select('span')
        category = None
        if len(category_spans):
            category = category_spans[0].get('title').strip()
        market = columns[2].contents[0].strip()
        price_change_in_currency_spans = columns[3].select('span')
        price_change_in_currency = None
        if len(price_change_in_currency_spans):
            # price_change_in_currency = Money(price_change_in_currency_spans[0].contents[0], 'EUR')
            price_change_in_currency = decimal.Decimal(price_change_in_currency_spans[0].contents[0])
        price_change_percentage_spans = columns[4].select('span')
        price_change_percentage = None
        if len(price_change_percentage_spans):
            price_change_percentage = decimal.Decimal(price_change_percentage_spans[0].contents[0])
        close_price = None
        if len(columns[5].contents):
            close_price = decimal.Decimal(columns[5].contents[0])
        last_price = None
        if len(columns[6].contents):
            last_price = decimal.Decimal(columns[6].contents[0])
        ask = decimal.Decimal(columns[7].contents[0].strip().replace('\\t', ''))
        bid = None
        print(display_name, ticker, category, market, price_change_in_currency, price_change_percentage, close_price,
              last_price)

    return []


def scrape_general_market_data_for_date(year: int, month: int, day: int):
    # url = f'https://www.nasdaqbaltic.com/statistics/en/shares?date={year}-{month}-{day}'
    url = f'https://www.nasdaqbaltic.com/statistics/en/shares'
    prices_response = requests.get(url)
    tables = bs4.BeautifulSoup(prices_response.text, 'html.parser').select('.biglisttable.table-responsive > table')
    stocks = []
    for table in tables:
        stocks += _mine_table_for_data(table)

    return stocks
