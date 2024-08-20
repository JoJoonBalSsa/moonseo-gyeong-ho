# app.py
from flask import Flask, request, jsonify, send_file

import requests
import re

from preprocess_predict import use_model

from pathlib import Path
from typing import Union, Literal, List
from PyPDF2 import PdfWriter, PdfReader, PageObject

app = Flask(__name__)

# 모델 및 스케일러 경로 설정
model_path = './iforest_byte_model7.pkl'
scaler_path = './scaler7.pkl'


@app.route('/sus')
def downloadfile():
    # 파일 경로를 지정합니다.
    #file_path = f'/{filename}'

    try:
        return send_file("./sus.pdf", as_attachment=True)
    except FileNotFoundError:
        return "File not found!", 404
    
    
@app.route('/sused')
def downloadedfile():
    # 파일 경로를 지정합니다.
    #file_path = f'/{filename}'

    try:
        return send_file("./sused.pdf", as_attachment=True)
    except FileNotFoundError:
        return "File not found!", 404


@app.route('/', methods=['POST'])
def receive_data():
    data = request.data.decode('utf-8')  # 받은 데이터를 UTF-8로 디코딩
    print(data)
    url = extract_url(data)

    client_ip = request.remote_addr
    download_file(url, client_ip)

    pdf_path = './sus.pdf'  # 테스트용 PDF 경로 설정
    index = use_model(model_path, scaler_path, pdf_path)

    if index == [] :
        response_data = {
            'safe': 1,
            'path' : "sus",
        }
        
    else :
        output_path = "./sused.pdf"
        stamp_pdf_path = "./moonseo_icon.pdf"

        for i in index:
            erase_page_content(pdf_path, output_path, i)  # 인덱스는 배열
            stamp(output_path, stamp_pdf_path, output_path, i)
            pdf_path = output_path

        response_data = {
            'safe': 0,
            'path' : "sused",
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
  save_path = "./sus.pdf"
  params = {
    "table": "block",
    "id": "4092cd2c-1caa-4050-ae52-47616d469416",
    "spaceId": "1555847c-ad04-4775-bf98-dc41a42ab25c",
    "expirationTimestamp": "1724277600000",
    "signature": "JYGwHJmNbM0t7_gwU7SDq9o3UqED9VpS7d_lKoS4l_w",
    "downloadName": "0a0c1a9d853ca6221456b690f826cec7.pdf"
}

  headers = {
        "Host": "file.notion.so",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Cookie": "file_token=v02%3Afile_token%3AMGuAlpEqFzRdJGTSKYtKf4kLV5FWlrv6fqrXYEx_Vk-HAhpoFBjx9ncmS_fPkMVtbVEBFRF1BSWisuektAMqWidICHuPylz_-ohP4kXLHMFa9RNhK0jdVVALeIQ5t_QbwbNrDeii2iU0LEZV2rTQa8AYCSap; amp_af43d4=c5fc077503dd4474b3fe551100961f2e.ZmEyZjZhNDUyNTlmNDg5NjgxNDdiYzVmODEyYTNjYmY=..1i5oo93j8.1i5opslrs.69s.68.6g4; _cioid=fa2f6a45259f48968147bc5f812a3cbf; _gcl_au=1.1.614511954.1723543468; _ga_9ZJ8CB186L=GS1.1.1723543468.1.1.1723543724.60.0.0; _ga=GA1.1.340125454.1723543468; _rdt_uuid=1723543469049.8427512d-c926-4fea-ae09-0eaec91ba9bc; _hjSessionUser_3664679=eyJpZCI6IjEyNzNhMmIwLWRlZjYtNWNiOC1iZWQ4LWJmY2U5ODYzMGM5NyIsImNyZWF0ZWQiOjE3MjM1NDM0Njk2MDksImV4aXN0aW5nIjpmYWxzZX0=; _cfuvid=z13kUUgN29nUXv6Qja1je_JSQCQcyox9rstpZ2gb8V4-1724114043815-0.0.1.1-604800000; __cf_bm=dcj3zdf5Ew_T183_6JHwQnipwMHgBpXRGbl4rogUrzI-1724187598-1.0.1.1-yJSZSYZcrVhNbQt51v.ve8ahrbfWHOglLj8UxaphsA5xDRjfP2e.cs1umHW1AnebloWJ.2fI.dQsXA_ArYrV8g",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }
  try:
    response = requests.get(url, headers=headers, params=params, stream=True)
    response.raise_for_status()  # 예외 발생 시 HTTPError 발생s

    with open(save_path, 'wb') as f:
      for chunk in response.iter_content(chunk_size=8192):
        if chunk:  # filter out keep-alive new chunks
          f.write(chunk)

    print(f"파일 다운로드 완료: {save_path}")

  except requests.exceptions.RequestException as e:
    print(f"Error downlding: {e}")


def erase_page_content(pdf_path, output_path, page_index):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i in range(len(reader.pages)):
        page = reader.pages[i]
        if i in page_index:
            # 새로운 빈 페이지 생성
            empty_page = PageObject.create_blank_page(width=page.mediabox.width, height=page.mediabox.height)
            writer.add_page(empty_page)
        else:
            writer.add_page(page)

    with open(output_path, "wb") as f_out:
        writer.write(f_out)


def stamp(
    content_pdf: Path,
    stamp_pdf: Path,
    pdf_result: Path,
    page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    stamp_reader = PdfReader(stamp_pdf)
    image_page = stamp_reader.pages[0]  # 스탬프 파일의 첫 번째 페이지 사용

    writer = PdfWriter()

    content_reader = PdfReader(content_pdf)
    if page_indices == "ALL":
        page_indices = list(range(0, len(content_reader.pages)))

    for i in range(len(content_reader.pages)):
        content_page = content_reader.pages[i]
        if i in page_indices:
            content_page.merge_page(image_page)  # 지정된 페이지에만 스탬프 추가
        writer.add_page(content_page)  # 모든 페이지 추가

    with open(pdf_result, "wb") as fp:
        writer.write(fp)


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)