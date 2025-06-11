import pandas as pd

def convert_csv_encoding(input_file, output_file, from_encoding='cp949', to_encoding='utf-8-sig'):
    try:
        df = pd.read_csv(input_file, encoding=from_encoding)
        df.to_csv(output_file, index=False, encoding=to_encoding)
        print(f"✅ 변환 완료: {input_file} → {output_file}")
    except Exception as e:
        print(f"⚠️ 변환 실패: {e}")

# 정확한 경로 입력
input_file = r'C:\Users\apro\OneDrive\Desktop\AIRISS\AIRISS_평가정제\dummy_sample_20.csv'
output_file = r'C:\Users\apro\OneDrive\Desktop\AIRISS\AIRISS_평가정제\dummy_sample_20_UTF8.csv'

convert_csv_encoding(input_file, output_file)
