import pandas as pd
import json

# JSON 파일 로드
with open("response_1748419440178 (1).json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 변환할 데이터 추출
rows = []
for item in data["sample_data"]:
    row = {
        "라인": item["line"],
        "UID": item["raw"]["UID"],
        "의견": item["raw"]["의견"],
        "AI 요약": item["summary"]
    }
    rows.append(row)

# 데이터프레임 생성
df = pd.DataFrame(rows)

# 엑셀로 저장 (encoding 제거)
df.to_excel("AI_분석결과.xlsx", index=False)
print("✅ 엑셀 파일 생성 완료: AI_분석결과.xlsx")
