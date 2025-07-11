
import joblib
import pandas as pd
import numpy as np
import joblib
import holidays
import tensorflow as tf
from datetime import datetime, timedelta
from weather import get_hourly_weather_seoul_openmeteo
from DBMS_lastYear_M2 import fill_missing_timeseries
from model1 import result_df_return
from model2 import input_M2_data
import warnings; 
warnings.filterwarnings('ignore')
model = joblib.load("../../Predict_models/M2/M2_categorical_rf.pkl")
model2_input = input_M2_data() # 라벨링 스케일링 완료된 상태
# feature_cols = ['PM대여량', '1년전_PM대여량', '1년전_총생활인구수', '총생활인구수', '출퇴근시간여부', '시', '주말구분',
#     '풍속', '공공자전거대여량', '습도', '기온', '행정구', '월', 'PM대여량_class', '계절', '강수',
#     '연도', '공휴일', '일']
# num_cols=['총생활인구수_1년전', '강수', '기온','습도','풍속','대여량_1년전']
cols_X = ['연도','월','일','시','행정구','총생활인구수','계절','출퇴근시간여부','주말구분','강수','기온','습도','풍속','공공자전거대여량','공휴일','1년전_총생활인구수','1년전_PM대여량']

model = joblib.load("../../Predict_models/M2/M2_categorical_rf.pkl")

def predict_result() :
    '''오늘로부터 8일간의 데이터를 predict해서 결과를 반환하는 함수'''
    pred = model.predict(model2_input[cols_X]).reshape(-1,1)
    df_pred = pd.DataFrame(pred, columns=['예상PM수요'])
    return df_pred


if __name__ == "__main__" :
    pred = predict_result() 
    df_pred = pd.DataFrame(pred)
    print(pred)
    print(df_pred)
