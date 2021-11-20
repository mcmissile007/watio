"""
TODO
"""
import logging
import os
import time
from datetime import datetime
from datetime import timedelta

import pytz
from data_api_ree import DataAPIRee
from matrix import Matrix
from private.config import ZWayPrivate, MatrixPrivate
from zway import ZWayConf, ZWayvDevAPI


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


def send_message(message):
    """
    TODO
    """
    m_matrix = Matrix(
        MatrixPrivate.client_base_url,
        MatrixPrivate.media_base_url,
        MatrixPrivate.user_name,
        MatrixPrivate.password,
        MatrixPrivate.room_id,
    )
    if m_matrix.login():
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


def better_times_slot(ree_prices: dict, number: int):
    """
    TODO
    """

    prices = {key: float(value) for key, value in ree_prices.items()}
    prices = list(prices.items())
    prices.sort(key=lambda x: x[0])  # sort by datetime
    logging.info("prices:%s", prices)

    prices_slot1 = prices[: int(len(prices) / 2)]
    prices_slot2 = prices[int(len(prices) / 2) :]

    prices_slot1.sort(key=lambda x: x[1])  # sort by price
    prices_slot1 = [item[0] for item in prices_slot1]

    prices_slot2.sort(key=lambda x: x[1])  # sort by price
    prices_slot2 = [item[0] for item in prices_slot2]

    logging.info("prices_slot1:%s", prices_slot1)
    logging.info("prices_slot2:%s", prices_slot2)

    return prices_slot1[:number] + prices_slot2[:number]


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
    logging.info(ree_prices)
    if ree_prices:
        switch_on_times = better_times_slot(ree_prices, 4)
        logging.info("switch_on_times:%s", switch_on_times)
        zway = ZWayvDevAPI(
            ZWayConf.url, ZWayConf.port, ZWayPrivate.user, ZWayPrivate.password
        )
        heater = ZWayConf.water_heater_electric_meter
        while True:
            now = wake_up_o_clock(time_zone)
            logging.info("now:%s", now)
            if now in switch_on_times:
                zway.switch_on(heater)
                logging.info("Switch on heater")
                send_message(f"Optimizer: Switch on heater:{now}")
            else:
                zway.switch_off(heater)
                logging.info("Switch off heater:%s", now)
                send_message(f"Optimizer: Switch off heater:{now}")
            if now.hour == 20:
                logging.info("it is time to start again with new prices")
                send_message(f"Optimizer: start again with new prices:{now}")
                return
            time.sleep(60)


if __name__ == "__main__":

    TZ = pytz.timezone("Europe/Madrid")
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    logging.info("start optimizer")
    while True:  # run as a service always running
        time.sleep(60)
        logging.info("Waiting to have new prices from REE")
        send_message("Optimizer: Waiting to have new prices from REE")
        wake_up_on_time(20, 40, TZ)
        main(TZ)
        time.sleep(60)
    logging.info("end optimizer")
