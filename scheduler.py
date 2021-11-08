"""
TODO
"""

# import pandas as pd
from datetime import datetime
from data_api_ree import DataAPIRee
from data_analysis import DataAnalysis


def main():
    """
    TODO
    """
    ree = DataAPIRee()
    # prices = ree.today_kwh_price()
    prices = ree.tomorrow_kwh_price()
    if prices:
        data_analysis = DataAnalysis()
        data_analysis.read_data_from_file("data/DWBOSCHECO3h30m50cel.csv")
        prices = {
            datetime.strptime(key, "%Y-%m-%d %H:%M").hour: float(value)
            for key, value in prices.items()
        }
        data_analysis.get_total_cost(prices, 0.0)
        delays = [x / 2 for x in range(0, 48, 1)]
        results = [
            (delay, data_analysis.get_total_cost(prices, delay)) for delay in delays
        ]
        results = [result for result in results if result[1] > 0.0]
        results.sort(key=lambda tup: tup[1])

        print(results)


if __name__ == "__main__":
    print("start scheduler")
    main()
    print("end scheduler")
