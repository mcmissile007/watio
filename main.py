from data_api_ree import DataAPIRee
from mongodb import MongoDB
from zway import ZWayConf, ZWayvDevAPI
from private.config import ZWayPrivate
import time
import csv
import sys, select

def test_data_api_ree():
    api_ree = DataAPIRee()
    print (api_ree.today_kwh_price())


def test_zway_api():
    zway = ZWayvDevAPI(ZWayConf.url,ZWayConf.port,
                        ZWayPrivate.user,ZWayPrivate.password)
    
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


def test_save_info():
    zway = ZWayvDevAPI(ZWayConf.url,ZWayConf.port,
                        ZWayPrivate.user,ZWayPrivate.password)
    zway.sensor_update(ZWayConf.house_electric_meter)
    time.sleep(4)
    info = zway.sensor_meter_info(ZWayConf.house_electric_meter)
    print (f"info:{info}")
    with MongoDB() as mongodb:
         mongodb.insert("test1",info)


def save_info_process(name:str ,interval:int ) -> None:

    data = []
    zway = ZWayvDevAPI(ZWayConf.url,ZWayConf.port,
                        ZWayPrivate.user,ZWayPrivate.password)
                        
    with MongoDB() as mongodb:
        while True:
            zway.sensor_update(ZWayConf.house_electric_meter)
            print ("press enter to finish:")
            input, _output, _excep = select.select([sys.stdin],[],[],interval)
            if (input):
                break

            info = zway.sensor_meter_info(ZWayConf.house_electric_meter)
            print (f"info:{info}")
            mongodb.insert(name,info)
            data.append(info)
    if data:
        with open(f"data/{name}.csv","w") as f:
            w = csv.DictWriter(f,fieldnames=data[0].keys())
            w.writeheader()
            w.writerows(data)

def load_data_from_mongodb (collection):
    data = []
    with MongoDB() as mongodb:
         data = mongodb.read_collection(collection)
    if data:
            with open(f"data/generate_{collection}.csv","w") as f:
                w = csv.DictWriter(f,fieldnames=data[0].keys())
                w.writeheader()
                w.writerows(data)



def main () -> None:
    print("profesor watio main starting...")
    #test_data_api_ree()
    #test_zway_api()
    #test_save_info()
    measurement = ""
    save_info_process(measurement,interval = 10)
    #load_data_from_mongodb(measurement)


    print("profesor watio main ended...")

if __name__ == "__main__":
    main()
   