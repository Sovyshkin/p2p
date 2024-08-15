import requests
import json
from time import sleep


def take_payment_only(tokenId, currencyId):
    if str(currencyId) == '' or str(currencyId) == "None":
        currencyId = 'RUB'

    if str(tokenId) == '' or str(tokenId) == "None":
        tokenId = 'USDT'
    
    
    amount = '' #'20000'
    tokenId = tokenId #'USDT'
    currencyId = currencyId #'RUB' #'THB'
 
    paymant = [] # всего банков 37
    side = '0' #продажа 1-покупка

    headers = {
    'accept': 'application/json',
    'accept-language': 'en',
    'content-type': 'application/json;charset=UTF-8',
    'lang': 'en',
    'origin': 'https://www.bybit.com',
    'platform': 'PC',
    'referer': 'https://www.bybit.com/',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    json_data = {
    'userId': '',
    'tokenId': tokenId, #'USDT',
    'currencyId': currencyId,
    'payment': [],#paymant,#['14'],#f'{paymant}',
    'side': side,#'0',
    'size': '300000',
    'page': '1',
    'amount': '',#amount,
    'authMaker': False,
    'canTrade': False,
    }

    response = requests.post('https://api2.bybit.com/fiat/otc/item/online', headers=headers, json=json_data)
    #print(json_data)
    #print(response.json())
    #return response.json()
    data_firstPage = response.json()
    data_firstPage = data_firstPage['result']['items']
    counter = 1
    print("Для - ", currencyId)

    only_payments = []
    only_data_byb = {}
    for i in data_firstPage:  
        #if counter > 2:      
        #print(f"{counter}. Никнейм: {i['nickName']}, Цена: {i['price']}")
        #print(i)
        for pay in i['payments']:
            #print(f'{pay}')
            if pay not in only_payments:
                only_payments.append(pay)
        only_data_byb[counter] = i
        counter +=1

    #print(only_data_byb)
    count_payment = 0
    for i in only_payments:
        count_payment +=1
    #print("Payment: ", only_payments, count_payment)
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(only_data_byb, file, ensure_ascii=False, indent=4)

    return only_payments


def take_metods(only_pays):
    bank_filter = {}
    headers = {
        'accept': 'application/json',
        'accept-language': 'ru-RU',
        'content-type': 'application/x-www-form-urlencoded',
        'lang': 'ru-RU',
        'origin': 'https://www.bybit.com',
        'platform': 'PC',
        'priority': 'u=1, i',
        'referer': 'https://www.bybit.com/',
    }

    response = requests.post('https://api2.bybit.com/fiat/otc/configuration/queryAllPaymentList', headers=headers)

    #print(response.json())
    r = response.json()
    count_bank = 0

    array_bank_byb = []
    for i in r['result']['paymentConfigVo']:
        if i['paymentType'] in only_pays:
            # print(type(i['paymentType']), i['paymentType'], type(i['paymentName']), i['paymentName'])
            count_bank +=1
            bank_filter[i['paymentType']] = i['paymentName']
            a = {"id" : f"{i['paymentType']}", "name": i['paymentName'],}
            array_bank_byb.append(a)
    # print('Only bank: ', count_bank)
    bank_filter = [bank_filter]
    return array_bank_byb #bank_filter


def take_byb(tokenId, amount, currencyId, paymant, side):

    if str(currencyId) == '' or str(currencyId) == "None":
        currencyId = 'RUB'

    if str(tokenId) == '' or str(tokenId) == "None":
        tokenId = 'USDT'

    if str(amount) == '' or str(amount) == "None" or str(amount) == '0':
        amount = ''

    if str(paymant) == '' or str(paymant) == "None":
        paymant = []

    if str(side) == '' or str(side) == "None":
        side = '1'


    headers = {
    'accept': 'application/json',
    'accept-language': 'en',
    'content-type': 'application/json;charset=UTF-8',
    'lang': 'en',
    'origin': 'https://www.bybit.com',
    'platform': 'PC',
    'referer': 'https://www.bybit.com/',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    json_data = {
    'userId': '',
    'tokenId': tokenId, #'USDT',
    'currencyId': currencyId,
    'payment': paymant,#['14'],#f'{paymant}',
    'side': str(side),#'0',
    'size': '10',
    'page': '1',
    'amount': str(amount),
    'authMaker': False,
    'canTrade': False,
    }

    response = requests.post('https://api2.bybit.com/fiat/otc/item/online', headers=headers, json=json_data)
    print("Check: ", tokenId, amount, currencyId, paymant, side)
    #print(response.text)
    data_firstPage = response.json()
    data_firstPage = data_firstPage['result']['items']
    counter = 1
    print("Для - ", currencyId)

    only_payments = []
    only_data_byb = {}
    for i in data_firstPage:  
        #if counter > 2:      
        #print(f"{counter}. Никнейм: {i['nickName']}, Цена: {i['price']}")
        #print(i)
        only_data_byb[counter] = i
        counter +=1

    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(only_data_byb, file, ensure_ascii=False, indent=4)

    return data_firstPage #only_payments


# #Выбор из какой монеты в какую валюту
# tokenId = None #должно предоваться 'USDT' если ничего не выбранно 
# currencyId = None #должно предоваться "RUB" если ничего не выбранно 

# #Получение доступных методов оплаты (банки):
# only_pays = take_payment_only(tokenId, currencyId)
# name_banks = take_metods()

# amount = '' #'20000'
# paymant = []
# side = '0' #продажа 1-покупка

# price_list = take_byb(tokenId, amount, currencyId, paymant, side)
# print(price_list)

def take_spot_bybit():

    headers = {
        'Content-Type': 'application/json',
    }
    
    params = (
        ('symbol', 'USDT'),  # Фильтр по символу USDT
    )
    
    response = requests.get('https://api.bybit.com/v2/public/symbols', headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        futures_pairs = [pair['name'] for pair in data['result']]
        bybit_symb = futures_pairs
        price_spot_bybit = {}
        # print(futures_pairs)
        # for symbol in futures_pairs:
        #     print("Берем цену монеты: ", symbol)
        #     if len(futures_pairs) > 0:
        #         url = f'https://api.bybit.com/v5/market/tickers?category=inverse&symbol={symbol}'
        #         response = requests.get(url)
        #         price = response.json()
        #         current_price = float(price['result']['list'][0]['lastPrice'])
        #         price_spot_bybit[symbol] = str(current_price)
        # return price_spot_bybit
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        e = 'Error take spot bybit!'
        return e

# spot_bybit_price = take_spot_bybit()
# print(spot_bybit_price)