from datetime import date
import pandas as pd
from matplotlib import pyplot as plt



class DataAnalysis():
    def __init__(self):
        self.df = None

    def prepare_data(self):
        self.df.drop(columns=['_id','unit','title'],inplace=True)
        self.df['ts'] = pd.to_datetime(self.df['ts'])
        self.df.sort_values(by="ts") #just in case
        self.df.set_index('ts',inplace=True)
        self.df.dropna(inplace=True)
        self.df['level'] = abs(self.df.level)
        filt = self.df['level'] != 0.0
        self.df = self.df.loc[filt]
        self.df['epoch'].apply(int)
        self.df.drop_duplicates(keep ='first',inplace=True)
        self.df['interval'] = self.df.epoch.shift(-1) - self.df.epoch
        self.df['minute'] = (self.df.epoch - self.df.iloc[0].epoch ) / 60.0
        self.df['hour'] = (self.df.epoch - self.df.iloc[0].epoch ) / 3600.0
        self.df.dropna(inplace=True)
        print(self.df)
        
    def get_kwh(self):
        self.df['wh'] = (self.df['level'] * self.df['interval'])/3600.0
        return (self.df['wh'].sum())/1000

    def show_graph(self, appliances,kwh):
        plt.style.use("seaborn")
        fig1,ax1 = plt.subplots()
        #fig2,ax2 = plt.subplots()
        values = self.df.level.resample("1Min").agg({'epoch':'first'})
        #ax2.plot(self.df.level,color="blue")
        #ax2.plot(values,color="blue")
        bars = ('0.0','0.25','0.5','1', '1.5', '2.0', '2.5','3.0','3.5')
        x_pos = [0.0,0.25,0.5,1.0,1.5,2.0,2.5,3.0,3.5]
        plt.title(f"{appliances} {kwh} KWh")
        plt.xlabel('Hours')
        plt.ylabel('Watts')
        plt.xticks(x_pos, bars)
        ax1.plot(self.df.hour,self.df.level,color="blue")
        plt.show()

    def read_data_from_file(self,filename):
        print(filename)
        self.df = pd.read_csv(filename)
        self.prepare_data()

def test_funcs ():
    data = DataAnalysis()
    measurement = "DWBOSCH1h65cel"
    data.read_data_from_file(f"data/{measurement}.csv")
    kwh = data.get_kwh()
    print(f"kwh:{kwh}")
    data.show_graph("measurement",kwh)
if __name__ == "__main__":
    test_funcs()
