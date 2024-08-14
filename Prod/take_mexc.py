import requests

#ok

def take_p2p_mexc(amount,symbol, coin, payMethod, tradeType):
    coin_id = '128f589271cb4951b03e71e6323eb7be'#usdt

    if symbol == 'BTC':
        coin_id = 'febc9973be4d4d53bb374476239eb219'
    
    if symbol == 'USDT':
        coin_id = '128f589271cb4951b03e71e6323eb7be'#usdt

    if symbol == 'ETH':
        coin_id = '93c38b0169214f8689763ce9a63a73ff'

    if symbol == 'USDC':
        coin_id = '34309140878b4ae99f195ac091d49bab'

    if payMethod == []:
        payMethod = ''
    else:
        payMethod = ','.join(payMethod)
    # print(amount, coin, payMethod, tradeType)
    if amount == '0':
        amount = ''
    params = {
        'allowTrade': 'false',
        'amount': amount,#'',
        'blockTrade': 'false',
        'coinId': coin_id,
        'countryCode': '',
        'currency': coin,#'RUB',
        'follow': 'false',
        'haveTrade': 'false',
        'page': '1',
        'payMethod': payMethod,#' ',
        'tradeType': tradeType,#'SELL',
    }

    response = requests.get('https://p2p.mexc.com/api/market', params=params)

    r = response.json()

    data_mexc_p2p = []
    # print(r)
    for i in r['data']:
        # print(i['merchant']['nickName'], i['price'], 'Limit: ', i['minTradeLimit'], '-', i['maxTradeLimit'])
        print(i)

        #print(i['user']['user_name'], i['price'], 'Limit: ', i['limit_min'], '-' ,i['limit_max'])
        a = {'user': i['merchant']['nickName'], 'price': i['price'], 'min': i['minTradeLimit'], 'max': i['maxTradeLimit'], 'available': i['availableQuantity'], 'payMethod': i['payMethod'].split(',')}
        data_mexc_p2p.append(a)

    return data_mexc_p2p

def take_bank_metod_mexc(coin):
    params = {
        'currency': coin,#'RUB',
    }

    response = requests.get('https://p2p.mexc.com/api/payment/method', params=params,)

    r = response.json()

    data_mexc_metod = []
    for i in r['data']:
        # print(i['id'], i['nameEn'])
        print(i)
        try:
            a = {'id': i['id'], 'metod': i['nameEn']}
        except:
            a = {'id': i['id'], 'metod': i['name']}
        data_mexc_metod.append(a)
    return data_mexc_metod
#take_bank_metod_mexc()

def mexc_spot():
    params = {
        'symbols':'all'
    }
    response = requests.get('https://api.mexc.com/api/v3/ticker/price', params=params,)
    
    # print(response.json())
    data_mexc_spot = response.json()
    return data_mexc_spot
#mexc_spot()