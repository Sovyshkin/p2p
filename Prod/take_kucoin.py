import requests
from time import sleep

def take_code_bank(coin):
    code_banks_kucoin = {}
    headers = {
        'authority': 'www.kucoin.com',
        'accept': 'application/json',
        'accept-language': 'ru,en;q=0.9',
        'referer': 'https://www.kucoin.com/ru/otc/buy/USDT-RUB',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Chromium";v="112"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
    }

    params = {
        'legal': coin, #'RUB',
        'lang': 'ru_RU',
    }

    array_bank_kuc = []
    response = requests.get('https://www.kucoin.com/_api/otc/legal/payTypes', params=params, headers=headers)
    data = response.json()
    count_banks = 0
    # print('Data kucoin1: ', data['data'])
    for i in data['data']:
        if len(data['data']) != 0:
            # print(i['payTypeCode'])
            code_banks_kucoin[count_banks] = i['payTypeCode']
            count_banks +=1

            a = {"id" : f"{i['payTypeCode']}", "name": i['payTypeCode']}
            array_bank_kuc.append(a)
        else:
            print("Ошибка в получение данных по банкам Кукоин")

    return array_bank_kuc



def parce_cucoin(symbol, coin, type_c, code_bank):
    data_price_kucoin = {}
    #types = ['SELL','BUY']#sell = купить , buy = продать тут напутано нахуй 
    if str(type_c) == '0':
        type_c = 'SELL'

    if str(type_c) == '1':
        type_c = 'BUY'

    #def zapros(coin, type_c):
    headers = {
        'authority': 'www.kucoin.com',
        'accept': 'application/json',
        'accept-language': 'ru,en;q=0.9',
        'referer': 'https://www.kucoin.com/ru/otc/buy/USDT-RUB',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Chromium";v="112"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
    }


    params = {
        'status': 'PUTUP',
        'currency': symbol,#coin,#'USDT',
        'legal': coin,#'RUB',
        'page': '1',
        'pageSize': '10',
        'side': type_c, #'BUY',
        'amount': '',
        'payTypeCodes': code_bank, #'',
        'sortCode': 'PRICE',
        'highQualityMerchant': '0',
        'lang': 'ru_RU',
    }

    response = requests.get('https://www.kucoin.com/_api/otc/ad/list', params=params, headers=headers)
    data = response.json()
    # print('Data kucoin: ', data['items'])
    for i in data['items']:
        if len(data['items']) != 0:
            # print(i['nickName'], i['floatPrice'], 'limit:', i['limitMinQuote'], '-', i['limitMaxQuote'])
            for i in data['items']:
                data_price_kucoin[coin] = i
            return data['items']

        else:
            a = "Ошибка в получение данных предложений Кукоин"
            print("Ошибка в получение данных предложений Кукоин")
            return a

def kukoin_spot():
    response = requests.get('https://api.kucoin.com/api/v1/market/allTickers')
    data = response.json()
    #print(data)
    data_kuc_spot = []
    for i in data['data']['ticker']:
        # print(i['symbolName'], i['last'])
        a = {'symbol': i['symbolName'], 'price': i['last']}
        data_kuc_spot.append(a)
    # print(data_kuc_spot)
    return data_kuc_spot

#kukoin_spot()

# symbol = 'USDT' 
# coin = 'RUB' 
# type_c = '0' 
# code_bank = 'BANK' 
   
# types = ['SELL','BUY']#sell = купить , buy = продать тут напутано нахуй 
# symbol = ['USDT', 'BTC', 'ETH', 'KCS','USDC']  # список коинов


#code_bank_kucoin = take_code_bank(coin) # coin = 'RUB'
#parce_cucoin(symbol, coin, type_c, code_bank) #symbol = 'USDT' coin = 'RUB' type_c = '0' code_bank = 'QIWI'
#kukoin_spot()#данные по споту 





