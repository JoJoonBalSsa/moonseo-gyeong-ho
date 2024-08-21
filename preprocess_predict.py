import numpy as np
import joblib
import os
import fitz  # PyMuPDF

# PDF 파일에서 바이트 데이터 추출 (200KB 한정)
def extract_bytes_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
    #with fitz.open(pdf_path) as file:
        byte_data = []
        for page_num in range(len(file)):
            page = file.load_page(page_num)
            text = page.get_text("text").encode('utf-8')
            byte_vector = np.frombuffer(text, dtype=np.uint8)
            if len(byte_vector) > 20000:
                byte_vector = byte_vector[:20000]  # 200KB로 자르기
            byte_vector = np.pad(byte_vector, (0, max(0, 20000 - len(byte_vector))), 'constant')
            byte_data.append(byte_vector)
    byte_data = np.array(byte_data)
    return byte_data



def use_model(model_path, scaler_path, pdf_path):
    # iForest 모델 및 스케일러 로드
    iforest = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # PDF에서 바이트 데이터 추출
    bytes_from_pdf = extract_bytes_from_pdf(pdf_path)

    # 데이터 정규화
    byte_data_normalized = scaler.transform(bytes_from_pdf)
    # 모델을 사용한 예측
    predictions = iforest.predict(byte_data_normalized)
    index = []
    # 예측 결과 출력: -1은 이상치, 1은 정상
    for i, pred in enumerate(predictions):
        if pred == -1:
          index.append(i)
    return index

def test():
    model_path = './iforest_byte_model7.pkl'
    scaler_path = './scaler7.pkl'
    pdf_path = './0e419f50ed7a7eeee7436c73acbd2d30N.pdf'  # 테스트용 PDF 경로 설정
    index = use_model(model_path, scaler_path, pdf_path)
    print(index)

test()