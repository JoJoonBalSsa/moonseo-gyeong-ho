import requests

def download_file(url, save_path):
    try:
        # GET 요청으로 파일을 가져옴
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 요청이 성공했는지 확인
        
        # 파일을 바이너리 모드로 저장
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    
        print(f"File downloaded successfully and saved as {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")

# 사용 예시
download_file("https://karf.or.kr/wp-content/uploads/2022/03/Download_Sample.pdf", "downloaded_file.pdf")
