from typing import get_type_hints
from https_requests import HTTPSRequest

class ZWaveMe():
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.base_url = "http://192.168.1.118:8083/ZAutomation/api/v1/devices/"

    def __parse_sensor_meter_level_response(self,response) -> float:
        try:
            return float(response['data']['metrics']['level'])
        except KeyError as ke:
            print(f"KeyError in sensor_meter_response:{ke}")
        except IndexError as ie:
            print(f"IndexError in sensor_meter_response:{ie}")
        except Exception as e:
            print(f"Exception in sensor_meter_response:{e}")
        return -1.0


    def sensor_meter_level(self,device: str) -> dict:
        http = HTTPSRequest(total_retries=0,backoff_factor=0)
        url = self.base_url + device
        response = http.get_basic_auth_request(url,self.username,self.password)
        return self.__parse_sensor_meter_level_response(response)
        

    
