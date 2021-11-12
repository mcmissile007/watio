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
        time_to_wake_up = _now.replace(
            hour=_hour, minute=_minute, second=0, microsecond=0
        )
        if _now > time_to_wake_up:
            return
        time.sleep(30)


def analyze(ree_prices: dict, name: str):
    """
    TODO
    """
    data_analysis = DataAnalysis()
    data_analysis.read_data_from_file(f"data/{name}.csv")
    prices = {key: float(value) for key, value in ree_prices.items()}

    results = [
        data_analysis.get_total_cost(prices, delay)
        for delay in range(0, len(prices.keys()))
    ]

    results = [result for result in results if result[1] > 0.0]
    results.sort(key=lambda x: x[1])

    return results


def send_results(_device: str, _results: list, number: int, _now: datetime):
    """
    TODO
    """
    message = f"Mejores horarios para {_device}:\r\n"
    option = 1
    for _datetime, _price in _results[:number]:
        str_time = _datetime.strftime("%H:%M")
        if _datetime.day == _now.day:
            message += f"{option}. Hoy  a las {str_time}h\r\n"
        else:
            message += f"{option}. Mañana a las {str_time}h\r\n"

        option += 1

    m_matrix = Matrix(
        MatrixPrivate.client_base_url,
        MatrixPrivate.media_base_url,
        MatrixPrivate.user_name,
        MatrixPrivate.password,
    )
    if m_matrix.login():
        m_matrix.room_id = MatrixPrivate().room_id
        m_matrix.send_message(message)


def main(programs: dict, _now: datetime):
    """
    TODO
    """
    while True:
        ree = DataAPIRee()
        ree_prices = ree.kwh_price(_now + timedelta(hours=1))
        if ree_prices:
            for description, name in programs.items():
                results = analyze(ree_prices, name)
                print(results)
                send_results(description, results, 12, _now)
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
        "lavadora o lavavajillas programa corto 1h": "WMAEGOKOPower1h40cel1000rpm",
    }
    print("start scheduler")

    TZ = pytz.timezone("Europe/Madrid")

    while True:  # run as a service always running
        wake_up_on_time(20, 30, TZ)
        main(PROGRAMS, datetime.now(tz=TZ))
        time.sleep(18 * 3600)

    # main(PROGRAMS, datetime.now(tz=TZ))

    print("end scheduler")
