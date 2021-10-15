from typing import get_type_hints
from https_requests import HTTPSRequest
from dataclasses import dataclass

@dataclass
class ZWayConf():
    url = "192.168.1.118"
    port = 8083
    hall_light = "ZWayVDev_zway_18-0-37"
    hall_light_electric_meter = "ZWayVDev_zway_18-0-50-2"
    water_heater_electric_meter = "ZWayVDev_zway_15-0-50-2"
    house_electric_meter = "ZWayVDev_zway_17-0-50-2"

class ZWayvDevAPI():
    def __init__(self,ip,port,username,password):
        self.username = username
        self.password = password
        self.base_url = f"http://{ip}:{port}/ZAutomation/api/v1/devices/"

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
    
    def sensor_update(self,device: str) -> None:
        http = HTTPSRequest(total_retries=0,backoff_factor=0)
        url = self.base_url + device + "/command/update"
        response = http.get_basic_auth_request(url,self.username,self.password)
        print(response)

    def __switch_update(self,device :str, state: str) -> None:
        http = HTTPSRequest(total_retries=0,backoff_factor=0)
        url = self.base_url + device + "/command/" + state
        response = http.get_basic_auth_request(url,self.username,self.password)
        print(response)


    def switch_on(self,device: str) -> None:
        self.__switch_update(device,"on")
        

    def switch_off(self,device: str) -> None:
        self.__switch_update(device,"off")

    
