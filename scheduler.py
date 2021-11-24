"""
TODO
"""
import logging
import os
import time
import sys
import getopt
import decimal
from datetime import date, datetime
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



def send_header(
    sender: Sender,
    _now: datetime
):
    """
    TODO
    """    
    if not sender.login():
        return
    tomorrow = (_now + timedelta(days=1)).day
    message = f"Con los precios actualizados de la tarifa de la luz PVPC para mañana dia {tomorrow}"
    sender.send_message(message)

def send_best_results(
    sender: Sender,
    _device: str,
    _results: list,
    _now: datetime
):
    """
    TODO
    """
    
    if not sender.login():
        return
    message = f"Los mejores horarios para programar {_device}:\n"
    results_night = [item for item in _results if is_night(item[0])]
    results_night.sort(key=lambda item: item[1])

    results_morning = [item for item in _results if is_morning(item[0])]
    results_morning.sort(key=lambda item: item[1])

    results_afternoon = [item for item in _results if is_afternoon(item[0])]
    results_afternoon.sort(key=lambda item: item[1])

    results_evening = [item for item in _results if is_evening(item[0])]
    results_evening.sort(key=lambda item: item[1])

    best_results = []
    best_results.append(results_night[0])
    best_results.append(results_morning[0])
    best_results.append(results_afternoon[0])
    best_results.append(results_evening[0])
    best_results.sort(key=lambda item: item[1])
    icons = ['🏆','🥇','🥈','🥉']

    final_results = []
    for i,icon in enumerate(icons):
        final_results.append((icon,part_of_the_day(best_results[i][0]),best_results[i][0],best_results[i][1]))
    
    decimal.getcontext().prec = 4
    for result in final_results:
        message += "De " + result[1] + ": " 
        message += result[0]
        message += "a las " + result[2].strftime("%H:%M") + "h"
        if result[1] == "noche":
            if result[2].day == _now.day:
                message += " de hoy "
            else: 
                message += " de mañana "
        message += " a "  + str(decimal.Decimal(result[3]))+ "\n"
 
    sender.send_message(message)

def send_worst_results(
    sender: Sender,
    _results: list,
    _now: datetime
    
):
    """
    TODO
    """
    if not sender.login():
        return
    message = ""
    _results.sort(key=lambda item: item[1],reverse=True)
    icons = ['⛔️','❌','❗️','👎']
    results = _results[:len(icons)]
    final_results = []
    for i,icon in enumerate(icons):
        final_results.append((icon,results[i][0],results[i][1]))
    
    decimal.getcontext().prec = 4

    for result in final_results:
        message += result[0]
        message += " a las " + result[1].strftime("%H:%M") + "h"
        if part_of_the_day(result[1]) == "noche":
            if result[1].day == _now.day:
                message += " de hoy"
            else: 
                message += " de mañana"
        message += " a "  + str(decimal.Decimal(result[2]))+ "\n"
 
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
            for sender in senders:
                send_header(sender,_now)
            for description, name in programs.items():
                results = analyze(ree_prices, name)
                logging.info("results:%s", results)
                for sender in senders:
                    send_best_results(sender, description, results, _now)
                time.sleep(5)
            prices = {key: float(value) for key, value in ree_prices.items()}
            for sender in senders:
                send_worst_results(sender, list(prices), _now)
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
        "lavavajillas programa largo ECO 3h": "DWBOSCHECO3h30m50cel",
        "lavadora o lavavajillas programa": "WMAEGOKOPower1h40cel1000rpm",
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
   

    SENDERS = [telegram]

    while True:  # run as a service always running
        wake_up_on_time(HOUR, MINUTE, TZ)
        main(SENDERS, PROGRAMS, datetime.now(tz=TZ))
        time.sleep(3600)
