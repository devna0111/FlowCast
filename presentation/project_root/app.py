# app.py
import pandas as pd
from flask import Flask, render_template, request
from model_utils import weather, lastyear_data, model1_result, model2_result
from model1 import save_all_station_top_five
import warnings
import dotenv
import openai
import joblib
import os
import matplotlib
matplotlib.use('Agg')  # 파일 저장 전용 백엔드
import matplotlib.pyplot as plt
import io
import base64

plt.rc('font', family="Malgun Gothic")
plt.rc('font', size=30)  # 전체 폰트 크기
plt.rc('axes', titlesize=30)    # 타이틀 폰트 크기
plt.rc('axes', labelsize=28)    # x, y축 라벨 폰트 크기
plt.rc('legend', fontsize=28)   # 범례 폰트 크기
plt.rc('xtick', labelsize=22)   # x축 눈금 폰트 크기
plt.rc('ytick', labelsize=22)   # y축 눈금 폰트 크기
warnings.filterwarnings('ignore')
global_gu_list = joblib.load("../../Predict_models/M2/M2_ENCODER/서울전역행정구리스트.pkl")
global_pm_gu_list =joblib.load("../../Predict_models/M2/M2_ENCODER/PM활용행정구리스트.pkl")
dotenv.load_dotenv()
model1_result = model1_result
model2_result = model2_result
save_all_station_top_five()

# model1_result = pd.DataFrame({'행정구': ['강남구', '강서구'], '공공자전거수요': [123, 456]})
# model2_result = pd.DataFrame({'행정구': ['강남구', '강서구'], 'PM수요': [78, 99]})

app = Flask(__name__)
def summarize_df_with_gpt(df, context="PM 수요 예측"):
    """
    DataFrame을 GPT에 전달해 요약 분석 반환
    """
    table = df.describe()
    # table = df_short.to_markdown(index=False)
    client = openai.OpenAI()
    prompt = f"""
                다음은 {context} 결과 데이터입니다.
                표를 읽고 최대값, 특이점, 최대값 등의 해석을 간단하게 요약해주세요.{table}
                """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # 또는 gpt-4o
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"데이터를 확인하세요. {e}"


@app.route('/', methods=['GET', 'POST'])
def index():
    gu_list = global_gu_list
    pm_gu_list = global_pm_gu_list
    return render_template('index.html', gu_list=gu_list, pm_gu_list=pm_gu_list)

@app.route('/pm_result')
def pm_result():
    gu = request.args.get('gu')
    date = request.args.get('date')
    if gu not in global_pm_gu_list:
        return render_template('result.html', gu=gu, date=date, img_data=None, menu='PM 수요 예측')
    month, day = date.split('-')[1], date.split('-')[2]
    df = model2_result[(model2_result['행정구'] == gu) &
                        (model2_result['월'].astype(str).str.zfill(2) == month) &
                        (model2_result['일'].astype(str).str.zfill(2) == day)].copy()
    df.columns = ['월', '일', '시', '행정구', '예상']

    # 예측값을 중앙값 숫자로 변환 (범주형이면)
    def get_mid(val):
        if '~' in val:
            a, b = val.replace('대','').split('~')
            return (int(a)+int(b))//2
        elif '대' in val:
            return int(val.replace('대',''))
        return 0
    df['예상수'] = df['예상'].apply(get_mid)

    # 최대값
    max_idx = df['예상수'].idxmax()
    max_x = df.loc[max_idx, '시']
    max_y = df.loc[max_idx, '예상수']
    # 추세선
    Q1 = 9; Q2 =24 ; Q3 = 38
    colors = []
    for y in df['예상수']:
        if y <= Q1:
            colors.append('gray')
        elif y <= Q2:
            colors.append('limegreen')
        elif y <= Q3:
            colors.append('orange')
        else:
            colors.append('red')
    plt.figure(figsize=(18,12))
    plt.bar(df['시'], df['예상수'], color=colors, alpha=0.8)
    plt.axhline(Q1, color='orange', linestyle='--', linewidth=2, label='공급 과다')
    plt.axhline(Q2, color='green', linestyle='-', linewidth=2, label='공급 적정 수준')
    plt.axhline(Q3, color='red', linestyle='-.', linewidth=2, label='추가 공급 필요')
    # 최대값 점과 주석
    plt.scatter([max_x], [max_y], color='darkorange', s=120, zorder=5, label='최대값')
    plt.annotate(f"{int(max_y)}", (max_x, max_y),
                textcoords="offset points", xytext=(0,10), ha='center',
                fontsize=11, color='darkorange', fontweight='bold')
    # 추세선
    plt.xticks(df['시'])
    plt.xlabel('시')
    plt.ylabel('PM 대수 (중앙값)')
    plt.title(f"{gu} | {date} 시간대별 PM 수요 예측")
    plt.legend(loc=(1.01,0.8))
    plt.tight_layout()
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png', bbox_inches='tight')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()
    plt.close()

    summary_text = summarize_df_with_gpt(df, context="PM 수요 예측")
    return render_template('result.html', gu=gu, date=date, img_data=img_base64, text=summary_text)

