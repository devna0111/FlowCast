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
    if len(total_last_week) != 4800 :
        dates = pd.date_range('2024-07-10', '2024-07-17')
        hours = list(range(24))
        gus = total_last_week['행정구'].unique()

        multi_index = pd.MultiIndex.from_product(
            [dates.year, dates.month, dates.day, hours, gus],
            names=['연도', '월', '일', '시', '행정구']
        )
        full_df = pd.DataFrame(index=multi_index).reset_index()

        merged = full_df.merge(total_last_week, on=['연도','월','일','시','행정구'], how='left', indicator=True)
        missing_rows = merged[merged['_merge'] == 'left_only']
        missing_rows = merged[merged['_merge'] == 'left_only']

        missing_rows_unique = missing_rows.drop_duplicates(subset=['연도', '월', '일', '시', '행정구'])
        missing_rows_unique = missing_rows_unique.drop('_merge', axis=1)
        result = pd.concat((total_last_week,missing_rows_unique))
        
        result = result.sort_values(['행정구', '시', '연도', '월', '일']).reset_index(drop=True)

        for col in ['총생활인구수_1년전', '대여량_1년전']:
            result[col] = result.groupby(['행정구', '시'])[col].apply(lambda x: x.fillna(method='ffill'))

        result = result.sort_values(['연도', '월', '일', '시', '행정구']).reset_index(drop=True)

        result = result[['연도', '월', '일', '시', '행정구', '총생활인구수_1년전', '대여량_1년전']]

        return result
    
    return total_last_week # 일주일 치 연도, 월, 일, 시, 행정구, 총생활인구수_1년전, 대여량_1년전

if __name__ == "__main__" :
    data = DBMS_last_year_one_week()
    print(data)
    print(len(data))