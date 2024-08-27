import pandas as pd
import re 
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
import numpy as np


def conv_date(date):
    regular_format = r"\d{4}-\d{2}-\d{2}"
    if re.match(regular_format,date):
        return pd.to_datetime(date, format = "%Y-%m-%d")
    return pd.to_datetime(date, format = '%Y年%m月%d日')

def read_file(file, skiprows=False):
    if file.name == '2017-2020-kyoto.csv':
        skiprows = True
    if skiprows:
        rows = [0, 1, 2, 4]
    else:
        rows = None

    df = pd.read_csv(file, 
        encoding = 'shift_jis',
        skiprows=rows,
        converters={'Unnamed: 0':conv_date},
        index_col=0,
    )
    if file.name == '2017-2020-kyoto.csv':
        column_names = [
        'precipitation', 'sunshine_duration', 'windspeed_ave',
        'humidity_ave', 'temp_max(C)', 'temp_min(C)', 'snow']
        df.columns = column_names
    return df

def plot_decompose_result(decompose_result):
    fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(8, 8), sharex=True)
    # 原系列
    axes[0].set_title('Observed')
    axes[0].plot(decompose_result.observed)

    # 傾向変動
    axes[1].set_title('Trend')
    axes[1].plot(decompose_result.trend)

    # 季節変動
    axes[2].set_title('Seasonal')
    axes[2].plot(decompose_result.seasonal)

    # 残差 (不規則変動 = 誤差変動 + 特異的変動)
    axes[3].set_title('Residual')
    axes[3].plot(decompose_result.resid)

    plt.show()

def nettaiya(x):
    return len(x[25<x])

def natsubi(x):
    return len(x[np.logical_and(25<x.values, x.values<30)])

def manatsubi(x):
    return len(x[np.logical_and(30<x.values, x.values<35)])

def mousyobi(x):
    return len(x[35<x])


class Weather:
    def __init__(self, file):
        if type(file) == pd.DataFrame:
            self.weather_data = file
        elif type(file.name) == str:
            self.weather_data = read_file(file)
        else:
            self.filename = file
    
    def simple_statistics(self,temp):
        if 'temp_max(C)' in self.weather_data.columns:
            mask = self.weather_data['temp_max(C)'] > temp
            
        elif '最高気温(℃)' in self.weather_data.columns:
            mask = self.weather_data['最高気温(℃)'] > temp
        
        else: 
            return '最高気温(℃) が見当たらない。'

        greater_than = self.weather_data[mask]

        days = len(greater_than)

        total = len(self.weather_data)

        percent = days/total
    

        return (
                f"{temp}℃を超えた日 {days}日  \n"
                f"{temp}℃を超えた日 {percent*100:.2f}%"
            )
    
    def categorize(self):
        groups = self.weather_data.groupby(pd.Grouper(freq='Y'))
        if '最高気温(℃)' in self.weather_data.columns:
            print('here')
            temp_max = '最高気温(℃)'
            temp_min = '最低気温(℃)'
        else:
            temp_max = 'temp_max(C)'
            temp_min = 'temp_min(C)'
        
        summary= groups.agg({temp_max:[('夏日', natsubi),('真夏日', manatsubi),('猛暑日', mousyobi)], temp_min: [('熱帯夜',nettaiya)]})
        
        summary.index = pd.to_datetime(summary.index, format='%Y-%m-%d').year
        summary.columns = summary.columns.droplevel()
        
        return summary
    
    def seasonal(self):
        decompose_result = seasonal_decompose(
            self.weather_data['最高気温(℃)'],
            model='adaptive',
            period=365,
        )
        plot_decompose_result(decompose_result)
    

    def visualize(self):
        date_index = self.weather_data.index
        mask = (date_index.month == 2) & (date_index.day == 29)
        data = self.weather_data[~mask]
        last_year = data.index.year.unique().max()

        data_past = data[['temp_max(C)', 'temp_min(C)']][data.index.year != last_year]
        data_last = data[data.index.year == last_year].reset_index()
        data_past['dayofyear'] = data_past.index.dayofyear

        group = data_past.groupby('dayofyear')

        min_temp = group.min()
        max_temp = group.max()

        bands = pd.merge(max_temp['temp_max(C)'], min_temp['temp_min(C)'], left_index=True, right_index=True).reset_index().drop('dayofyear', axis=1)
        temp_upper = bands['temp_max(C)'].values
        temp_lower = bands['temp_min(C)'].values

        upper_mask = bands['temp_max(C)'].values < data_last['temp_max(C)'].values
        lower_mask = bands['temp_min(C)'].values > data_last['temp_min(C)'].values

        fig, ax = plt.subplots()

        ax.fill_between(bands.index ,temp_upper, temp_lower, alpha=0.2)
        ax.plot(temp_upper, 'k', alpha=0.5)
        ax.plot(temp_lower, 'k', alpha=0.5)
        ax.plot(data_last[upper_mask]['temp_max(C)'], 'xr')
        ax.plot(data_last[lower_mask]['temp_min(C)'], 'xb')
        ax.set_xlabel('Days')
        ax.set_ylabel('Temperature [C]')
        ax.autoscale(enable=True, axis='x', tight=True)

        return fig

if __name__ == "__main__":
    df = read_file("data/2017-2020-kyoto.csv")
    print(df)