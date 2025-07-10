
import joblib
import pandas as pd
import numpy as np
import joblib
import holidays
import tensorflow as tf
from datetime import datetime, timedelta
from weather import get_hourly_weather_seoul_openmeteo
from DBMS_lastYear import DBMS_last_year_one_week
from DBMS_lastYear_M2 import fill_missing_timeseries
from model1 import result_df_return
import warnings; 
warnings.filterwarnings('ignore')

df_PM = pd.read_csv(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\PM_data\서울시_시간별_PM_배치_2021_2025.csv")
df_PM.columns =['일시','행정구','PM대여량']

weather = get_hourly_weather_seoul_openmeteo()
lastyear_data = fill_missing_timeseries()
#['연도','월','일','시','행정구','총생활인구수_1년전','대여량_1년전']
model1_result = result_df_return()

feature_cols = ['PM대여량', '1년전_PM대여량', '1년전_총생활인구수', '총생활인구수', '출퇴근시간여부', '시', '주말구분',
    '풍속', '공공자전거대여량', '습도', '기온', '행정구', '월', 'PM대여량_class', '계절', '강수',
    '연도', '공휴일', '일']
num_cols=['총생활인구수_1년전', '강수', '기온','습도','풍속','대여량_1년전']
cols_X = ['연도','월','일','시','행정구','총생활인구수','계절','출퇴근시간여부','주말구분','강수','기온','습도','풍속','공공자전거대여량','공휴일','1년전_총생활인구수','1년전_PM대여량']

model = joblib.load(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\M2_categorical_LGBM.pkl")
pm_gu_list =joblib.load(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\M2_ENCODER\PM활용행정구리스트.pkl")
gu_list = joblib.load(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\M2_ENCODER\서울전역행정구리스트.pkl")
le_season = joblib.load(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\M2_ENCODER\계절라벨인코더.pkl")
le_commute =joblib.load(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\M2_ENCODER\출퇴근시간여부라벨인코더.pkl")
le_gu = joblib.load(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\M2_ENCODER\행정구라벨인코더.pkl")
cols_scale = joblib.load(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\M2_ENCODER\독립변수리스트.pkl")
scaler = joblib.load(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\M2_ENCODER\독립변수스케일러.pkl")
le_target = joblib.load(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\M2_ENCODER\타겟변수라벨인코더.pkl")
pm_gu_list =joblib.load(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Predict_models\M2\M2_ENCODER\PM활용행정구리스트.pkl")

def get_season_num(month):
    if month in [3, 4, 5]:
        return 1  # 봄
    elif month in [6, 7, 8]:
        return 2  # 여름
    elif month in [9, 10, 11]:
        return 3  # 가을
    else:
        return 4  # 겨울
def class_to_range(pred_class):
    ''' 모델 예측 결과를 범주형 결과로 반환하는 함수 '''
    labels = ['공급과다', '공급평균', '공급다소부족', '공급부족', '공급절대부족']
    pred_class = int(pred_class)
    return labels[pred_class]

def predict_result() :
    '''오늘로부터 8일간의 데이터를 predict해서 결과를 반환하는 함수'''
    df_1y = lastyear_data # ['연도','월','일','시','행정구','총생활인구수_1년전','대여량_1년전']
    PM_data = df_PM # ['일시','행정구','PM대여량']
    PM_data.columns = ['일시','행정구','1년전_PM대여량']
    # 현재 시각
    now = datetime.now()

    # 1주일치 시간 list
    this_week = [now + timedelta(days=i) for i in range(8)]

    # 1년 전 1주일치 데이터
    dt_1y = [day.replace(year=day.year - 1) for day in this_week]
    target_dates = [d.date() for d in dt_1y]
    PM_data['일시'] = pd.to_datetime(PM_data['일시'])

    PM_data['연도'] = PM_data['일시'].dt.year.astype(str)
    PM_data['월'] = PM_data['일시'].dt.month.astype(str)
    PM_data['일'] = PM_data['일시'].dt.day.astype(str)
    PM_data['시'] = PM_data['일시'].dt.hour.astype(str)
    
    mask = PM_data['일시'].dt.date.isin(target_dates)
    filtered = PM_data[mask]
    
    
    df_total = df_1y.merge(filtered, on=['행정구','월','일','시','연도'])
    df_total['계절'] = df_total['월'].apply(get_season_num)
    df_total['일시'] = pd.to_datetime(df_total['일시'])
    
    kr_holidays = holidays.KR(years=[datetime.now().year, datetime.now().year+1])
    df_total['요일'] = df_total['일시'].dt.weekday
    df_total['주말구분'] = (df_total['요일'] >= 5).astype(int)
    df_total['공휴일'] = df_total['일시'].dt.date.isin(kr_holidays).astype(int)
    df_total['계절'] = df_total['월'].apply(get_season_num)
    # df_need = df_total[['연도','월','일','시','행정구','총생활인구수','계절','출퇴근시간여부','주말구분','강수','기온','습도','풍속','공공자전거대여량','공휴일','1년전_총생활인구수','1년전_PM대여량']]
    
    weather_df = weather
    # weather.columns = 
    weather_df['일시'] = pd.to_datetime(weather_df['일시'])
    weather_df['월'] = weather_df['일시'].dt.month.astype(str)
    weather_df['일'] = weather_df['일시'].dt.day.astype(str)
    weather_df['시'] = weather_df['일시'].dt.hour.astype(str)
    df_input = weather_df.merge(df_total, on=['행정구','월','일','시', '일시'])

    df_input = df_input[df_input['행정구'].isin(pm_gu_list)]
    model1_result.columns=["행정구","날짜","시","대여량_1년전","일시","연도","월","일"] # 행정구 날짜 시 예측값 일시 연도 월 일
    df_input2 = df_input.merge(model1_result, on=['행정구','월','일','시', '일시'])
#     input_df = pd.DataFrame([input_dict])
    df_input2['행정구'] = le_gu.transform(df_input2['행정구'].values)
    df_input2[num_cols] = scaler.transform(df_input2[num_cols]) 
    # 행정구 일시 강수 습도 풍속 기온 월 일 시 연도 총생활인구수_1년전 대여량_1년전
    # X_input = df_input[cols_X].astype('float32').values
    # pred = model.predict(X_input,verbose=0).round().astype(np.int32)
    return df_input2


if __name__ == "__main__" :
    print(predict_result())
