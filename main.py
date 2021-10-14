from data_api_ree import DataAPIRee
from zwaveme import ZWaveMe

def main () -> None:
    print("profesor watio main starting...")
    api_ree = DataAPIRee()
    print (api_ree.today_kwh_price())
    #now insert in mongodb

    zwaveme = ZWaveMe("admin",".HuSTr3pMq7aA!")
    level = zwaveme.sensor_meter_level("ZWayVDev_zway_18-0-50-2")
    print (f"level:{level}")


if __name__ == "__main__":
    main()