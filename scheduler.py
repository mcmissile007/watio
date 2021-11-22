"""
TODO
"""
import logging
import os
import time
import sys
import getopt
from datetime import datetime
from datetime import timedelta
from typing import List

import pytz
from data_api_ree import DataAPIRee
from data_analysis import DataAnalysis
from matrix import Matrix
from telegram import Telegram
from private.config import MatrixPrivate, TelegramPrivate
from sender import Sender
from utils import wake_up_on_time


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


def send_results(
    sender: Sender,
    destination_id: str,
    _device: str,
    _results: list,
    number: int,
    _now: datetime,
):
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

    logging.info("message:%s", message)

    if sender.login():
        sender.send_message(message, destination_id)


def main(senders: List[Sender], programs: dict, _now: datetime):
    """
    TODO
    """
    while True:
        ree = DataAPIRee()
        ree_prices = ree.kwh_price(_now + timedelta(hours=1))
        if ree_prices:
            logging.info("prices:%s", ree_prices)
            for description, name in programs.items():
                results = analyze(ree_prices, name)
                logging.info("results:%s", results)
                for sender in senders:
                    send_results(sender, None, description, results, 12, _now)
                time.sleep(5)
            return True
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

    TZ = pytz.timezone("Europe/Madrid")
    HOUR = 20
    MINUTE = 30

    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s",
        level=os.environ.get("LOGLEVEL", "INFO"),
    )
    logging.info("start scheduler")

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "h:m:", longopts=["hour=", "minute="])

    except getopt.GetoptError as error:
        logging.error("%s", error)
        sys.exit(2)

    for opt in opts:
        if opt[0] == "-h" or opt[0] == "--hour":
            HOUR = int(opt[1])
        if opt[0] == "-m" or opt[0] == "--minute":
            MINUTE = int(opt[1])

    matrix = Matrix(
        MatrixPrivate.client_base_url,
        MatrixPrivate.media_base_url,
        MatrixPrivate.user_name,
        MatrixPrivate.password,
        MatrixPrivate.room_id,
    )

    telegram = Telegram(TelegramPrivate.bot_api_key, TelegramPrivate.channel_id)

    telegram.send_message("Start scheduler")
    if matrix.login():
        matrix.send_message("Start scheduler")

    SENDERS = [matrix, telegram]

    while True:  # run as a service always running
        wake_up_on_time(HOUR, MINUTE, TZ)
        main(SENDERS, PROGRAMS, datetime.now(tz=TZ))
        time.sleep(3600)

    # main(PROGRAMS, datetime.now(tz=TZ))
    telegram.send_message("End scheduler")
    if matrix.login():
        matrix.send_message("End scheduler")
    logging.info("end scheduler")
