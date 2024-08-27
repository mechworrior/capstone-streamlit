import streamlit as st

import numpy as np
import pandas as pd
from weather_io import Weather
from weather_scraper import get_weather

st.set_page_config(
        page_title="Capstone",
)

st.markdown("""# Capstone webapp
#### Capstoneの結果を可視化するウェブアプリです。""")

st.write('''手持ちのデータをアップロードしてください。''')

uploaded_file = st.file_uploader('天気データ')
if uploaded_file is not None:
    weather_inst = Weather(uploaded_file)
    st.write(weather_inst.weather_data.head(3))
    st.session_state['weather_data'] = weather_inst

st.write('''または取得したいデータを指定してください。''')

years = list(range(1976,2024))
start_year, end_year = st.select_slider(
    '取得したい年間を選択してください。',
    options=years,
    value=[2000,2023],
    )
get_data_confirm = st.button(f'{start_year} から {end_year}までのデータを取得')
if start_year and end_year and get_data_confirm:
    if start_year == end_year:
        years = [start_year]
    else:
        years = [start_year,end_year]
    with st.spinner(f'{start_year} から {end_year}までのデータを取得しています。'):
        weather_inst = Weather(get_weather(years=years))
    st.write(weather_inst.weather_data.head(3))
    st.write(weather_inst.weather_data.columns)
    st.session_state['weather_data'] = weather_inst
    st.session_state['years'] = years




