"""
TODO
"""


import csv
import sys
import getopt
import signal
import time
from datetime import datetime
import pytz
from mongodb import MongoDB
from zway import ZWayConf, ZWayvDevAPI
from private.config import ZWayPrivate


class Meter:
    """
    TODO
    """

    def __init__(self, name, time_zone):
        self.run = True
        self.name = name
        self.time_zone = time_zone
        self.data = []
        signal.signal(signal.SIGTERM, self.__signal_term_handler)
        signal.signal(signal.SIGINT, self.__signal_int_handler)
        signal.signal(signal.SIGTSTP, self.__signal_tstp_handler)

    def __signal_term_handler(self, _signal, _frame):
        self.run = False
        print("got SIGTERM:15")
        self.__save_data_to_file(self.name)
        sys.exit(0)

    def __signal_int_handler(self, _signal, _frame):
        self.run = False
        print("got SIGINT:2")
        self.__save_data_to_file(self.name)
        sys.exit(0)

    def __signal_tstp_handler(self, _signal, _frame):
        self.run = False
        print("got SIGTSTP:20")
        self.__save_data_to_file(self.name)
        sys.exit(0)

    def __save_data_to_file(self, file_name: str):

        if self.data:
            with open(f"data/{file_name}.csv", "w") as _file:
                writer = csv.DictWriter(_file, fieldnames=self.data[0].keys())
                writer.writeheader()
                writer.writerows(self.data)

    def save_info_process(self, device: str, interval: int, stop_end_of_day: bool):
        """
            TODO
        """
        zway = ZWayvDevAPI(
            ZWayConf.url, ZWayConf.port, ZWayPrivate.user, ZWayPrivate.password
        )
        with MongoDB() as mongodb:
            while self.run:
                zway.sensor_update(device)
                time.sleep(interval)
                info = zway.sensor_meter_info(device, self.time_zone)
                print(f"info:{info}")
                mongodb.insert(self.name, info)
                self.data.append(info)
                if stop_end_of_day:
                    now = datetime.now(tz=self.time_zone)
                    if now.hour == 23 and now.minute == 59:
                        print("End of day, terminating...")
                        filename = f"{self.name}_{now.day}_{now.month}_{now.year}"
                        self.__save_data_to_file(filename)
                        self.run = False

    @staticmethod
    def load_data_from_mongodb(collection):
        """
            TODO
        """
        data = []
        with MongoDB() as mongodb:
            data = mongodb.read_collection(collection)
        if data:
            with open(f"data/generate_{collection}.csv", "w") as filename:
                writer = csv.DictWriter(filename, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)


if __name__ == "__main__":
    print("profesor watio main starting...")
    DEVICES = {
        17: ZWayConf.house_electric_meter,
        18: ZWayConf.hall_light_electric_meter,
        15: ZWayConf.water_heater_electric_meter,
    }
    NAME = ""
    DEVICE_ID = 0
    TIME = "now"
    TZ = pytz.timezone("Europe/Madrid")
    # main = Main(NAME)
    # main.save_info_process(DEVICES[0], interval=10)
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            argv, "n:d:t:", longopts=["name=", "device=", "time="]
        )

    except getopt.GetoptError as error:
        print(f"Error:{error}")
        sys.exit(2)

    for opt in opts:
        if opt[0] == "-n" or opt[0] == "--name":
            NAME = opt[1]
        if opt[0] == "-d" or opt[0] == "--device":
            DEVICE_ID = int(opt[1])
        if opt[0] == "-t" or opt[0] == "--time":
            TIME = opt[1]

    if NAME == "":
        print("Invalid name")
        sys.exit(2)

    if DEVICE_ID not in DEVICES:
        print("Device ID does not exist")
        sys.exit(2)

    meter = Meter(NAME, TZ)
    if TIME == "day":
        while True:
            time.sleep(10)
            print("waiting to start at 0:00")
            __now = datetime.now(tz=TZ)
            print(__now)
            if __now.hour == 0 and __now.minute == 0:
                print("It is time to start")
                meter.save_info_process(DEVICES[DEVICE_ID], 10, True)
    elif TIME == "now":
        meter.save_info_process(DEVICES[DEVICE_ID], 10, False)
    else:
        print("time option not valid")

    print("profesor watio main ended...")
