import pymysql
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import pandas as pd
from itertools import product

def DBMS_last_year_one_week() :
    '''내일을 기준으로 작년 1주일치 생활인구수와 대여량을 DataFrame으로 반환하는 함수'''
    load_dotenv()
    host = os.getenv('host')
    user = os.getenv('user')
    password = os.getenv('password')
    database = os.getenv('database')
    port = int(os.getenv('port', 3306))

    # 현재 시각
    now = datetime.now()

    # 1주일치 시간 list
    this_week = [now + timedelta(days=i) for i in range(8)]

    # 1년 전 1주일치 데이터
    dt_1y = [day.replace(year=day.year - 1) for day in this_week]

    total_last_week = pd.DataFrame(columns = ['연도','월','일','시','행정구','총생활인구수_1년전','대여량_1년전'])
    # total_last_week = pd.DataFrame(columns = ['year','month','day','hour','district','total_population','rental_count'])
    for data in dt_1y :
        query =f"""
            SELECT *
            FROM basic_data
            WHERE year = {data.year}
                AND month = {data.month}
                AND day = {data.day}
                """

        try:
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            with connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
                whole_data = pd.DataFrame(data)
                using_data = whole_data[['year','month','day','hour','district','total_population','rental_count']]
                using_data.columns = total_last_week.columns
                total_last_week = pd.concat([total_last_week, using_data],axis=0)
        except Exception as e:
            print('에러 발생:', e)
        finally:
            try:
                connection.close()
            except:
                pass
    return total_last_week # 일주일 치 연도, 월, 일, 시, 행정구, 총생활인구수_1년전, 대여량_1년전

data = DBMS_last_year_one_week()

def fill_missing_timeseries(data=data, days=8, key_cols=None, num_cols=None):
    """
    data: DataFrame, 기준이 되는 원본 데이터 (key_cols 모두 포함)
    days: int, 몇 일간의 데이터를 보장할지 (기본값 8일)
    key_cols: list, 시계열 Key가 되는 컬럼 (예: ['월','일','시','행정구'])
    num_cols: list, 결측값 채울 대상 컬럼. None이면 모든 컬럼 채움

    반환값: 누락 구간이 보간된, 중복 없는 DataFrame
    """
    if key_cols is None:
        key_cols = ['월', '일', '시', '행정구']
    if num_cols is None:
        num_cols = [col for col in data.columns if col not in key_cols]
    for col in key_cols:
        data[col] = data[col].astype(str)
    
    # 1. 전체 조합 만들기
    now = datetime.now().date()
    dates = pd.date_range(now, now + timedelta(days=days-1))   # 8일
    hours = list(range(24))
    gus = data['행정구'].unique().tolist()

    full = []
    for dt in dates:
        for h in hours:
            for g in gus:
                full.append({
                    '월': str(dt.month),
                    '일': str(dt.day),
                    '시': str(h),
                    '행정구': str(g)
                })
    full_df = pd.DataFrame(full)

    # 2. 누락행 탐색 및 합치기
    merged = full_df.merge(data, on=key_cols, how='left', indicator=True)
    missing = merged[merged['_merge']=='left_only']
    df_all = pd.concat([data, missing.drop('_merge', axis=1)], ignore_index=True)
    df_all = df_all.sort_values(key_cols).reset_index(drop=True)

    # 3. ffill, bfill 결측치 채우기 (numeric 및 object 모두 적용 가능)
    for col in num_cols:
        df_all[col] = df_all.groupby(['행정구', '시'])[col].ffill()
        df_all[col] = df_all.groupby(['행정구', '시'])[col].bfill()

    # 4. 중복제거 및 정렬
    df_all = df_all.drop_duplicates(subset=key_cols, keep='first')
    df_all = df_all.sort_values(key_cols).reset_index(drop=True)
    return df_all

if __name__ == "__main__" :
    df = DBMS_last_year_one_week()
    test = fill_missing_timeseries()
    print(df)
    print(test)
    print(len(test))