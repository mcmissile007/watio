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


def send_results_old(
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


def send_header(sender: Sender, _now: datetime):
    """
    TODO
    """
    if not sender.login():
        return
    tomorrow = (_now + timedelta(days=1))
    message = "Precios actualizados de la *tarifa de la luz PVPC* "
    message += f"para mañana *día {tomorrow.day}*\n"
    sender.send_message(message)


def calculate_best_results(_device: str, _results: list, ree_prices: dict):
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


def send_best_results(
    sender: Sender, _device: str, best_results: list, ree_prices: dict, _now: datetime
):
    """
    TODO
    """

    if not sender.login():
        return
      
    message = f"Las horas *más baratas* por  __franja horaria__ para conectar {_device }  son:"
    if "coches"  in _device:
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
        if "electrodomésticos" in _device:
            price = ree_prices[result[2]]
            price = price.replace(".", ",")
            message += f" a {price} €/kWh"

    sender.send_message(message)


def send_worst_results(
    sender: Sender, worst_results: list, ree_prices: dict, _now: datetime
):
    """
    TODO
    """
    if not sender.login():
        return
    message = (
        "Las horas *más caras* en los que hay que evitar  un consumo alto de energía son:\n"
    )

    icons = ["⛔️", "❌", "❗️", "👎","👎","👎"]

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


def main(senders: List[Sender], programs: dict, _now: datetime):
    """
    TODO
    """
    while True:
        ree = DataAPIRee()
        ree_prices = ree.kwh_price(_now + timedelta(hours=1))
        if ree_prices:
            logging.info("prices:%s", ree_prices)
            worst_results = calculate_worst_results(ree_prices, 6)
            for sender in senders:
                send_header(sender, _now)
           
            for description, name in programs.items():
                results = analyze(ree_prices, name)
                logging.info("results:%s", results)
                best_results = calculate_best_results(name, results, ree_prices)
                for sender in senders:
                    send_best_results(
                        sender, description, best_results, ree_prices, _now
                    )
                time.sleep(2)
           
            time.sleep(5)
            for sender in senders:
                send_worst_results(sender, worst_results, ree_prices, _now)

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
        "electrodomésticos de alto consumo eléctrico como lavadoras,lavavajillas,secadoras etc\\.": "WMAEGOKOPower1h40cel1000rpm",
        "lavavajillas  con programas ECO de 3 horas o más": "DWBOSCHECO3h30m50cel",
        "coches electricos \\(8 horas de carga\\)": "continuous8h",
        "coches electricos \\(6 horas de carga\\)": "continuous6h",
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

    #telegram.send_message("Start scheduler")

    SENDERS = [telegram]

    while True:  # run as a service always running
        wake_up_on_time(HOUR, MINUTE, TZ)
        main(SENDERS, PROGRAMS, datetime.now(tz=TZ))
        time.sleep(3600)
