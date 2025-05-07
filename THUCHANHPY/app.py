from flask import Flask, render_template
import requests
import json
import matplotlib
matplotlib.use('Agg')  # Dùng backend không cần GUI
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# API URLs
GOLD_API_URL = 'https://www.goldapi.io/api/XAU/USD'
WEATHER_API_URL = 'https://api.open-meteo.com/v1/forecast?latitude=21.0285&longitude=105.8542&current_weather=true'
CURRENCY_API_URL = 'https://v6.exchangerate-api.com/v6/10847939a53a6ec288583b1c/latest/USD'

WEATHER_CODES = {
    0: "Trời quang", 1: "Chủ yếu quang đãng", 2: "Có mây một phần", 3: "Nhiều mây",
    45: "Sương mù", 48: "Sương mù đóng băng", 51: "Mưa phùn nhẹ", 53: "Mưa phùn vừa", 55: "Mưa phùn dày",
    61: "Mưa nhẹ", 63: "Mưa vừa", 65: "Mưa to", 71: "Tuyết nhẹ", 73: "Tuyết vừa", 75: "Tuyết dày", 95: "Giông"
}

@app.route('/')
def index():
    gold = {'rates': {'USD': 'N/A'}}
    weather = {'name': 'Hà Nội', 'weather': [{'description': 'N/A'}], 'current_weather': {'temperature': 'N/A'}}
    currency = {'rates': {'VND': 'N/A'}}
    gold_history = {'years': [2019, 2020, 2021, 2022, 2023], 'prices': [1500, 1700, 1800, 1900, 2000]}
    error = None

    try:
        # Lấy dữ liệu giá vàng
        headers = {'x-access-token': 'goldapi-byh741smadjtb5d-io'}
        gold_response = requests.get(GOLD_API_URL, headers=headers)
        if gold_response.status_code == 200:
            gold_data = gold_response.json()
            if 'price' in gold_data:
                price = gold_data['price']
                gold['rates']['USD'] = price
                gold_history['years'].append(2024)
                gold_history['prices'].append(price)

        # Lấy dữ liệu thời tiết
        weather_response = requests.get(WEATHER_API_URL)
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            if 'current_weather' in weather_data:
                code = weather_data['current_weather'].get('weathercode', 0)
                temp = weather_data['current_weather'].get('temperature', 'N/A')
                desc = WEATHER_CODES.get(code, "Không xác định")
                weather = {
                    'name': 'Hà Nội',
                    'weather': [{'description': desc}],
                    'current_weather': {'temperature': temp}
                }

        # Lấy tỷ giá USD/VND
        currency_response = requests.get(CURRENCY_API_URL)
        if currency_response.status_code == 200:
            currency_data = currency_response.json()
            if 'conversion_rates' in currency_data and 'VND' in currency_data['conversion_rates']:
                currency['rates']['VND'] = currency_data['conversion_rates']['VND']

        # Vẽ biểu đồ
        years = gold_history['years']
        prices = gold_history['prices']
        plt.figure()
        plt.plot(years, prices, marker='o', color='gold')
        plt.title('Biểu đồ giá vàng theo năm')
        plt.xlabel('Năm')
        plt.ylabel('Giá vàng (USD/ounce)')
        plt.grid(True)
        chart_path = os.path.join('static', 'gold_chart.png')
        plt.savefig(chart_path)
        plt.close()

    except Exception as e:
        error = str(e)

    return render_template(
    'index.html',
    gold=gold,
    weather=weather,
    currency=currency,
    gold_history=json.dumps(gold_history),  # ← Cực kỳ quan trọng!
    chart_url='static/gold_chart.png',
    error=error
)
if __name__ == '__main__':
    app.run(debug=True)