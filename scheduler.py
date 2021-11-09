"""
TODO
"""

# import pandas as pd
from datetime import datetime
from data_api_ree import DataAPIRee
from data_analysis import DataAnalysis


class Scheduler:
    """
    TODO
    """

    def __init__(self, when: str = "today"):
        self.when = when
        self.devices = {
            1: "data/DWBOSCHECO3h30m50cel.csv",
            2: "data/WMAEGCotton30cel1000rpmEco.csv",
            3: "data/WMAEGOKOPower1h40cel1000rpm.csv",
            4: "data/WMAEG20min30cel1000rpm.csv",
        }

    @staticmethod
    def __convert_float_to_time(time: float) -> str:
        """
        TODO
        """
        hour = int(time)
        if hour == 0:
            minutes = int(time * 60)
            if minutes == 0:
                return "0:00h"
            return f"0:{minutes}"

        mod = time % hour
        if mod == 0:
            return f"{hour}:00h"
        minutes = int(60 * mod)
        return f"{hour}:{minutes}h"

    def service(self):
        """
        TODO
        """
        ree = DataAPIRee()
        # prices = ree.today_kwh_price()
        prices = ree.today_kwh_price()
        if prices:
            data_analysis = DataAnalysis()
            # data_analysis.read_data_from_file("data/DWBOSCHECO3h30m50cel.csv")
            data_analysis.read_data_from_file("data/WMAEGCotton30cel1000rpmEco.csv")
            prices = {
                datetime.strptime(key, "%Y-%m-%d %H:%M").hour: float(value)
                for key, value in prices.items()
            }
            data_analysis.get_total_cost(prices, 0.0)
            # delays = [x / 2 for x in range(0, 48, 1)]

            results = [
                (delay, data_analysis.get_total_cost(prices, delay))
                for delay in range(0, 24)
            ]
            results = [result for result in results if result[1] > 0.0]
            results = list(
                map(lambda x: (Scheduler.__convert_float_to_time(x[0]), x[1]), results)
            )
            results.sort(key=lambda x: x[1])

            print(results)


if __name__ == "__main__":
    print("start scheduler")
    scheduler = Scheduler()
    scheduler.service()
    print("end scheduler")
