# app.py
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_data():
    data = request.data.decode('utf-8')  # 받은 데이터를 UTF-8로 디코딩
    print(data)
    return 'Data received: ' + data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)