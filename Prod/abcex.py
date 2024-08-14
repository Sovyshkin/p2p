from typing import Any, List, Dict, Optional
from pprint import pprint
import json
import time

import requests
from fake_useragent import UserAgent
from loguru import logger
from enum import StrEnum

# Actions (buy, sell)
class Actions(StrEnum):
    BUY = "buy"
    SELL = "sell"

class Abcex:
    def __init__(self,
        coin: str,
        fiat: str,
        email: str,
        password: str,
        action: Actions,
        price: str,
        logger: logger,
        bank: Optional[str] = None
    ) -> None:
        '''
        Args:
            coin (str): Coin symbol, like 'BTC'
            fiat (str): Fiat symbol, like 'RUB'
            email (str): Email for login
            password (str): Password for login
            action (Actions): Actions.BUY for buying, Actions.SELL for selling
            price (str): The amount of fiat desirebale for selling/buying coin
            logger (logger): Logger            
            bank (Optional[str]): Bank's id
        '''
        self.coin = coin
        self.fiat = fiat
        self.email = email
        self.password = password
        self.action = str(action)
        self.price = price
        self.bank = bank

        # Generating User Agent
        self.ua = UserAgent(os='windows').random
        # Logger
        self.logger = logger
        #self.logger.add(f"logs/abcex_{time.strftime('%H%M%S')}.log", format="[ {time} ] [ {level} ] [ {message} ]", rotation="50 MB")
        # Login (required)
        self.login()

    def login(self) -> None:
        '''
        Used for logging in and receiving token
        '''
        url = "https://abcex.io/api/v1/auth/login?lang=ru"
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Origin": "https://abcex.io",
            "Referer": "https://abcex.io/client/login",
            "User-Agent": self.ua,
            "X-Requested-With": "XMLHttpRequest"
        }
        params = {
            "username": self.email,
            "password": self.password,
            "auth2fa_code":"0000"
        }
        try:
            self.tokens = requests.post(url=url, headers=headers, json = params).json()
            if "token" not in self.tokens:
                raise ValueError("Token not found!")
            self.logger.debug("Token is received!")
        except Exception as e:
            err_msg = f"Failed to login Abcex: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)
            
    def get_banks(self) -> List[Dict[str, str]]:
        '''
        Used to retrive all available banks for selected fiat
        '''
        url = "https://abcex.io/api/v1/p2p/client/payment-method/list"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "authorization": f"Bearer {self.tokens['token']}",
            "Host": "abcex.io",
            "Referer": "https://abcex.io/client/p2p",
            "User-Agent": self.ua,
            "X-Requested-With": "XMLHttpRequest"
        }
        params = {
            "page": "1",
            "limit": "100",
            "lang": "ru"
        }
        try:
            return requests.get(url=url, headers=headers, params=params).json()['data']
        except Exception as e:
            err_msg = f"Failed to retrive banks list: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)

    def get_merchants(self) -> List[Dict[str, Any]]:
        '''
        Used to retrive the list of suitable merchants
        '''
        url = "https://abcex.io/api/v1/p2p/client/advertisement/list"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "authorization": f"Bearer {self.tokens['token']}",
            "Host": "abcex.io",
            "Referer": "https://abcex.io/client/p2p",
            "User-Agent": self.ua,
            "X-Requested-With": "XMLHttpRequest"
        }
        # There are some problems with price filtering: abcex don't give a f@ck on price filters
        # filter.minLimit: $gte:value
        # filter.maxLimit: $lte:value
        # filter.side: sell/buy
        # filter.paymentMethods.id:	$in:id1,id2
        # sortBy: price:ASC if sell/ price:DESC if buy
        params = {
            "filter.side": self.action,
            "filter.marketId": self.coin+self.fiat,
            "page": "1",
            "limit": "10",
            "lang": "ru"
        }
        if self.action == str(Actions.SELL):
            params["sortBy"] = "price:ASC"
        else:
            params["sortBy"] = "price:DESC"
        if self.bank:
            params["filter.paymentMethods.id"] = f"$in:{self.bank}"
        try:
            merchants = requests.get(url=url, headers=headers, params=params).json()['data']
        except Exception as e:
            err_msg = f"Failed to retrive merchants: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)
            
        def parse_p2p(merchant: dict) -> dict:
            try:
                return {
                    'price': merchant['price'],
                    'merchant': merchant['user']['username'],
                    'max': merchant['maxLimit'],
                    'min': merchant['minLimit'],
                    'banks': [bank['id'] for bank in merchant['paymentMethods']]
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
        # There are only two symbols at all: USDTRUB, USDTUSD
        symbols = ["USDTRUB", "USDTUSD"]
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "authorization": f"Bearer {self.tokens['token']}",
            "Host": "abcex.io",
            "Referer": "https://abcex.io/client/p2p",
            "User-Agent": self.ua,
            "X-Requested-With": "XMLHttpRequest"
        }
        try:
            symbols = requests.get("https://abcex.io/api/v1/markets/price-dynamics?lang=ru", headers=headers).json()
        except Exception as e:
            err_msg = f"Failed to get spot info: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)

        
        def get_pair(symbol: dict) -> Dict[str, Any]:
            return {'symbol': symbol['marketId'], 'price': symbol['price']}
        
        return [get_pair(symbol) for symbol in symbols]

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
        
        self.logger.success("Abcex report has successfuly been done") 
        return result


if __name__ == "__main__":
    # NOTE: Register fake account without 2FA and KYC to use with this script
    abcex = Abcex(
            coin = "USDT",
            fiat = "RUB",
            email = "your mail here",
            password = "your password here",
            action = Actions.BUY,
            price = "115",
        
    )
    with open("report.json", "w") as rep:
        rep.write(json.dumps(abcex.report(), indent=4))
