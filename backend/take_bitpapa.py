import requests
import json
import re


def parce_bitpapa(side, amount, currency_cod, fiat, pay_method): 

    sort = 'price'
    if str(side) == '0':
        side = 'sell'
        sort = 'price'

    if str(side) == '1':
        side = 'buy'
        sort = '-price'

    params = {
        'type': side,
        'page': '1',
        'sort': sort,#'-price',
        'currency_code': currency_cod,#'RUB',
        'previous_currency_code': currency_cod,#'RUB',
        'crypto_currency_code': fiat,#'BTC',
        'with_correct_limits': 'false',
        'limit': '10',
        'pages': '15',
    }
    #side, amount, currency_cod, fiat, pay_method
    #'sell', '10000', 'USD', 'BTC', 'SPECIFIC_BANK'   
    if amount != '0':
        params['amount'] = str(amount)
    if pay_method != []:
        params['payment_method_code'] = str(pay_method)
    

    r = requests.get('https://bitpapa.com/api/v1/pro/search', params=params)
    json_string = r.text
    data = r.json()
    #print(json_string)
    print('BITPAPA', data)
    data_papa_p2p = []
    for i in data['ads']:
        #print(i['user']['user_name'], i['price'], 'Limit: ', i['limit_min'], '-' ,i['limit_max'])
        try:
            a = {'user': i['user']['user_name'], 'price': i['price'], 'min': i['limit_min'], 'max': i['limit_max'], 'bank_name': i['payment_method_banks'][0]['name'], 'bank_id': i['payment_method_banks'][0]['code'],}
        except:
            a = {'user': i['user']['user_name'], 'price': i['price'], 'min': i['limit_min'], 'max': i['limit_max'], 'bank_name': i['payment_method']['name'], 'bank_id': i['payment_method']['id']}
        data_papa_p2p.append(a)

    return data_papa_p2p


def bitpapa_spot():
    r = requests.get('https://bitpapa.com/api/v1/exchange_rates/all')

    data = r.json()
    spot_papa = []
    for i in data['rates']:
        # print(i, data['rates'][i])
        symbol = i.replace("_", "")
        a = {'symbol': symbol, 'price': str(data['rates'][i])}
        spot_papa.append(a)
        
    return spot_papa


def only_bank_papa():
    response = requests.get('https://bitpapa.com/buy')
    #print(response.text)
    with open("bitpapa_paymetod.html", "w", encoding="utf-8") as file:
        file.write(response.text)
    pattern = r"<script>\s*var INITIAL_STATE\s*=\s*\{(.*)\}\s*</script>"
    match = re.search(pattern, response.text, re.DOTALL | re.MULTILINE)

    if match:
        # Извлечение содержимого переменной в виде строки
        initial_state_str = match.group(1)
        # print(initial_state_str)
        #decoded_initial_state_str = bytes(initial_state_str, "latin1").decode("unicode_escape")
        # Преобразование строки в словарь Python
        #initial_state_dict = json.loads(initial_state_str)
        
        #print(initial_state_dict)
        # print(initial_state_str)
        return initial_state_str
    else:
        print("Переменная INITIAL_STATE не найдена")

#def only_bank_papa():


# side = '0'
# amount = ''
# currency_cod = 'RUB'
# fiat = 'USDT'
# pay_method = ''
##'sell', '10000', 'USD', 'BTC', 'SPECIFIC_BANK'
# d = parce_bitpapa(side, amount, currency_cod, fiat, pay_method)
#print(d)


# info = bitpapa_spot()
# #print(info)