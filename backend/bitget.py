from typing import Any, List, Dict, Optional
from pprint import pprint
import json
import time

import requests
from fake_useragent import UserAgent
from enum import IntEnum
from loguru import logger

# Actions (buy, sell)
class Actions(IntEnum):
    BUY = 1
    SELL = 2

class BitGet:
    def __init__(self,
        coin: str,
        fiat: str,
        action: Actions,
        price: str,
        logger: logger,
        bank: Optional[str] = None,
    ) -> None:
        '''
        Args:
            coin (str): Coin symbol, like 'BTC'
            fiat (str): Fiat symbol, like 'RUB'
            action (Actions): Actions.BUY for buying, Actions.SELL for selling
            price (str): The amount of fiat desirebale for selling/buying coin
            logger (logger): Logger
            bank (Optional[str]): Bank's id
        '''
        self.coin = coin
        self.fiat = fiat
        self.action = str(action)
        self.price = price
        self.bank = bank

        # Generating User Agent
        self.ua = UserAgent(os='windows').random
        # Logger
        self.logger = logger
        #self.logger.add(f"logs/bitget_{time.strftime('%H%M%S')}.log", format="[ {time} ] [ {level} ] [ {message} ]", rotation="50 MB")

    def get_banks(self) -> List[Dict[str, str]]:
        '''
        Used to retrive all available banks for selected fiat
        '''
        url = "https://www.bitget.com/v1/p2p/pub/currency/queryAllCoinAndFiat"
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "locale": "ru_RU",
            "language": "ru_RU",
            "Origin": "https://www.bitget.com",
            "Referer": "https://www.bitget.com/p2p-trade",
            "User-Agent": self.ua,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        params = {
            "languageType": "6"
        }
        
        banks = []
        try:
            raw_data = requests.post(url=url, headers=headers, data=params).json()['data']['fiatInfoRespList']
        except Exception as e:
            err_msg = f"Failed to retrive banks list: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)
        for fiat in raw_data:
            if fiat['fiatCode'] == self.fiat:
                for bank in fiat['paymethodInfo']:
                    banks.append({'id': bank['paymethodId'], 'name': bank['paymethodName']})
        return banks

    def get_merchants(self) -> List[Dict[str, Any]]:
        '''
        Used to retrive the list of suitable merchants
        '''
        url = "https://www.bitget.com/v1/p2p/pub/adv/queryAdvList"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=utf-8",
            "locale": "ru_RU",
            "language": "ru_RU",
            "Host": "www.bitget.com",
            "Origin": "https://www.bitget.com",
            "User-Agent": self.ua
        }
        params = {
            "price": self.price, 
            "coinCode": self.coin,
            "fiatCode": self.fiat,
            "pageNo": "1",
            "pageSize": "10",
            "side": self.action,
            "languageType": "6"
        }
        if self.bank:
            params["paymethodId"] = self.bank
        try:
            merchants = requests.post(url=url, headers=headers, json = params).json()['data']['dataList']
        except Exception as e:
            err_msg = f"Failed to retrive merchants: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)
            
        def parse_p2p(merchant: dict) -> dict:
            try:
                return {
                    'price': merchant['price'],
                    'merchant': merchant['nickName'],
                    'max': merchant['maxAmount'],
                    'min': merchant['minAmount'],
                    'banks': [bank['paymethodId'] for bank in merchant['paymethodInfo']]
                }
            except Exception as e:
                err_msg = f"Failed to parse merchant due to error: {e}"
                self.logger.error(err_msg)
                raise ValueError(err_msg)


        return list(map(parse_p2p, merchants))

    def get_spot(self) -> List[Any]:
        '''
        Used to retrive all pairs and their last prices for symbol
        '''
        def get_price(symbol: str) -> str:
            try:
                data = requests.get("https://api.bitget.com/api/v2/spot/market/tickers", params={'symbol': symbol}).json()
                return data['data'][0]['lastPr']
            except Exception as e:
                err_msg = f"[!] Failed to get price for {symbol} symbol: {e}"
                self.logger.error(err_msg)
                raise ValueError(err_msg)

        def get_pair(symbol: dict, base: str) -> Optional[Dict]:
            if symbol['baseCoin'] == base:
                return {'symbol': symbol['symbol'], 'price': get_price(symbol['symbol'])}
        
        try:
            raw_data = requests.get("https://api.bitget.com/api/v2/spot/public/symbols").json()['data']
        except Exception as e:
            err_msg = f"Failed to get spot info: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)
        return [pair for symbol in raw_data if (pair := get_pair(symbol, self.coin)) is not None]

    def report(self) -> Dict:
        result = {}
        # Receiving banks
        try:
            result['banks'] = self.get_banks()
        except Exception as e:
            err_msg = f"Failed to create report - problems with banks list: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)
        # Receiving merchants
        try:
            result['merchants'] = self.get_merchants()
        except Exception as e:
            err_msg = f"Failed to create report - problems with merchants list: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)
        # Receiving spot
        try:
            result['spot'] = self.get_spot()
        except Exception as e:
            err_msg = f"Failed to create report - problems with spot info: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)
        self.logger.success("BitGet report has successfuly been done") 
        return result




