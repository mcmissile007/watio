import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

class HTTPSRequest():


    def __init__(self,total_retries = 3,backoff_factor = 2):

        allowed_methods = ["HEAD", "GET", "PUT",
                           "DELETE", "OPTIONS", "TRACE", "POST"]
        status_forcelist = [429, 500, 502, 503, 504]
        retries = Retry(total=total_retries, backoff_factor=backoff_factor,
                        status_forcelist=status_forcelist, allowed_methods=allowed_methods)
        self.adapter = HTTPAdapter(max_retries=retries)

    def get_request(self,url,timeout=2.0) -> dict:
        print(f"getting request: {url}")
        with requests.Session() as session:
            session.mount("https://", self.adapter)
            try:
                response = session.get(url,timeout = timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as errc:
                print(f"connection error {errc}")
            except requests.exceptions.Timeout as errt:
                print(f"timeout error: {errt}")
            except requests.exceptions.TooManyRedirects as errm:
                print(f"too many redirects error:{errm}")
            except requests.exceptions.HTTPError as errh:
                print(f"http error: {errh}")
            except requests.RequestException as err:
                print(f"generic requests error:{err}")
            except json.decoder.JSONDecodeError as errj:
                print(f"json decode error: {errj}")
            except Exception as e:
                print(f"exception: {e}")
        return {}
