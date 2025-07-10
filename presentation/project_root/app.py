# app.py

from flask import Flask, render_template, request
from model_utils import predict_by_gu

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        gu = request.form['gu']
        date = request.form['date']
        df_result = predict_by_gu(gu, date)
        table_html = df_result.pivot_table(index='시', columns='station', values='분배대여량', aggfunc='sum').fillna(0).round(1).to_html(classes='data', border=1)
        return render_template('result.html', gu=gu, date=date, table=table_html)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
