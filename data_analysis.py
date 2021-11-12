"""
TODO
"""
from datetime import timedelta
import pandas as pd
from matplotlib import pyplot as plt


class DataAnalysis:
    """
    TODO
    """

    def __init__(self):

        self.data = None

    def prepare_data(self):
        """
        TODO
        """
        self.data.drop(columns=["_id", "unit", "title"], inplace=True)
        self.data["ts"] = pd.to_datetime(self.data["ts"])
        self.data.sort_values(by="ts")  # just in case
        self.data.set_index("ts", inplace=True)
        self.data.dropna(inplace=True)
        self.data["level"] = abs(self.data.level)
        filt = self.data["level"] != 0.0
        self.data = self.data.loc[filt]
        self.data["epoch"].apply(int)
        self.data.drop_duplicates(keep="first", inplace=True)
        self.data["interval"] = self.data.epoch.shift(-1) - self.data.epoch
        self.data["minute"] = (self.data.epoch - self.data.iloc[0].epoch) / 60.0
        self.data["hour"] = (self.data.epoch - self.data.iloc[0].epoch) / 3600.0
        self.data.dropna(inplace=True)
        # print(self.data)

    def get_kwh(self):
        """
        TODO
        """
        self.data["wh"] = (self.data["level"] * self.data["interval"]) / 3600.0
        return (self.data["wh"].sum()) / 1000

    def get_data(self) -> pd.DataFrame:
        """
        TODO
        """
        return self.data

    def show_graph(self, appliances, kwh):
        """
        TODO
        """
        plt.style.use("seaborn")
        _fig1, ax1 = plt.subplots()
        # fig2,ax2 = plt.subplots()
        # values = self.data.level.resample("1Min").agg({'epoch':'first'})
        # ax2.plot(self.data.level,color="blue")
        # ax2.plot(values,color="blue")
        bars = ("0.0", "0.25", "0.5", "1", "1.5", "2.0", "2.5", "3.0", "3.5")
        x_pos = [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        plt.title(f"{appliances} {kwh} KWh")
        plt.xlabel("Hours")
        plt.ylabel("Watts")
        plt.xticks(x_pos, bars)
        ax1.plot(self.data.hour, self.data.level, color="blue")
        plt.show()

    def get_total_cost(self, prices: dict, delay: float) -> tuple:
        """
        TODO
        """
        sorted_prices_datetimes = sorted(prices.keys())
        first_price_datetime = sorted_prices_datetimes[0]
        last_price_datetime = sorted_prices_datetimes[-1]
        print(f"first_price_datetime:{first_price_datetime}")
        print(f"last_price_datetime:{last_price_datetime}")
        print(f"delay:{delay}")
        duration = self.data["hour"].max()
        print(f"max_duration:{duration}")
        start = first_price_datetime + timedelta(hours=(delay))
        end = first_price_datetime + timedelta(hours=(delay + duration))
        if end > last_price_datetime + timedelta(hours=1):
            return (
                start,
                -1,
            )

        # rounded values down 4.7 -> 4
        self.data["rate_hour"] = (self.data.hour + delay).astype(int)
        # rounded values ok 4.7 -> 5
        # self.data["rate_hour"] = self.data["rate_hour"].round(0).astype(int)
        # https://kanoki.org/2019/04/06/pandas-map-dictionary-values-with-dataframe-columns/
        self.data["datetime"] = first_price_datetime + self.data["rate_hour"].map(
            lambda x: timedelta(hours=x)
        )
        print(self.data)
        self.data["price_kwh"] = self.data["datetime"].map(prices)
        self.data["price_ws"] = self.data.price_kwh.map(lambda x: x / (3600 * 1000))
        self.data["cost"] = (
            self.data["level"] * self.data["interval"] * self.data["price_ws"]
        )
        return (
            start,
            self.data["cost"].sum(min_count=int(duration)),
        )

    def read_data_from_file(self, filename):
        """
        TODO
        """
        print(filename)
        self.data = pd.read_csv(filename)
        self.prepare_data()


def test_funcs():
    """
    TODO
    """
    data = DataAnalysis()
    measurement = "DWBOSCH1h65cel"
    data.read_data_from_file(f"data/{measurement}.csv")
    kwh = data.get_kwh()
    print(f"kwh:{kwh}")
    data.show_graph("measurement", kwh)


if __name__ == "__main__":
    test_funcs()
