import pandas as pd
import numpy as np
import joblib
import holidays
import tensorflow as tf
from datetime import datetime, timedelta
from weather import get_hourly_weather_seoul_openmeteo
from DBMS_lastYear import DBMS_last_year_one_week
import matplotlib.pyplot as plt
plt.rc('font', family = "Malgun Gothic")

weather = get_hourly_weather_seoul_openmeteo()
lastyear_data = DBMS_last_year_one_week()
le = joblib.load('C:/Users/Admin/OneDrive/Desktop/FlowCast/FlowCast/Predict_models/M2/ENCODER_SCALER/labelencoders.pkl')
scaler = joblib.load('C:/Users/Admin/OneDrive/Desktop/FlowCast/FlowCast/Predict_models/M2/ENCODER_SCALER/scaler.pkl')
feature_cols = joblib.load('C:/Users/Admin/OneDrive/Desktop/FlowCast/FlowCast/Predict_models/M2/ENCODER_SCALER/featurecols.pkl')
num_cols = joblib.load('C:/Users/Admin/OneDrive/Desktop/FlowCast/FlowCast/Predict_models/M2/ENCODER_SCALER/numcols.pkl')
model = tf.keras.models.load_model("C:/Users/Admin/OneDrive/Desktop/FlowCast/FlowCast/Predict_models/M2/best_dnn_model_lr.h5")
gu_weight = pd.read_csv(r"C:\Users\Admin\OneDrive\Desktop\FlowCast\FlowCast\Data_Preprocessing\행정구별자전거대여량비중\행정구top5자전거대여량비중.csv")

def predict_bike_demand():
    """
    내일부터 7일간의 자전거 수요를 예측하는 함수, 강남구, 강동구....중구, 중랑구 순으로 0시부터 24시 까지의 데이터를 순서대로 반환
    """

    df_1y = lastyear_data[['월', '일', '시', '행정구', '총생활인구수_1년전', '대여량_1년전']] # 일주일 치 연도, 월, 일, 시, 행정구, 총생활인구수_1년전, 대여량_1년전
    weather_df = weather
    weather_df['일시'] = pd.to_datetime(weather_df['일시'])
    # weather_df['연도'] = weather_df['일시'].dt.year
    weather_df['월'] = weather_df['일시'].dt.month
    weather_df['일'] = weather_df['일시'].dt.day
    weather_df['시'] = weather_df['일시'].dt.hour

    df_total = weather_df.merge(df_1y, on=['행정구','월','일','시'])
    
    kr_holidays = holidays.KR(years=[datetime.now().year, datetime.now().year+1])
    df_total['요일'] = df_total['일시'].dt.weekday
    df_total['주말구분'] = (df_total['요일'] >= 5).astype(int)
    df_total['공휴일'] = df_total['일시'].dt.date.isin(kr_holidays).astype(int)

#     input_df = pd.DataFrame([input_dict])
    df_total['행정구'] = le.transform(df_total['행정구'].values)
    df_total[num_cols] = scaler.transform(df_total[num_cols])
    X_input = df_total[feature_cols].astype('float32').values
    pred = model.predict(X_input,verbose=0).round().astype(np.int32)
    return pred

datas = predict_bike_demand()

def result_df_return(datas=datas) :
    districts = ['강남구',"강동구","강북구", "강서구","관악구","광진구","구로구","금천구","노원구","도봉구","동대문구","동작구","마포구","서대문구","서초구","성동구","성북구","송파구","양천구","영등포구","용산구","은평구","종로구","중구","중랑구"]
    
    base_date = datetime.now()
    num_days = 8
    num_hours = 24
    all_dates = [base_date + timedelta(days=i) for i in range(num_days)]

    date_hour_list = []
    for d in all_dates:
        for h in range(num_hours):
            date_hour_list.append((d.date(), h))

    # datas shape 자동 보정
    datas = np.array(datas).reshape(len(districts), len(date_hour_list))  
    
    df = pd.DataFrame(datas, index=districts, columns=pd.MultiIndex.from_tuples(date_hour_list, names=['날짜', '시']))

    df_long = df.stack(level=[0, 1]).reset_index()
    df_long.columns = ['행정구', '날짜', '시', '예측값']
    df_long['일시'] = pd.to_datetime(df_long['날짜'].astype(str) + ' ' + df_long['시'].astype(str) + ':00:00')
    df_long['연도'] = df_long['일시'].dt.year
    df_long['월'] = df_long['일시'].dt.month
    df_long['일'] = df_long['일시'].dt.day
#     print(df_long.head())
#     print(df_long.shape)  # (3600, 4) => 현재는 7일치로, 4200,4
    return df_long

df = result_df_return()

def check_station_top_five(gu) :
    ''' 행정구를 입력받아 그 행정구의 수요가 높은 5개 역의 비중에 따라 예상 대여량을 그래프로 반환 '''
    
    gu_weight['weight'] = gu_weight['weight'] / 100
    weight_stations = gu_weight[gu_weight['gu'] == gu]
    now = datetime.now().date()
    pred = df
    need_pred = pred[pred['행정구']==gu]
#     selected_gu = gu_weight[gu_weight['gu']==gu][['station','weight']] 
    result_pred = need_pred[need_pred['날짜']==now]
    result = []

    for _, row in result_pred.iterrows():
        for _, srow in weight_stations.iterrows():
            result.append({
                '날짜': row['날짜'],
                '시': row['시'],
                '행정구': row['행정구'],
                'station': srow['station'],
                '예상대여량': round(row['예측값'] * srow['weight'], 2)
            })

    df_station = pd.DataFrame(result)
    station_list = df_station['station'].unique().tolist()
    
    for station in station_list:
        data = df_station[df_station['station']==station]
        plt.figure(figsize=(12, 6))  # 크기 조정

        # Bar chart
        plt.bar(data['시'], data['예상대여량'], color='skyblue', alpha=0.7, label='대여량(예측)')

        # Line chart
        plt.plot(data['시'], data['예상대여량'], c='red', lw=3, marker='o', markersize=8, label='추이')

        # x축 시각화
        plt.xticks([i for i in range(24)], [f'{i}시' for i in range(24)], fontsize=11, rotation=0)
        plt.xlabel('시간(시)', fontsize=14, fontweight='bold')
        plt.ylabel('예상 대여량', fontsize=14, fontweight='bold')

        plt.ylim(0, data['예상대여량'].max() * 1.15)

        # 최대값 라벨 표시
        max_idx = data['예상대여량'].idxmax()
        max_x = data.loc[max_idx, '시']
        max_y = data.loc[max_idx, '예상대여량']
        plt.annotate(f'{max_y:,.0f}', (max_x, max_y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=11, color='red', fontweight='bold')

        plt.title(f'{station}', fontsize=18, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(fname = f'project_root/static/{station}_result.png', dpi=200, bbox_inches='tight')

    return df_station

if __name__ == "__main__" :
    print(result_df_return())
    # check_station_top_five("강서구")


