# app.py
from flask import Flask, request, jsonify

import requests
import re

from preprocess_predict import validate_model

app = Flask(__name__)

# 모델 및 스케일러 경로 설정
model_path = './iforest_byte_model.pkl'
scaler_path = './scaler.pkl'


@app.route('/', methods=['POST'])
def receive_data():
    data = request.data.decode('utf-8')  # 받은 데이터를 UTF-8로 디코딩
    print(data)
    url = extract_url(data)

    client_ip = request.remote_addr
    download_file(url, client_ip)

    pdf_folder_path = './sus.pdf'  # 테스트용 PDF 경로 설정
    res = validate_model(model_path, pdf_folder_path, scaler_path)

    if res == 1 :
        response_data = {
            'safe': 1,
        }
        
    else :
        response_data = {
            'safe': 0,
        }
    
    return jsonify(response_data)

def extract_url(data):
    url_pattern = r'https?://\S+'  # 간단한 URL 패턴 예시
    match = re.search(url_pattern, data)
    if match:
        return match.group()
    else:
        return None


def download_file(url, client_ip):
  
  """
  지정된 URL의 파일을 다운로드하여 저장합니다.

  Args:
    url: 파일 다운로드 URL
    save_path: 파일 저장 경로

  Returns:
    None
  """
  save_path = "sus.pdf"

  try:
    response = requests.get(url, stream=True)
    response.raise_for_status()  # 예외 발생 시 HTTPError 발생s

    with open(save_path, 'wb') as f:
      for chunk in response.iter_content(chunk_size=8192):
        if chunk:  # filter out keep-alive new chunks
          f.write(chunk)

    print(f"파일 다운로드 완료: {save_path}")

  except requests.exceptions.RequestException as e:
    print(f"Error downlding: {e}")
    


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)