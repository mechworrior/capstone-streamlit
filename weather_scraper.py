import pandas as pd
import requests
from typing import Optional


def get_weather(
    years: Optional[int] = [2023],
    months: Optional[int] = list(range(1,13)),
    prec_no: int = 44,
    block_no: int = 47662,
):
    uri = 'https://www.data.jma.go.jp/stats/etrn/view/daily_s1.php'
    params = locals()
    prev = False
    
    def parse_headers(cols):
        new_cols = []
        for col in cols:
            new_cols.append(
                ''.join(list(dict.fromkeys(col,None).keys())[-1::-1]) 
            )
        return new_cols
    
    for year in params['years']:
        for month in params['months']:
            resp = requests.get(
                url=uri, 
                params={
                    'year': year,
                    'month': month,
                    'prec_no': prec_no,
                    'block_no': block_no,
                }
            )
            df_cur = pd.read_html(resp.content)[0]
            df_cur.columns = parse_headers(df_cur.columns)
            df_cur['日'] = pd.to_datetime(
                df_cur['日'].apply(
                    lambda x: f'{year}-{month:02d}-{x:02d}'
                )
            )
            df_cur = df_cur.iloc[:,[0,3,16,11,9,7,8,17]]
            if not prev:
                df_total = df_cur
                prev = True
            else:
                df_total = pd.concat((df_total,df_cur), axis=0)
    df_total.set_index('日',inplace=True)
    df_total.columns = [
        'precipitation', 'sunshine_duration', 'windspeed_ave',
        'humidity_ave', 'temp_max(C)', 'temp_min(C)', 'snow'
        ]
    print(df_total.info())
    return df_total