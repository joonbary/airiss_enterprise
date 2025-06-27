# create_test_data.py
import pandas as pd
import numpy as np
from datetime import datetime

# 테스트 데이터 생성
data = {
    'UID': [f'EMP{str(i).zfill(4)}' for i in range(1, 21)],
    '이름': [f'직원{i}' for i in range(1, 21)],
    '부서': ['인사팀', '개발팀', '영업팀', '기획팀', '재무팀'] * 4,
    '평가의견': [
        '업무 성과가 탁월하며 KPI를 초과 달성했습니다. 적극적인 태도와 뛰어난 커뮤니케이션 능력을 보여줍니다.',
        '전문성이 뛰어나고 창의적인 아이디어로 팀에 기여합니다. 리더십도 우수합니다.',
        '성실하게 업무를 수행하나 커뮤니케이션 개선이 필요합니다.',
        'KPI 달성률이 미흡하며 태도 개선이 필요합니다.',
        '협업 능력이 우수하고 조직 적응력이 뛰어납니다. 전문성 향상 노력이 보입니다.',
    ] * 4,
    '성과등급': ['S', 'A', 'B', 'C', 'B'] * 4,
    '역량점수': np.random.randint(60, 100, 20),
    'KPI달성률': np.random.randint(70, 120, 20),
    '교육이수시간': np.random.randint(10, 50, 20)
}

df = pd.DataFrame(data)

# Excel 파일로 저장
filename = f'AIRISS_테스트데이터_{datetime.now().strftime("%Y%m%d")}.xlsx'
df.to_excel(filename, index=False)
print(f"✅ 테스트 파일 생성 완료: {filename}")
print(f"   - 직원 수: {len(df)}명")
print(f"   - 텍스트 컬럼: 평가의견")
print(f"   - 정량 컬럼: 성과등급, 역량점수, KPI달성률, 교육이수시간")