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
        return send_file("./output.pdf", as_attachment=True)
    except FileNotFoundError:
        return "File not found!", 404
    
    
@app.route('/sused')
def downloadedfile():
    # 파일 경로를 지정합니다.
    #file_path = f'/{filename}'

    try:
        return send_file("./output.pdf", as_attachment=True)
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
            erase_page_content(pdf_path, output_path, index)  # 인덱스는 배열
            stamp(output_path, stamp_pdf_path, output_path, index)
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