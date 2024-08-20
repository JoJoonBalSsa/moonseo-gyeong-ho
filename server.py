# app.py
from flask import Flask, request

import requests
import re

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_data():
    data = request.data.decode('utf-8')  # 받은 데이터를 UTF-8로 디코딩
    print(data)
    url = extract_url(data)

    client_ip = request.remote_addr
    download_file(url, client_ip)


    return 'Data received: ' + data


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
  save_path = "~/"

  try:
    response = requests.get(url, stream=True)
    response.raise_for_status()  # 예외 발생 시 HTTPError 발생

    with open(save_path, 'wb') as f:
      for chunk in response.iter_content(chunk_size=8192):
        if chunk:  # filter out keep-alive new chunks
          f.write(chunk)
          
    print(f"파일 다운로드 완료: {save_path}")
    response = requests.post('http://' + client_ip, data={'message': f'Data received successfully from {client_ip}'}, safe=1)
    response.raise_for_status()  # HTTP 상태 코드 검사
    print(f"Success sending to {client_ip}")

  except requests.exceptions.RequestException as e:
    response = requests.post('http://' + client_ip, data={'message': f'Data received successfully from {client_ip}'}, safe=0)
    response.raise_for_status()  # HTTP 상태 코드 검사
    print(f"Error downlding: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)