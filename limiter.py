"""
TODO
"""
import logging
import os
import time
from datetime import datetime
import pytz
from zway import ZWayConf, ZWayvDevAPI
from private.config import ZWayPrivate, MatrixPrivate
from matrix import Matrix


def send_notification(message: str):
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


def main(
    meter: str,
    switches: list,
    upper_limit: int,
    lower_limit: int,
    sleep: int,
    interval: int,
    time_zone: pytz.timezone,
):
    """
    TODO
    """
    zway = ZWayvDevAPI(
        ZWayConf.url, ZWayConf.port, ZWayPrivate.user, ZWayPrivate.password
    )
    zway.sensor_update(meter)
    time.sleep(interval)
    info = zway.sensor_meter_info(meter, time_zone)
    logger.info("info:%s", info)
    if "level" not in info:
        logger.error("level not  in info")
        return
    if info["level"] > upper_limit:
        message = f"exceeded maximum power:{info['level']}w"
        logger.info("exceeded maximun power:%d w", info["level"])
        send_notification(message)
        for switch in switches:
            zway.switch_off(switch)
            message = f"switch_off:{switch}"
            logger.info("switch_off:%s", switch)
            send_notification(message)
            time.sleep(interval)
        while True:
            time.sleep(sleep)
            zway.sensor_update(meter)
            time.sleep(interval)
            info = zway.sensor_meter_info(meter, time_zone)
            if "level" not in info:
                logger.error("level not  in info")
                continue
            if info["level"] < lower_limit:
                message = f"now is safe to turn on devices:{info['level']}w"
                logger.info("now is safe to turn on devices:%d w", info["level"])
                send_notification(message)
                for switch in switches:
                    zway.switch_on(switch)
                    message = f"switch_on:{switch}"
                    logger.info("switch_on:%s", switch)
                    send_notification(message)
                    time.sleep(INTERVAL)
                return


if __name__ == "__main__":



    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    _datetime = datetime.now().strftime("_%Y-%m-%d_%H:%m_")
    file_handler = logging.FileHandler(f"logs/limiter{_datetime}.log")
    formatter    = logging.Formatter('%(asctime)s : %(levelname)s  : %(funcName)s: %(name)s : %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info('start limiter')

    TZ = pytz.timezone("Europe/Madrid")
    INTERVAL = 10
    METER = ZWayConf.house_electric_meter
    SWITCHES = [ZWayConf.water_heater]
    UPPER_LIMIT = 4000
    LOWER_LIMIT = 2200
    SLEEP = 600

    while True:
        main(METER, SWITCHES, UPPER_LIMIT, LOWER_LIMIT, SLEEP, INTERVAL, TZ)
        time.sleep(INTERVAL)

