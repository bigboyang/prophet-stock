from flask import Flask, render_template, url_for, jsonify, json, request
import pandas as pd
import numpy as np
import FinanceDataReader as fdr
from fbprophet import Prophet


app = Flask(__name__)

# 인덱스
@app.route('/', methods=['GET','POST'])
def hello_world():  # put application's code here
    ID = 'test'
    return render_template('index.html',test = ID)

# 메인페이지이동
@app.route('/main', methods=['POST'])
def toMain():
    result = request.form['id']


    return render_template('main.html', user=result)


@app.route('/search', methods=['GET'])
def src():
    args = request.args
    stockName = args['stock']
    date = args['date']
    num = int(args['num'])
    print(stockName, date, num)
    print(type(num), ' 타입확인')

    class Stock:
        def getSymbol(self, name):
            # KRX	KRX 전체 종목
            # KOSPI	KOSPI 종목
            # KOSDAQ	KOSDAQ 종목
            # KONEX	KONEX 종목
            # NASDAQ	나스닥 종목
            # NYSE	뉴욕 증권거래소 종목
            # AMEX	AMEX 종목
            # SP500	S&P500 종목
            import FinanceDataReader as fdr
            import pandas as pd
            df_krx = fdr.StockListing('KRX')
            symbols = list(df_krx[df_krx['Name'].isin(name)]['Symbol'])
            return symbols

        def getStock(self, symbol):
            import FinanceDataReader as fdr
            import pandas as pd
            symbol = ''.join(symbol)
            df_inver = fdr.DataReader(symbol)
            df_inver.fillna(method='backfill', inplace=True)
            df_inver.fillna(method='pad', inplace=True)
            df_inver['ds'] = df_inver.index
            df_inver['y'] = df_inver['Close']

            return df_inver

            # 프로펫으로 구현

        def getPredictData(self, stock, forecast_days, date):  # stock df , 예측하고싶은 기간, (학습기준일 비교시작날짜)
            import pandas as pd
            from fbprophet import Prophet
            if forecast_days == None:
                forecast_days = 365
            forecast_days = forecast_days

            prophet_price = Prophet(weekly_seasonality=False, daily_seasonality=False, yearly_seasonality=False,
                                    changepoint_range=1.0)
            prophet_price.add_seasonality(name='weekly', period=10.5, fourier_order=2)
            prophet_price.add_seasonality(name='monthly', period=30.5, fourier_order=5)
            prophet_price.add_seasonality(name='yearly', period=365.5, fourier_order=5)
            if not date == None:
                stock = stock[stock['ds'] >= date]

            prophet_price.fit(stock)
            future = prophet_price.make_future_dataframe(periods=forecast_days,  freq='D')
            forecast = prophet_price.predict(future)
            forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days)


            df1 = stock[['ds', 'Close']]
            df1[['y']] = stock[['Close']]
            forecast[['y']] = forecast[['yhat']]
            df2 = forecast[['ds', 'y', 'yhat_lower', 'yhat_upper']]


            resultdf = pd.concat([df1, df2])
            resultdf = resultdf[['ds','y']]
            resultdf = resultdf.set_index('ds')

            return resultdf

    s = Stock()
    tmp = [stockName]
    sym = s.getSymbol(tmp)
    df = s.getStock(sym)

    oldFutere = s.getPredictData(df, num, date)


    realDates = list(oldFutere.index.strftime('%Y-%m-%d'))
    realPrice = oldFutere['y']

    result = {
        'ds': realDates,
        'y': list(realPrice),
    }
    print(result)

    return result



if __name__ == '__main__':
    app.run()
