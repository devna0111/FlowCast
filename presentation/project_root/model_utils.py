# model_utils.py
from weather import get_hourly_weather_seoul_openmeteo
import pandas as pd
from DBMS_lastYear import DBMS_last_year_one_week
from DBMS_lastYear_M2 import DBMS_last_year_one_week_M2, fill_missing_timeseries
from model1 import result_df_return
from model2 import return_M2_result

weather = get_hourly_weather_seoul_openmeteo()
lastyear_data = DBMS_last_year_one_week() 
try :
    model1_result = result_df_return()
    model2_result = return_M2_result()
except :
    model1_result = pd.read_csv('M1_data.csv')
    model2_result = pd.read_csv('M2_data.csv')
# lastyear_data.columns = ['연도','월','일','시','행정구','일시','1년전_총생활인구수','계절','출퇴근시간여부','주말구분','강수','기온','습도','풍속','1년전_공공자전거대여량']

if __name__ == '__main__' :
    print(model1_result)
    print(model2_result)