@app.route('/bike_result')
def bike_result():
    gu = request.args.get('gu')
    date = request.args.get('date')
    menu = '공공자전거 수요 예측'
    if date:
        df = model1_result[
            (model1_result['행정구'] == gu) &
            (model1_result['날짜'].astype(str) == date)
        ]
    else:
        df = model1_result[model1_result['행정구'] == gu]

    Q1 = df['예측값'].quantile(0.25)
    Q2 = df['예측값'].quantile(0.5)
    Q3 = df['예측값'].quantile(0.75)
    colors = []
    for y in df['예측값']:
        if y <= Q1:
            colors.append('gray')
        elif y <= Q2:
            colors.append('limegreen')
        elif y <= Q3:
            colors.append('orange')
        else:
            colors.append('red')
    max_idx = df['예측값'].idxmax()
    max_x = df.loc[max_idx, '시']
    max_y = df.loc[max_idx, '예측값']

    plt.figure(figsize=(18,12))
    plt.bar(df['시'], df['예측값'], color=colors, alpha=0.8)
    plt.axhline(Q1, color='orange', linestyle='--', linewidth=2, label='초과 공급 상황')
    plt.axhline(Q2, color='green', linestyle='-', linewidth=2, label='적정 수준')
    plt.axhline(Q3, color='red', linestyle='-.', linewidth=2, label='즉시 공급 필요')
    # 최대값 점과 주석
    plt.scatter([max_x], [max_y], color='darkorange', s=120, zorder=5)
    plt.annotate(f"{int(max_y)}", (max_x, max_y),
                textcoords="offset points", xytext=(0,10), ha='center',
                fontsize=11, color='darkorange', fontweight='bold')
    # 추세선(선형회귀)
    plt.xticks(df['시'])
    plt.xlabel('시')
    plt.ylabel('예상 대여량')
    plt.title(f"{gu} | {date} 시간대별 공공자전거 수요 예측")
    plt.legend(loc=(1.01,0.8))
    plt.tight_layout()
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png', bbox_inches='tight')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()
    plt.close()

    summary_text = summarize_df_with_gpt(df, context="공공자전거 수요 예측")

    return render_template(
        'result.html',
        menu=menu,
        gu=gu,
        date=date,
        img_data=img_base64,
        text=summary_text
    )

@app.route('/top5', methods=['GET', 'POST'])
def top5():
    img_list = []
    gu = request.args.get('gu')
    static_folder = os.path.join(app.root_path, 'static')
    img_list = [
        fname for fname in os.listdir(static_folder)
        if fname.startswith(f"{gu}_") and fname.endswith('.png')
    ]
    return render_template('top5.html',  gu=gu, img_list=img_list)

if __name__ == '__main__':
    app.run(debug=False)
