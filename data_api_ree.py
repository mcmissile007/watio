"""
TODO
"""

# Red Electrica de España REData API
# https://www.ree.es/es/apidatos

# https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real?start_date=2021-09-22T00:00&end_date=2021-09-22T23:59&time_trunc=hour&geo_ids=8741

# very useful
# https://towardsdatascience.com/are-you-using-python-with-apis-learn-how-to-use-a-retry-decorator-27b6734c3e6


import decimal
from datetime import datetime
from datetime import timedelta
from typing import List
from https_requests import HTTPSRequest


class DataAPIRee:
    """
    TODO
    """

    def __init__(self):
        self.base_url = "https://apidatos.ree.es/es/datos"
        self.geo_ids = {
            "peninsula": 8741,
            "canarias": 8742,
            "baleares": 8443,
            "ceuta": 8744,
            "melilla": 8745,
        }

    def __convert_datetime(self, _datetime: str) -> str:
        """convert the complex ree datetime format to my simpler internal datetime format"""
        ree_datetime = datetime.strptime(_datetime, "%Y-%m-%dT%H:%M:%S.%f%z")
        # return datetime.strftime(ree_datetime, "%Y-%m-%d %H:%M")
        return ree_datetime

    def __convert_mwh_to_kwh(self, kwh_price: int) -> str:
        """convert Mwh price to Kwh price"""
        decimal.getcontext().prec = 4
        return str(decimal.Decimal(kwh_price) / decimal.Decimal(1000))

    def __parse_kwh_price_values(self, values: List[dict]) -> dict:
        return {
            self.__convert_datetime(v["datetime"]): self.__convert_mwh_to_kwh(
                v["value"]
            )
            for v in values
        }

    @staticmethod
    def __parse_kwh_price_response(response: dict) -> list:
        try:
            return response["included"][0]["attributes"]["values"]
        except KeyError as key_error:
            print(
                f"KeyError in kwh_price response:{key_error}. maybe not data in server yet"
            )
        except IndexError as index_error:
            print(
                f"IndexError in kwh_price response:{index_error}. maybe not data in server yet"
            )
        return []

    def __get_kwh_price(
        self, start_date: str, end_date: str, time_trunc="hour", geo="peninsula"
    ) -> dict:

        command = "mercados/precios-mercados-tiempo-real"
        if geo not in self.geo_ids:
            return {}

        query = f"?start_date={start_date}&end_date={end_date}\
                &time_trunc={time_trunc}&geo_ids={self.geo_ids[geo]}"
        url = f"{self.base_url}/{command}/{query}"
        kwh_prices_response = DataAPIRee.__parse_kwh_price_response(
            HTTPSRequest().get_request(url)
        )
        return self.__parse_kwh_price_values(kwh_prices_response)

    def today_kwh_price(self, geo="peninsula") -> dict:
        """
        TODO
        """
        print("getting today kwh price...")
        # YYYY-MM-DDTHH:MM ; T means local time
        today = datetime.now().strftime("%Y-%m-%d")
        start_date = f"{today}T00:00"
        end_date = f"{today}T23:59"
        return self.__get_kwh_price(start_date, end_date, geo=geo)

    def tomorrow_kwh_price(self, geo="peninsula") -> dict:
        """
        TODO
        """
        print("getting today kwh price...")
        # YYYY-MM-DDTHH:MM ; T means local time
        today = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = f"{today}T00:00"
        end_date = f"{today}T23:59"
        return self.__get_kwh_price(start_date, end_date, geo=geo)

    def kwh_price(self, _now: datetime, geo="peninsula") -> dict:
        """ 
        TODO
        """
        print("getting kwh price...")
        today = _now.strftime("%Y-%m-%d")
        tomorrow = (_now + timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = f"{today}T{_now.hour}:00"
        end_date = f"{tomorrow}T23:59"
        return self.__get_kwh_price(start_date, end_date, geo=geo)


if __name__ == "__main__":
    ree = DataAPIRee()
    prices = ree.kwh_price(datetime.now() - timedelta(days=1))
    print(f"prices:{prices}")
    for k in prices.keys():
        print(type(k))
