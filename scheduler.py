"""
TODO
"""

import pandas as pd
from data_api_ree import DataAPIRee
from data_analysis import DataAnalysis
from datetime import datetime


def main():
    """
    TODO
    """
    ree = DataAPIRee()
    prices = ree.today_kwh_price()
    print(f"today prices:{prices}")
    data_analysis = DataAnalysis()
    data_analysis.read_data_from_file("data/DWBOSCHECO3h30m50cel.csv")
    device_df = data_analysis.get_data()
    print(device_df)
    for item in prices:
        hour = datetime.strptime(item["datetime"], "%Y-%m-%d %H:%M").hour
        price = float(item["price"])
        print(hour, price)


if __name__ == "__main__":
    main()
