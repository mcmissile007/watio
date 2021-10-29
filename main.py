"""
TODO
"""


import csv
import sys
import select
import signal

from mongodb import MongoDB
from zway import ZWayConf, ZWayvDevAPI
from private.config import ZWayPrivate


class Main:
    """
    TODO
    """

    def __init__(self, name):
        self.run = True
        self.name = name
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

    def save_info_process(self, interval: int):
        """
            TODO
        """
        zway = ZWayvDevAPI(
            ZWayConf.url, ZWayConf.port, ZWayPrivate.user, ZWayPrivate.password
        )
        with MongoDB() as mongodb:
            while self.run:
                zway.sensor_update(ZWayConf.house_electric_meter)
                print("press enter to finish:")
                _input, _output, _excep = select.select([sys.stdin], [], [], interval)
                if _input:
                    self.__save_data_to_file(self.name)
                    break

                info = zway.sensor_meter_info(ZWayConf.house_electric_meter)
                print(f"info:{info}")
                mongodb.insert(self.name, info)
                self.data.append(info)

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
    main = Main("test2")
    main.save_info_process(interval=10)
    print("profesor watio main ended...")
