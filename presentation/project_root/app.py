# app.py
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from model_utils import weather, lastyear_data, model1_result, model2_result
from model1 import save_all_station_top_five
import warnings
import joblib
import os
warnings.filterwarnings('ignore')
global_gu_list = joblib.load("../../Predict_models/M2/M2_ENCODER/서울전역행정구리스트.pkl")
global_pm_gu_list =joblib.load("../../Predict_models/M2/M2_ENCODER/PM활용행정구리스트.pkl")

model1_result = model1_result
model2_result = model2_result
save_all_station_top_five()

# model1_result = pd.DataFrame({'행정구': ['강남구', '강서구'], '공공자전거수요': [123, 456]})
# model2_result = pd.DataFrame({'행정구': ['강남구', '강서구'], 'PM수요': [78, 99]})

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    gu_list = global_pm_gu_list
    if request.method == 'POST':
        gu = request.form['gu']
        # GET 쿼리스트링으로 값 전달
        return redirect(url_for('select_menu', gu=gu))
    return render_template('index.html', gu_list=gu_list)

@app.route('/select')
def select_menu():
    gu = request.args.get('gu')
    table = model2_result[model2_result['행정구'] == gu].to_html()
    return render_template('select_menu.html', table=table, gu=gu)

@app.route('/pm_result')
def pm_result():
    gu = request.args.get('gu')
    df = model2_result[model2_result['행정구'] == gu].copy()
    df.columns = ['월', '일', '시', '행정구', '예상']
    df['월'] = df['월'].astype(str)
    df['일'] = df['일'].astype(str)
    df['date'] = df['월'] + '-' + df['일']
    pivot = df.pivot(index='시', columns='date', values='0')
    table = pivot.to_html(classes='data', border=1)
    return render_template('result.html', table=table, menu='PM 수요 예측', gu=gu)

@app.route('/bike_result')
def bike_result():
    gu = request.args.get('gu')
    df = model1_result[model1_result['행정구'] == gu]
    pivot = df.pivot(index='시', columns='날짜', values='0')
    table = pivot.to_html(index=False, classes='data', border=1)
    return render_template('result.html', table=table, menu='공공자전거 수요 예측', gu=gu)

@app.route('/top5', methods=['GET', 'POST'])
def top5():
    gu_list = global_gu_list
    img_list = []
    gu = None
    if request.method == 'POST':
        gu = request.form['gu']
        # static 폴더 내 해당 행정구 이미지 모두 탐색
        static_folder = os.path.join(app.root_path, 'static')
        img_list = [
            fname for fname in os.listdir(static_folder)
            if fname.startswith(f"{gu}_") and fname.endswith('.png')
        ]
        # 필요시 img_list = sorted(img_list)  # 순서정렬
        return render_template('top5.html', gu_list=gu_list, gu=gu, img_list=img_list)
    return render_template('top5.html', gu_list=gu_list, gu=gu, img_list=img_list)

if __name__ == '__main__':
    app.run(debug=False)
