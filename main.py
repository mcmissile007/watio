from data_api_ree import DataAPIRee
from zway import ZWayConf, ZWayvDevAPI
from private.config import Config as Private
import time


def test_data_api_ree():
    api_ree = DataAPIRee()
    print (api_ree.today_kwh_price())


def test_zway_api():
    zway = ZWayvDevAPI(ZWayConf.url,ZWayConf.port,
                        Private.zwaveme_username,Private.zwaveme_password)
    
    zway.switch_off(ZWayConf.hall_light)
    time.sleep(10)
    
    zway.switch_on(ZWayConf.hall_light)
    time.sleep(10)
    zway.sensor_update(ZWayConf.hall_light_electric_meter)
    time.sleep(10)
    level = zway.sensor_meter_level(ZWayConf.hall_light_electric_meter)
    print (f"level:{level} w")

    time.sleep(5)
    zway.sensor_update(ZWayConf.house_electric_meter)
    time.sleep(10)
    level = zway.sensor_meter_level(ZWayConf.house_electric_meter)
    print (f"level:{level} w")




def main () -> None:
    print("profesor watio main starting...")
    test_data_api_ree()
    test_zway_api()
    print("profesor watio main ended...")

if __name__ == "__main__":
    main()
   