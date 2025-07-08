# 필요 라이브러리 호출
import dotenv
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import requests
import xml.etree.ElementTree as ET
import warnings
import datetime
from bs4 import BeautifulSoup

# 경고창 무시
warnings.simplefilter("ignore")

dotenv.load_dotenv() # API 사용을 위한 인증키 로드
API_KEY = os.getenv('SEOUL_DATA')

# API를 통해 불러올 주요 장소의 이름과 카테고리 체크
df = pd.read_excel('data/서울시 주요 120장소 목록.xlsx')

spot_name = df['AREA_NM'].tolist() # 주요 장소의 이름을 list에 담아  iterable 객체로 for문을 활용해 정보를 수집

import time
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
# 예시 장소
base_output = "seoul_station_population_data.csv"
backup_folder = "backups"

# 백업 폴더 없으면 생성
os.makedirs(backup_folder, exist_ok=True)

def save_data(data_list):
    df = pd.DataFrame(data_list)

    # 기본 데이터에 append
    if not os.path.exists(base_output):
        df.to_csv(base_output, mode='w', index=False, encoding='utf-8-sig')
    else:
        df.to_csv(base_output, mode='a', index=False, encoding='utf-8-sig', header=False)

    # 날짜별로 백업 파일 저장
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    backup_file = os.path.join(backup_folder, f"backup_{timestamp}.csv")
    df.to_csv(backup_file, index=False, encoding='utf-8-sig')

# 30분 간격으로 120일간 반복
for i in range(5760):
    data_list = []

    for spot in [data for data in spot_name if data.endswith('역')]:
        try:
            url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/xml/citydata/1/5/{spot}"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, features='html.parser')

            data = {
                '장소구분': soup.select_one("AREA_NM").text,
                '최소유동인구': soup.select_one("AREA_PPLTN_MIN").text,
                '최대유동인구': soup.select_one("AREA_PPLTN_MAX").text,
                '습도': soup.select_one("HUMIDITY").text,
                '기온': soup.select_one("TEMP").text,
                '날씨': soup.select_one("SKY_STTS").text,
                '미세먼지지수': soup.select_one("AIR_IDX_MVL").text,
                '정보수집시간': soup.select_one("PPLTN_TIME").text,
                '수집시각': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '장소이름': spot,
                '강수량' : soup.select_one("PRECIPITATION").text,
            }
            data_list.append(data)

        except Exception as e:
            print(f"[{spot}] 수집 실패: {e}")

    save_data(data_list)

    print(f"[{i+1}/8760] ✅ 저장 및 백업 완료: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1시간 대기
    time.sleep(900)
    print('----명령 대기중----')
    time.sleep(900)