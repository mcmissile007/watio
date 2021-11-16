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


def wake_up_o_clock(timezone: pytz.timezone) -> datetime:
    """
    TODO
    """
    while True:
        _now = datetime.now(tz=timezone)
        if _now.minute == 0:
            return _now.replace(second=0, microsecond=0)
        time.sleep(10)


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


def better_times(ree_prices: dict, number: int):
    """
    TODO
    """
    prices = {key: float(value) for key, value in ree_prices.items()}
    prices = list(prices.items())
    prices.sort(key=lambda x: x[1])
    prices = [item[0] for item in prices]
    return prices[:number]


def worst_times(ree_prices: dict, number: int):
    """
    TODO
    """
    prices = {key: float(value) for key, value in ree_prices.items()}
    prices = list(prices.items())
    prices.sort(key=lambda x: x[1], reverse=True)
    prices = [item[0] for item in prices]
    return prices[:number]


def main(time_zone: pytz.timezone):
    """
    TODO
    """

    ree = DataAPIRee()
    ree_prices = ree.kwh_price(datetime.now(tz=time_zone) + timedelta(hours=1))
    print(ree_prices)
    if ree_prices:
        switch_on_times = better_times(ree_prices, 12)
        print(switch_on_times)
        switch_off_times = worst_times(ree_prices, 12)
        print(switch_off_times)
        while True:
            now = wake_up_o_clock(time_zone)
            if now in switch_on_times:
                print("switch on heater")
            if now in switch_off_times():
                print("switch off heater")
            if now.hour == 20:
                print("it is time to start again with new prices")
                return
            time.sleep(60)


if __name__ == "__main__":

    print("start optimizer")
    TZ = pytz.timezone("Europe/Madrid")
    while True:  # run as a service always running
        print("It is time to update prices")
        wake_up_on_time(20, 40, TZ)
        main(TZ)
    print("end optimizer")
