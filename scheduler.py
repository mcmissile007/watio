"""
TODO
"""

import time
from datetime import datetime
from datetime import timedelta

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
        _now = datetime.now(tz=timezone)
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


def analyze(ree_prices: dict, name: str):
    """
    TODO
    """
    data_analysis = DataAnalysis()
    data_analysis.read_data_from_file(f"data/{name}.csv")
    prices = {key: float(value) for key, value in ree_prices.items()}
    # print(prices)

    # delays = [x / 2 for x in range(0, 48, 1)]
    print(prices.keys())

    for k in prices.keys():
        print(k)

    results = [
        (delay, data_analysis.get_total_cost(prices, delay))
        for delay in range(0, len(prices.keys()))
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
    # m_matrix = Matrix(
    #     MatrixPrivate.client_base_url,
    #     MatrixPrivate.media_base_url,
    #     MatrixPrivate.user_name,
    #     MatrixPrivate.password,
    # )
    # if m_matrix.login():
    #     m_matrix.room_id = MatrixPrivate().room_id
    #     m_matrix.send_message(message)


def main(programs: dict, _now: datetime):
    """
    TODO
    """
    while True:
        ree = DataAPIRee()
        ree_prices = ree.kwh_price(_now + timedelta(hours=1))
        if ree_prices:
            for description, name in programs.items():
                print(description)
                results = analyze(ree_prices, name)
                send_results(description, results, 12)
                time.sleep(5)
            return
        time.sleep(300)


if __name__ == "__main__":

    # PROGRAMS = {
    #     "lavavajillas programa largo ECO 3h30m": "DWBOSCHECO3h30m50cel",
    #     "lavavajillas programa corto 1h": "DWBOSCH1h65cel",
    #     "lavadora programa largo ECO 2h30": "WMAEGCotton30cel1000rpmEco",
    #     "lavadora programa corto 1h": "WMAEGOKOPower1h40cel1000rpm",
    #     "lavadora programa rapido 20min": "WMAEG20min30cel1000rpm",
    # }

    PROGRAMS = {
        "lavavajillas programa largo 3h": "DWBOSCHECO3h30m50cel",
        "lavavajillas o lavadora programa corto 1h": "WMAEGOKOPower1h40cel1000rpm",
    }
    print("start scheduler")

    TZ = pytz.timezone("Europe/Madrid")

    # while True:  # run as a service always running
    #     wake_up_on_time(20, 30, TZ)
    #     main(PROGRAMS, datetime.now(tz=TZ))
    #     time.sleep(18 * 3600)

    main(PROGRAMS, datetime.now(tz=TZ))

    print("end scheduler")
