import pandas as pd
import re

# 1️⃣ 파일 경로 설정 (파일명은 상황에 맞게 수정)
input_file = 'AI_분석_결과_100명_전체.xlsx'  # AI 요약 포함된 원본 파일
output_file = 'AI_분석_결과_100명_전체_split.xlsx'  # 분리된 파일 저장 이름

# 2️⃣ AI 요약에서 장점/단점/AI 피드백 분리 함수
def extract_parts(text):
    if pd.isna(text) or not isinstance(text, str):
        return '', '', ''
    
    try:
        strengths = re.search(r'\*\*장점\*\*[:\s]*(.*?)(?=\*\*단점\*\*)', text, re.DOTALL).group(1).strip()
    except:
        strengths = ''
    try:
        weaknesses = re.search(r'\*\*단점\*\*[:\s]*(.*?)(?=\*\*AI 피드백\*\*)', text, re.DOTALL).group(1).strip()
    except:
        weaknesses = ''
    try:
        feedback = re.search(r'\*\*AI 피드백\*\*[:\s]*(.*)', text, re.DOTALL).group(1).strip()
    except:
        feedback = ''
    
    return strengths, weaknesses, feedback

# 3️⃣ 엑셀 파일 불러오기
df = pd.read_excel(input_file)

# 4️⃣ 함수 적용하여 컬럼 생성
df[['장점', '단점', 'AI 피드백']] = df['AI 요약'].apply(lambda x: pd.Series(extract_parts(x)))

# 5️⃣ 결과 저장 (encoding 옵션 제거 / pandas 2.x 이상에서 encoding 파라미터 지원X)
df.to_excel(output_file, index=False)

print(f"✅ 완료! '{output_file}' 파일이 생성되었습니다.")
