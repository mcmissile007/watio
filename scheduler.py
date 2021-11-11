"""
TODO
"""

import sys
import getopt
import time
from datetime import datetime

import pytz
from data_api_ree import DataAPIRee
from data_analysis import DataAnalysis
from matrix import Matrix
from private.config import MatrixPrivate


def wake_up_on_time(_hour: int, _minute: int, timezone: pytz.timezone):
    """
    TODO
    """
    while True:
        _now = datetime(tz=timezone)
        _time = _now.replace(hour=_hour, minute=_minute, second=0, microsecond=0)
        if _now > time:
            return
        time.sleep(30)


def convert_float_to_time(_time: float) -> str:
    """
    TODO
    """
    hour = int(_time)
    if hour == 0:
        minutes = int(_time * 60)
        if minutes == 0:
            return "0:00h"
        return f"0:{minutes}"

    mod = _time % hour
    if mod == 0:
        return f"{hour}:00h"
    minutes = int(60 * mod)
    return f"{hour}:{minutes}h"


def analyze(ree_prices: dict, device: str):
    """
    TODO
    """
    data_analysis = DataAnalysis()
    data_analysis.read_data_from_file(f"data/{device}.csv")
    prices = {
        datetime.strptime(key, "%Y-%m-%d %H:%M").hour: float(value)
        for key, value in ree_prices.items()
    }
    data_analysis.get_total_cost(prices, 0.0)
    # delays = [x / 2 for x in range(0, 48, 1)]

    results = [
        (delay, data_analysis.get_total_cost(prices, delay)) for delay in range(0, 24)
    ]
    results = [result for result in results if result[1] > 0.0]
    results = list(map(lambda x: (convert_float_to_time(x[0]), x[1]), results,))
    results.sort(key=lambda x: x[1])

    return results


def send_results(_device: str, _results: list, number: int):
    """
    TODO
    """
    message = f"Mejores horarios para {_device}:\r\n"
    for result in _results[:number]:
        message += f"{result[0]}\r\n"
    print(message)
    m_matrix = Matrix(
        MatrixPrivate.client_base_url,
        MatrixPrivate.media_base_url,
        MatrixPrivate.user_name,
        MatrixPrivate.password,
    )
    if m_matrix.login():
        m_matrix.room_id = MatrixPrivate().room_id
        m_matrix.send_message(message)


def main(_devices: list, when: str):
    """
    TODO
    """
    while True:
        ree = DataAPIRee()
        if when == "tomorrow":
            ree_prices = ree.tomorrow_kwh_price()
        else:
            ree_prices = ree.today_kwh_price()
        if ree_prices:
            for device in _devices:
                print(device)
                results = analyze(ree_prices, device)
                send_results(device, results, 12)
                time.sleep(5)
            return
        time.sleep(300)


if __name__ == "__main__":

    DEVICES = {
        1: "DWBOSCHECO3h30m50cel",
        2: "WMAEGCotton30cel1000rpmEco",
        3: "WMAEGOKOPower1h40cel1000rpm",
        4: "WMAEG20min30cel1000rpm",
    }
    print("start scheduler")

    DEVICE_ID = "all"
    WHEN = "now"
    TZ = pytz.timezone("Europe/Madrid")

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "d:w:", longopts=["device=", "when="])

    except getopt.GetoptError as error:
        print(f"Error:{error}")
        sys.exit(2)

    for opt in opts:
        if opt[0] == "-d" or opt[0] == "--device":
            if opt[1].isnumeric():
                DEVICE_ID = int(opt[1])
        if opt[0] == "-w" or opt[0] == "--when":
            WHEN = opt[1]

    devices = []
    print(f"DEVICE_ID:{DEVICE_ID}")
    if DEVICE_ID == "all":
        devices = [device for key, device in DEVICES.items()]

    else:
        print(f"specific device: {DEVICE_ID}")
        if DEVICE_ID in DEVICES:
            devices = [DEVICES[DEVICE_ID]]

    if WHEN == "tomorrow":
        while True:  # run as a service always running
            wake_up_on_time(20, 30, TZ)
            main(devices, WHEN)
            time.sleep(18 * 3600)
    else:
        print(devices)
        main(devices, WHEN)

    print("end scheduler")
