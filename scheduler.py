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
from utils import is_evening
from utils import is_night
from utils import is_afternoon
from utils import is_morning
from utils import part_of_the_day


def analyze(ree_prices: dict, name: str):
    """
    TODO
    """
    if name is None:
        prices = {key: float(value) for key, value in ree_prices.items()}
        prices.sort(key=lambda x: x[1])
        return prices

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


def send_header(sender: Sender, _now: datetime):
    """
    TODO
    """
    if not sender.login():
        return
    today = _now + timedelta(hours=1)
    tomorrow = _now + timedelta(days=1)
    message = "Ya tenemos los precios de tarifa de luz *PVPC* "
    message += (
        f"desde las {today.hour}h de hoy hasta las 23h de mañana *día {tomorrow.day}*\n"
    )
    sender.send_message(message)


def send_message(sender: Sender, message: str):
    """
    TODO
    """
    if not sender.login():
        return

    sender.send_message("\n" + message + "\n")


def calculate_best_results_by_slot(_device: str, _results: list, ree_prices: dict):
    """
    TODO
    """

    worst_results = calculate_worst_results(ree_prices, 6)
    worst_times = [result[0] for result in worst_results]

    _results = [result for result in _results if result[0] not in worst_times]

    results_night = [item for item in _results if is_night(item[0])]
    results_night.sort(key=lambda item: item[1])

    results_morning = [item for item in _results if is_morning(item[0])]
    results_morning.sort(key=lambda item: item[1])

    results_afternoon = [item for item in _results if is_afternoon(item[0])]
    results_afternoon.sort(key=lambda item: item[1])

    results_evening = [item for item in _results if is_evening(item[0])]

    results_evening.sort(key=lambda item: item[1])

    best_results = []
    if results_night:
        best_results.append(results_night[0])
    if results_morning:
        best_results.append(results_morning[0])
    if results_afternoon:
        best_results.append(results_afternoon[0])
    if results_evening:
        best_results.append(results_evening[0])
    best_results.sort(key=lambda item: item[1])

    return best_results


def calculate_worst_results(ree_prices: dict, number: int):
    """
    TODO
    """
    prices = {key: float(value) for key, value in ree_prices.items()}
    worst_results = list(prices.items())
    worst_results.sort(key=lambda item: item[1], reverse=True)
    worst_results = worst_results[:number]
    return worst_results


def calculate_best_results(ree_prices: dict, number: int):
    """
    TODO
    """
    prices = {key: float(value) for key, value in ree_prices.items()}
    worst_results = list(prices.items())
    worst_results.sort(key=lambda item: item[1])
    worst_results = worst_results[:number]
    return worst_results


def send_best_results_by_slots(
    sender: Sender, _device: str, best_results: list, ree_prices: dict, _now: datetime
):
    """
    TODO
    """

    if not sender.login():
        return

    message = f"Las horas *más baratas* por  __franja horaria__ para conectar {_device }  son:"
    if "coches" in _device:
        message = f"Las horas *más baratas* por __franja horaria__ para inciciar carga de  {_device }  son:"

    icons = ["🏆", "🥇", "🥈", "🥉"]

    final_results = []
    if "coches" in _device:
        for i, result in enumerate(best_results[:2]):
            final_results.append((icons[i], part_of_the_day(result[0]), result[0],))
    else:
        for i, result in enumerate(best_results):
            final_results.append((icons[i], part_of_the_day(result[0]), result[0],))

    for result in final_results:
        message += f"\nDe __{result[1]}__ : "
        message += f"{result[0]}"
        message += f"a las *{result[2].strftime('%H:%M')}*h"
        if result[2].day == _now.day:
            message += " de hoy "
        if "2h" in _device:
            price = ree_prices[result[2]]
            price = price.replace(".", ",")
            message += f" a {price} €/kWh"

    sender.send_message(message)


def send_worst_results(
    sender: Sender, worst_results: list, ree_prices: dict, _now: datetime, number: int
):
    """
    TODO
    """
    if not sender.login():
        return
    message = f"Las {number} horas *más caras* son:\n"

    icons = ["⛔️", "❌", "❗️", "👎", "👎", "👎", "👎", "👎"]

    final_results = []
    for i, result in enumerate(worst_results):
        final_results.append((icons[i], result[0]))

    for result in final_results:
        message += result[0]
        message += " a las *" + result[1].strftime("%H:%M") + "*h"
        if result[1].day == _now.day:
            message += " de hoy"
        price = ree_prices[result[1]]
        price = price.replace(".", ",")
        message += f" a {price} €/kWh\n"

    sender.send_message(message)


def send_best_results(
    sender: Sender, worst_results: list, ree_prices: dict, _now: datetime, number: int
):
    """
    TODO
    """
    if not sender.login():
        return
    message = f"Las {number} horas *más baratas* son:\n"

    icons = ["🏆", "🥇", "🥈", "🥉", "👌", "👍", "👍", "👍"]

    final_results = []
    for i, result in enumerate(worst_results):
        final_results.append((icons[i], result[0]))

    for result in final_results:
        message += result[0]
        message += " a las *" + result[1].strftime("%H:%M") + "*h"
        if result[1].day == _now.day:
            message += " de hoy"
        price = ree_prices[result[1]]
        price = price.replace(".", ",")
        message += f" a {price} €/kWh\n"

    sender.send_message(message)


def main(senders: List[Sender], programs: dict, _now: datetime, number: int):
    """
    TODO
    """
    while True:
        ree = DataAPIRee()
        ree_prices = ree.kwh_price(_now + timedelta(hours=1))
        if ree_prices:
            logging.info("prices:%s", ree_prices)
            worst_results = calculate_worst_results(ree_prices, number)
            best_results = calculate_best_results(ree_prices, number)
            for sender in senders:
                send_header(sender, _now)
                time.sleep(2)
                send_best_results(sender, best_results, ree_prices, _now, number)
                time.sleep(2)
                send_worst_results(sender, worst_results, ree_prices, _now, number)
                time.sleep(2)
            for description, name in programs.items():
                results = analyze(ree_prices, name)
                logging.info("results:%s", results)
                best_results_by_slots = calculate_best_results_by_slot(
                    name, results, ree_prices
                )
                for sender in senders:
                    send_best_results_by_slots(
                        sender, description, best_results_by_slots, ree_prices, _now
                    )
                time.sleep(2)

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
        "electrodomésticos con programas cortos o medios hasta 2h\\": "WMAEGOKOPower1h40cel1000rpm",
        "electrodomésticos  con programas largos de 3h o mas ": "DWBOSCHECO3h30m50cel",
        "coches eléctricos \\(8 horas de carga\\)": "continuous8h",
    }

    TZ = pytz.timezone("Europe/Madrid")
    HOUR = 20
    MINUTE = 30
    NUMBER = 6

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

    # telegram.send_message("Start scheduler")

    SENDERS = [telegram]

    while True:  # run as a service always running
        wake_up_on_time(HOUR, MINUTE, TZ)
        main(SENDERS, PROGRAMS, datetime.now(tz=TZ), NUMBER)

        time.sleep(3600)
