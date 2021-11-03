"""
TODO
"""
from datetime import datetime
import pytz
from https_requests import HTTPSRequest


class ZWayConf:
    """
    TODO
    """

    url = "192.168.1.118"
    port = 8083
    hall_light = "ZWayVDev_zway_18-0-37"
    hall_light_electric_meter = "ZWayVDev_zway_18-0-50-2"
    water_heater_electric_meter = "ZWayVDev_zway_15-0-50-2"
    house_electric_meter = "ZWayVDev_zway_17-0-50-2"


class ZWayvDevAPI:
    """
    TODO
    """

    def __init__(self, ip, port, username, password):
        self.username = username
        self.password = password
        self.base_url = f"http://{ip}:{port}/ZAutomation/api/v1/devices/"

    @staticmethod
    def __parse_sensor_meter_level(response) -> float:
        try:
            return float(response["data"]["metrics"]["level"])
        except KeyError as error:
            print(f"KeyError in sensor_meter_response:{error}")
        except IndexError as error:
            print(f"IndexError in sensor_meter_response:{error}")
        return -1.0

    @staticmethod
    def __parse_sensor_meter_info(response, time_zone: pytz.timezone) -> dict:
        info = {}
        try:
            info["level"] = float(response["data"]["metrics"]["level"])
            info["unit"] = str(response["data"]["metrics"]["scaleTitle"])
            info["title"] = str(response["data"]["metrics"]["title"])
            info["ts"] = datetime.fromtimestamp(
                int(response["data"]["updateTime"]), tz=time_zone
            )
            info["epoch"] = int(info["ts"].strftime("%s"))
            return info
        except KeyError as error:
            print(f"KeyError in sensor_meter_response:{error}")
        except IndexError as error:
            print(f"IndexError in sensor_meter_response:{error}")
        return info

    def sensor_meter_level(self, device: str) -> float:
        """
        TODO
        """
        http = HTTPSRequest(total_retries=0, backoff_factor=0)
        url = self.base_url + device
        response = http.get_basic_auth_request(url, self.username, self.password)
        # pprint(response)
        return ZWayvDevAPI.__parse_sensor_meter_level(response)

    def sensor_meter_info(self, device: str, time_zone: pytz.timezone) -> dict:
        """
        TODO
        """
        http = HTTPSRequest(total_retries=0, backoff_factor=0)
        url = self.base_url + device
        response = http.get_basic_auth_request(url, self.username, self.password)
        # pprint(response)
        return ZWayvDevAPI.__parse_sensor_meter_info(response, time_zone)

    def sensor_update(self, device: str) -> None:
        """
        TODO
        """
        http = HTTPSRequest(total_retries=0, backoff_factor=0)
        url = self.base_url + device + "/command/update"
        response = http.get_basic_auth_request(url, self.username, self.password)
        print(response)

    def __switch_update(self, device: str, state: str) -> None:
        """
        TODO
        """
        http = HTTPSRequest(total_retries=0, backoff_factor=0)
        url = self.base_url + device + "/command/" + state
        response = http.get_basic_auth_request(url, self.username, self.password)
        print(response)

    def switch_on(self, device: str) -> None:
        """
        TODO
        """
        self.__switch_update(device, "on")

    def switch_off(self, device: str) -> None:
        """
        TODO
        """
        self.__switch_update(device, "off")
