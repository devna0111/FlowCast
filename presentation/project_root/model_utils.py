# model_utils.py
import joblib
import pandas as pd
import numpy as np
import joblib
import holidays
import tensorflow as tf
from datetime import datetime, timedelta
from weather import get_hourly_weather_seoul_openmeteo
from DBMS_lastYear import DBMS_last_year_one_week
from model1 import result_df_return

# 1. 모델/스케일러/인코더/데이터 전역(Global)으로 한 번만 로딩
# model2 = joblib.load('M2_model.pkl')
# gu_weight = pd.read_csv('gu_weight.csv')

weather = get_hourly_weather_seoul_openmeteo()
lastyear_data = DBMS_last_year_one_week() 
model1_result = result_df_return()
# lastyear_data.columns = ['연도','월','일','시','행정구','일시','1년전_총생활인구수','계절','출퇴근시간여부','주말구분','강수','기온','습도','풍속','1년전_공공자전거대여량']

if __name__ == '__main__' :
    print(model1_result)