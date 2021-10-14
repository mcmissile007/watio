# Red Electrica de España REData API
# https://www.ree.es/es/apidatos

# https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real?start_date=2021-09-22T00:00&end_date=2021-09-22T23:59&time_trunc=hour&geo_ids=8741

#very useful
#https://towardsdatascience.com/are-you-using-python-with-apis-learn-how-to-use-a-retry-decorator-27b6734c3e6



from datetime import datetime
import decimal
from https_requests import HTTPSRequest
from pprint import pprint
from typing import List
from decimal import *

class DataAPIRee ():

    def __init__(self):
        self.base_url = "https://apidatos.ree.es/es/datos"
        self.geo_ids = {"peninsula": 8741, "canarias": 8742,
                        "baleares": 8443, "ceuta": 8744, "melilla": 8745}

    def __convert_datetime(self,_datetime:str) -> str:
        '''convert the complex ree datetime format to my simpler internal datetime format'''
        ree_datetime = datetime.strptime(_datetime,"%Y-%m-%dT%H:%M:%S.%f%z")
        return  datetime.strftime(ree_datetime,"%Y:%m:%d %H:%M")
    
    def __convert_Mwh_to_Kwh(self,kwh_price:int) -> str:
        '''convert Mwh price to Kwh price'''
        getcontext().prec = 4
        return str(Decimal(kwh_price) / Decimal(1000))
        

    def __parse_kwh_price_values(self,values:List[dict]) -> List[dict]:
        return [{'datatime':self.__convert_datetime(v['datetime']),
             'price':self.__convert_Mwh_to_Kwh(v['value'])} for v in values]
        
    def __parse_kwh_price_response(self,response: dict)->list:
        try:
            return response['included'][0]['attributes']['values']
        except KeyError as ke:
            print(f"KeyError in kwh_price response:{ke}")
        except IndexError as ie:
            print(f"IndexError in kwh_price response:{ie}")
        except Exception as e:
            print(f"Exception in kwh_price response:{e}")
        return []
        
    def __get_kwh_price(self, start_date: str, end_date: str, time_trunc="hour", geo="peninsula") -> list:
        command = "mercados/precios-mercados-tiempo-real"
        if geo not in self.geo_ids:
            return []
        
        query = f"?start_date={start_date}&end_date={end_date}&time_trunc={time_trunc}&geo_ids={self.geo_ids[geo]}"
        url = f"{self.base_url}/{command}/{query}"
        kwh_prices_response = self.__parse_kwh_price_response(HTTPSRequest().get_request(url))
        return self.__parse_kwh_price_values(kwh_prices_response)
        

    def get_today_kwh_price(self, geo="peninsula") -> None:
        print("getting today kwh price...")
        # YYYY-MM-DDTHH:MM ; T means local time
        today = datetime.now().strftime("%Y-%m-%d")
        start_date = f"{today}T00:00"
        end_date = f"{today}T23:59"
        return self.__get_kwh_price(start_date, end_date, geo=geo)
