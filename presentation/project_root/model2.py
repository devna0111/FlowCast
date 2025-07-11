import pandas as pd
# import numpy as np
import joblib
import holidays
# import tensorflow as tf
from datetime import datetime
from weather import get_hourly_weather_seoul_openmeteo
from DBMS_lastYear import DBMS_last_year_one_week
from DBMS_lastYear_M2 import DBMS_last_year_one_week_M2, fill_missing_timeseries
from model1 import result_df_return
import warnings; 
warnings.filterwarnings('ignore')

model = joblib.load("../../Predict_models/M2/M2_categorical_rf.pkl")

weather = get_hourly_weather_seoul_openmeteo()
check = fill_missing_timeseries()
df_PM = pd.read_csv(r"../../Predict_models/M2/PM_data/서울시_시간별_PM_배치_2021_2025.csv",parse_dates=['일시'])
df_PM.columns =['일시','행정구','1년전_PM대여량']
#['연도','월','일','시','행정구','총생활인구수_1년전','대여량_1년전']
df_long = result_df_return()
df_long.columns = ['행정구', '날짜', '시', '공공자전거대여량']

num_cols=['총생활인구수_1년전', '강수', '기온','습도','풍속','대여량_1년전']
cols_X = ['연도','월','일','시','행정구','총생활인구수',
        '계절','출퇴근시간여부','주말구분','강수','기온',
        '습도','풍속','공공자전거대여량','공휴일','1년전_총생활인구수','1년전_PM대여량']

pm_gu_list =joblib.load("../../Predict_models/M2/M2_ENCODER/PM활용행정구리스트.pkl")
gu_list = joblib.load("../../Predict_models/M2/M2_ENCODER/서울전역행정구리스트.pkl")
le_season = joblib.load("../../Predict_models/M2/M2_ENCODER/계절라벨인코더.pkl")
le_commute =joblib.load("../../Predict_models/M2/M2_ENCODER/출퇴근시간여부라벨인코더.pkl")
le_gu = joblib.load("../../Predict_models/M2/M2_ENCODER/행정구라벨인코더.pkl")
cols_scale = joblib.load("../../Predict_models/M2/M2_ENCODER/독립변수리스트.pkl")
scaler = joblib.load("../../Predict_models/M2/M2_ENCODER/독립변수스케일러.pkl")
le_target = joblib.load("../../Predict_models/M2/M2_ENCODER/타겟변수라벨인코더.pkl")
pm_gu_list =joblib.load("../../Predict_models/M2/M2_ENCODER/PM활용행정구리스트.pkl")


def get_season(month):
    """
    월(1~12) 입력 시 계절 반환 (한국 기준)
    """
    if month in [3, 4, 5]:
        return '봄'
    elif month in [6, 7, 8]:
        return '여름'
    elif month in [9, 10, 11]:
        return '가을'
    elif month in [12, 1, 2]:
        return '겨울'
    else:
        return '가을'

def get_commute_time(hour):
    """
    시간(0~23)을 입력하면 '출근시간', '퇴근시간', '기타'를 반환
    """
    if 7 <= hour <= 10:
        return '출근시간'
    elif 18 <= hour <= 21:
        return '퇴근시간'
    else:
        return '기타'

def class_to_range(pred_class):
    ''' 모델 예측 결과를 범주형 결과로 반환하는 함수 '''
    labels = ['공급과다', '공급다소부족', '공급부족', '공급절대부족', '공급평균']
    pred_class = int(pred_class)
    return labels[pred_class]

def return_M2_result(check=check) :
    weather = get_hourly_weather_seoul_openmeteo()
    check.drop(['연도','강수','습도','풍속','기온'],axis=1, inplace=True)
    weather_df = weather
    weather_df['일시'] = pd.to_datetime(weather_df['일시'])
    kr_holidays = holidays.KR(years=[datetime.now().year, datetime.now().year+1])
    weather_df['요일'] = weather_df['일시'].dt.weekday
    weather_df['공휴일'] = weather_df['일시'].dt.date.isin(kr_holidays).astype(int)
    weather_df['연도'] = weather_df['일시'].dt.year.astype(str)
    weather_df['월'] = weather_df['일시'].dt.month.astype(str)
    weather_df['일'] = weather_df['일시'].dt.day.astype(str)
    weather_df['시'] = weather_df['일시'].dt.hour.astype(str)
    weather_df.drop(['일시','요일'],axis=1, inplace=True)
    df_with_weather = pd.merge(check,weather_df, on=['행정구','월','일','시'])

    df_long['일시'] = pd.to_datetime(df_long['날짜'].astype(str) + ' ' + df_long['시'].astype(str) + ':00:00') # model1 결과
    df_long['연도'] = df_long['일시'].dt.year.astype(str)
    df_long['월'] = df_long['일시'].dt.month.astype(str)
    df_long['일'] = df_long['일시'].dt.day.astype(str)
    df_long['시'] = df_long['일시'].dt.hour.astype(str)
    df_long.drop(['일시'],axis=1, inplace=True)
    df_total = df_with_weather.merge(df_long, on=['행정구','월','일','시','연도']) # ok

    PM_data = df_PM # ['일시','행정구','PM대여량']
    PM_data.columns = ['일시','행정구','1년전_PM대여량']
    PM_data['연도'] = PM_data['일시'].dt.year.astype(str)
    PM_data['월'] = PM_data['일시'].dt.month.astype(str)
    PM_data['일'] = PM_data['일시'].dt.day.astype(str)
    PM_data['시'] = PM_data['일시'].dt.hour.astype(str)
    PM_data.drop(['일시'],axis=1, inplace=True)
    df_PM_data =pd.merge(df_total,PM_data,on=['행정구','월','일','시','연도'])
    df_PM_data['총생활인구수'] = df_PM_data['총생활인구수_1년전']
    df_PM_data['1년전_총생활인구수'] = df_PM_data['총생활인구수_1년전']
    df_PM_data_return = df_PM_data[['월','일','시','행정구']].copy()
    df_PM_data['계절'] = le_season.transform(df_PM_data['계절'].values)
    df_PM_data['출퇴근시간여부'] = le_commute.transform(df_PM_data['출퇴근시간여부'].values)
    df_PM_data['행정구'] = le_gu.transform(df_PM_data['행정구'].values)
    df_PM_data[num_cols] = scaler.transform(df_PM_data[num_cols].values)
    # ['총생활인구수_1년전', '강수', '기온','습도','풍속','대여량_1년전']
    pred = model.predict(df_PM_data[cols_X]).reshape(-1,1)
    df_pred = pd.DataFrame(pred, columns=['예상PM수요'])
    df_pred = df_pred.apply(class_to_range, axis=1)
    # df_PM_data.reset_index(drop=True)
    # df_pred.reset_index(drop=True)
    df_final = pd.concat([df_PM_data_return, df_pred], axis=1) # df_PM_data
    return df_final
# 행정구 날짜 시 예측값 일시 연도 월 일
if __name__ == "__main__" :
    print(return_M2_result())