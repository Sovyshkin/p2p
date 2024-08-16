from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, make_response
import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta
from loguru import logger
import sqlite3
import requests
import time
import json
from time import sleep
from take_bybit import *
from take_kucoin import *
from take_mexc import *
from take_bitpapa import *
from flask_cors import CORS, cross_origin
# Bitget
from bitget import BitGet, Actions as BitGetActions
# Abcex
from abcex import Abcex, Actions as AbcexActions
# BingX
from bingx import BingX, Actions as BingXActions

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Создание лога
logger.add(f"logs/{time.strftime('%H%M%S')}.log", format="[ {time} ] [ {level} ] [ {message} ]", rotation="50 MB")

@app.route('/login', methods=['POST'])
def login() -> json:

    result = {}
    data = request.get_json()
    login = str(data['params']['login']) 
    password = str(data['params']['password']) 
    # print(login,password)

    if str(login) == 'admin@crypto' and str(password) == 'admin_crypto481':
        result['status'] = '200'
        result['message'] = 'Успешно'
        return jsonify(result)
    
    else:
        result['status'] = '400'
        result['message'] = 'Ошибка авторизации'
        return jsonify(result)

    
@app.route('/admin', methods=['POST'])
def admin()-> json:
    #настройки по умолчанию: покупка, usdt за  рубли, без заполнения количества, все методы оплаты
    data = request.get_json()
    #Выбор из какой монеты в какую валюту
    tokenId = str(data['params']['tokenId'])#None #должно предоваться 'USDT' если ничего не выбранно 
    currencyId = str(data['params']['currencyId']) #должно предоваться "RUB" если ничего не выбранно 

    #Получение доступных методов оплаты (банки):
    only_pays = take_payment_only(tokenId, currencyId) # это отсеивает те банки, которые подходят
    name_banks = take_metods(only_pays) # это записывает id которое потребуется при подборе price_list

    amount = str(data['params']['amount'])#'' #'20000'
    paymant = data['params']['paymant']#[] #тут ['7']
    banks = data['params']['name_banks']
    side = str(data['params']['side'])#'0' #продажа 1-покупкаs


    price_list = take_byb(tokenId, amount, currencyId, paymant, side)

    # print(price_list)
    result = {}
    result['price_byb'] = price_list
    result['only_code_bank_bybit'] = name_banks 

    coin = currencyId 
    symbol = tokenId
    type_c = side

    code_bank = ''#тут нужно будет поправить так как по другому у банков id 

    name_banks_kuc = take_code_bank(coin)
    price_list_kuc = parce_cucoin(symbol, coin, type_c, code_bank)

    paymetod_mexc =  take_bank_metod_mexc(coin)
    if side:
        tradeType = 'BUY'
        # Покупка для BitGet, Abcex, BingX
        bitget_action = BitGetActions.BUY
        abcex_action = AbcexActions.BUY
        bingx_action = BingXActions.BUY
    else:
        tradeType = 'SELL'
        # Продажа для BitGet, Abcex, BingX
        bitget_action = BitGetActions.SELL
        abcex_action = AbcexActions.SELL
        bingx_action = BingXActions.SELL


    price_list_mexc_bitpapa = parce_bitpapa(side, amount, currencyId, tokenId, banks)
    spot_bitpapa = bitpapa_spot()
    price_list_mexc_p2p = take_p2p_mexc(amount, tokenId, coin, paymant, tradeType)
    spot_mexc = mexc_spot()

    # BitGet
    bitget = BitGet(
        coin = symbol,
        fiat = coin,
        price = amount,
        action = bitget_action,
        logger = logger
        # bank = добавить позже
    )

    # Получение отчёта от BitGet
    try_count = 0
    bitget_report = {}
    # Если все попытки получения закончились неудачно - возвращается пустой словарь
    while try_count < 3:
        try:
            bitget_report = bitget.report()
        except Exception as e:
            try_count += 1
            time.sleep(1)
            if try_count == 3:
                print(f"[!] BitGet info can not be received: {e}")
        else:
            break

    # Abcex
    abcex = Abcex(
        email = "anna.aleks491@gmail.com",
        password = "CodeRed_491",
        coin = symbol,
        fiat = coin,
        price = amount,
        action = abcex_action,
        logger = logger
        # bank = добавить позже
    )

    # Получение отчёта от Abcex
    try_count = 0
    abcex_report = {}
    # Если все попытки получения закончились неудачно - возвращается пустой словарь
    while try_count < 3:
        try:
            abcex_report = abcex.report()
        except Exception as e:
            try_count += 1
            time.sleep(1)
            if try_count == 3:
                print(f"[!] Abcex info can not be received: {e}")
        else:
            break

    # Получение отчёта от BingX
    bingx_report = {}
    if symbol == "USDT":
        bingx = BingX(
            api_key= "",
            secret = "",
            fiat = coin,
            action = bingx_action,
            price = float(amount) 
        )
        def get_bingx_report(bingx: BingX) -> Dict[str, Any]:
            try:
                bingx.setup_playwright()
                report = bingx.report()
                bingx.stop()
                return report
            except Exception as e:
                print(f"[!] BingX info can not be received: {e}")
        
        bingx_report = get_bingx_report(bingx)
        if bingx_report is None:
            bingx_report = {}

    result['price_kuc'] = price_list_kuc
    result['only_code_bank_kuc'] = name_banks_kuc
    result['paymetod_mexc'] = paymetod_mexc
    result['price_list_mexc_p2p'] = price_list_mexc_p2p
    result['price_list_mexc_bitpapa'] = price_list_mexc_bitpapa
    result['bitget'] = bitget_report
    result['abcex'] = abcex_report
    result['bingx'] = bingx_report

    return jsonify(result)

