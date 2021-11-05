"""
TODO
"""
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
