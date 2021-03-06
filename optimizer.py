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
from utils import wake_up_o_clock
from utils import is_evening


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
   

    prices = [item for item in prices if not is_evening(item[0])]

    logger.info("remove evenings by user requirement, prices:%s", prices)

    prices.sort(key=lambda x: x[0])  # sort by datetime
    logger.info("prices:%s", prices)

    prices_slot1 = prices[: int(len(prices) / 2)]
    prices_slot2 = prices[int(len(prices) / 2) :]

    prices_slot1.sort(key=lambda x: x[1])  # sort by price
    prices_slot1 = [item[0] for item in prices_slot1]

    prices_slot2.sort(key=lambda x: x[1])  # sort by price
    prices_slot2 = [item[0] for item in prices_slot2]

    logger.info("prices_slot1:%s", prices_slot1)
    logger.info("prices_slot2:%s", prices_slot2)

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
    logger.info(ree_prices)
    if ree_prices and len(ree_prices) > 16:
        switch_on_times = better_times_slot(ree_prices, 4)
        logger.info("switch_on_times:%s", switch_on_times)
        zway = ZWayvDevAPI(
            ZWayConf.url, ZWayConf.port, ZWayPrivate.user, ZWayPrivate.password
        )
        heater = ZWayConf.water_heater
        while True:
            now = wake_up_o_clock(time_zone)
            logger.info("now:%s", now)
            if now in switch_on_times:
                zway.switch_on(heater)
                logger.info("Switch on heater")
                send_message(f"Optimizer: Switch on heater:{now}")
            else:
                zway.switch_off(heater)
                logger.info("Switch off heater:%s", now)
                send_message(f"Optimizer: Switch off heater:{now}")
            if now.hour == 20:
                logger.info("it is time to start again with new prices")
                send_message(f"Optimizer: start again with new prices:{now}")
                time.sleep(35*60)
                return
            time.sleep(60)


if __name__ == "__main__":

    
    logger = logging.getLogger(__name__)  
  
   
    logger.setLevel(logging.DEBUG)
    _datetime = datetime.now().strftime("_%Y-%m-%d_%H:%m_")
    file_handler = logging.FileHandler(f"logs/optimizer{_datetime}.log")
    formatter    = logging.Formatter('%(asctime)s : %(levelname)s  : %(funcName)s: %(name)s : %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info('start optimizer')

    TZ = pytz.timezone("Europe/Madrid")

    while True:  # run as a service always running
        main(TZ)
        time.sleep(300)
  
