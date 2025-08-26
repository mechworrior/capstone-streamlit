import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np


def conv_date(date):
    regular_format = r"\d{4}-\d{2}-\d{2}"
    if re.match(regular_format, date):
        return pd.to_datetime(date, format="%Y-%m-%d")
    return pd.to_datetime(date, format="%Y年%m月%d日")


def read_file(file, skiprows=False):
    if file.name == "2017-2020-kyoto.csv":
        skiprows = True
    if skiprows:
        rows = [0, 1, 2, 4]
    else:
        rows = None

    df = pd.read_csv(
        file,
        encoding="shift_jis",
        skiprows=rows,
        converters={"Unnamed: 0": conv_date},
        index_col=0,
    )
    if file.name == "2017-2020-kyoto.csv":
        column_names = [
            "precipitation",
            "sunshine_duration",
            "windspeed_ave",
            "humidity_ave",
            "temp_max(C)",
            "temp_min(C)",
            "snow",
        ]
        df.columns = column_names
    return df


def plot_decompose_result(decompose_result):
    fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(8, 8), sharex=True)
    # 原系列
    axes[0].set_title("Observed")
    axes[0].plot(decompose_result.observed)

    # 傾向変動
    axes[1].set_title("Trend")
    axes[1].plot(decompose_result.trend)

    # 季節変動
    axes[2].set_title("Seasonal")
    axes[2].plot(decompose_result.seasonal)

    # 残差 (不規則変動 = 誤差変動 + 特異的変動)
    axes[3].set_title("Residual")
    axes[3].plot(decompose_result.resid)

    plt.show()


def nettaiya(x):
    return len(x[25 < x])


def natsubi(x):
    return len(x[np.logical_and(25 < x.values, x.values < 30)])


def manatsubi(x):
    return len(x[np.logical_and(30 < x.values, x.values < 35)])


def mousyobi(x):
    return len(x[35 < x])


class Weather:
    def __init__(self, file):
        if type(file) == pd.DataFrame:
            self.weather_data = file
        elif type(file.name) == str:
            self.weather_data = read_file(file)
        else:
            self.filename = file

    def simple_statistics(self, temp):
        if "temp_max(C)" in self.weather_data.columns:
            problematic_rows = self.weather_data[
                pd.to_numeric(self.weather_data["temp_max(C)"], errors="coerce").isna()
            ]

            # If any such rows are found, print them
            if not problematic_rows.empty:
                print("--- Found non-numeric data that would cause an error: ---")
                print(problematic_rows)
                print("---------------------------------------------------------")
                # --- END: DEBUGGING CODE ---

            mask = self.weather_data["temp_max(C)"] > temp

        elif "最高気温(℃)" in self.weather_data.columns:
            mask = self.weather_data["最高気温(℃)"] > temp

        else:
            return "最高気温(℃) が見当たらない。"

        greater_than = self.weather_data[mask]

        days = len(greater_than)

        total = len(self.weather_data)

        percent = days / total

        return f"{temp}℃を超えた日 {days}日  \n{temp}℃を超えた日 {percent * 100:.2f}%"

    def categorize(self):
        """
        年ごとの夏日、真夏日、猛暑日、熱帯夜の日数を集計する関数。

        Returns:
            pd.DataFrame: 年ごとの夏日、真夏日、猛暑日、熱帯夜の日数を格納したDataFrame。
        """
        # 年ごとにデータをグループ化
        groups = self.weather_data.groupby(pd.Grouper(freq="Y"))

        # 最高気温と最低気温の列名を、データフレームの列名に応じて設定
        if "最高気温(℃)" in self.weather_data.columns:
            temp_max = "最高気温(℃)"
            temp_min = "最低気温(℃)"
        else:
            temp_max = "temp_max(C)"
            temp_min = "temp_min(C)"

        # 各年に対して、夏日、真夏日、猛暑日、熱帯夜の日数を集計
        summary = groups.agg(
            {
                temp_max: [
                    ("夏日", natsubi),
                    ("真夏日", manatsubi),
                    ("猛暑日", mousyobi),
                ],
                temp_min: [("熱帯夜", nettaiya)],
            }
        )

        # インデックスを年に変換
        summary.index = pd.to_datetime(summary.index, format="%Y-%m-%d").year
        # 列のマルチインデックスを解除
        summary.columns = summary.columns.droplevel()

        return summary

    def visualize(self):
        """
        過去の気温データと最新年の気温データを比較するグラフを生成する関数。
        """
        date_index = self.weather_data.index

        # 閏年の2月29日を除外
        mask = (date_index.month == 2) & (date_index.day == 29)
        data = self.weather_data[~mask]
        # 最新年を取得
        last_year = data.index.year.unique().max()

        # 最新年と過去のデータを分割
        data_past = data[["temp_max(C)", "temp_min(C)"]][data.index.year != last_year]
        data_last = data[data.index.year == last_year].reset_index()
        # 日付を日番号に変換
        data_past["dayofyear"] = data_past.index.dayofyear

        # 閏年の3月以降の日番号を調整
        leap_year_mask = data_past.index.is_leap_year & (data_past.index.month >= 3)
        data_past["dayofyear"][leap_year_mask] = (
            data_past["dayofyear"][leap_year_mask] - 1
        )

        # 日番号ごとにデータをグループ化し、最高気温と最低気温の最小値と最大値を計算
        group = data_past.groupby("dayofyear")
        min_temp = group.min()
        max_temp = group.max()

        # 最高気温と最低気温の最小値と最大値を結合
        bands = (
            pd.merge(
                max_temp["temp_max(C)"],
                min_temp["temp_min(C)"],
                left_index=True,
                right_index=True,
            )
            .reset_index()
            .drop("dayofyear", axis=1)
        )
        temp_upper = bands["temp_max(C)"].values
        temp_lower = bands["temp_min(C)"].values

        # 最新年の最高気温と最低気温が過去の範囲外の日を特定
        upper_mask = bands["temp_max(C)"].values < data_last["temp_max(C)"].values
        lower_mask = bands["temp_min(C)"].values > data_last["temp_min(C)"].values

        # グラフを生成
        fig, ax = plt.subplots()

        # 過去の気温範囲を塗りつぶし
        ax.fill_between(bands.index, temp_upper, temp_lower, alpha=0.2)
        # 過去の最高気温と最低気温の最大値と最小値を線で表示
        ax.plot(temp_upper, "k", alpha=0.5)
        ax.plot(temp_lower, "k", alpha=0.5)
        # 最新年の範囲外の最高気温と最低気温をプロット
        ax.plot(data_last[upper_mask]["temp_max(C)"], "xr")
        ax.plot(data_last[lower_mask]["temp_min(C)"], "xb")
        # 軸ラベルを設定
        ax.set_xlabel("日数")
        ax.set_ylabel("気温 [℃]")
        # x軸を自動調整
        ax.autoscale(enable=True, axis="x", tight=True)
        plt.show()

        return fig


if __name__ == "__main__":
    df = read_file("data/2017-2020-kyoto.csv")
    print(df)