@app.route('/spot', methods=['POST'])
def spot()-> json:
    result = {}
    from pprint import pprint
    #data = request.get_json()
    #pprint(data)
    # BitGet
    bitget = BitGet(
        coin = "USDT",
        fiat = "RUB",
        price = "91",
        action = BitGetActions.BUY,
        logger = logger
        # bank = добавить позже
    )

    # Получение отчёта от BitGet
    try_count = 0
    bitget_report = {'spot': {}}
    # Если все попытки получения закончились неудачно - возвращается пустой словарь
    while try_count < 3:
        try:
            bitget_report = bitget.report()
        except Exception as e:
            try_count += 1
            time.sleep(1)
            if try_count == 3:
                print(f"[!] BitGet info can not be received: {e}")
        else:
            break

    # Abcex
    abcex = Abcex(
        email = "anna.aleks491@gmail.com",
        password = "CodeRed_491",
        coin = "USDT",
        fiat = "RUB",
        price = "91",
        action = AbcexActions.BUY,
        logger = logger
        # bank = добавить позже
    )

    # Получение отчёта от Abcex
    try_count = 0
    abcex_report = {'spot': {}}
    # Если все попытки получения закончились неудачно - возвращается пустой словарь
    while try_count < 3:
        try:
            abcex_report = abcex.report()
        except Exception as e:
            try_count += 1
            time.sleep(1)
            if try_count == 3:
                print(f"[!] Abcex info can not be received: {e}")
        else:
            break

    # Получение отчёта от BingX
    bingx = BingX(
        api_key= "",
        secret = "",
        fiat = "RUB",
        action = BingXActions.BUY,
        price = 91.0 
    )
    def get_bingx_report(bingx: BingX) -> Dict[str, Any]:
        try:
            bingx.setup_playwright()
            report = bingx.report()
            bingx.stop()
            return report
        except Exception as e:
            print(f"[!] BingX info can not be received: {e}")

    
    bingx_report = get_bingx_report(bingx)
    if bingx_report is None:
        bingx_report = {'spot': {}}
    result['bitpapa'] = bitpapa_spot()
    result['bitget'] = bitget_report
    result['bingx'] = bingx_report
    result['abcex'] = abcex_report
    result['mexc'] = [{'price': item['price'], 'symbol': item['symbol']} for item in mexc_spot()][:10] 
    result['bybit'] =  take_spot_bybit()
    result['kucoin'] = [{'price': item['price'], 'symbol': item['symbol']} for item in kukoin_spot()][:10]
    return jsonify(result)



if __name__ == '__main__':
   app.run(host="0.0.0.0", debug=True, port=3000)
