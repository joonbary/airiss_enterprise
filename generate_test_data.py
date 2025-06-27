#!/usr/bin/env python3
# AIRISS Week 1 테스트용 샘플 데이터 생성기
import pandas as pd
import random
from datetime import datetime

def generate_test_data():
    """AIRISS 시스템 테스트용 샘플 데이터 생성"""
    
    # 50명의 테스트 직원 데이터
    employees = []
    
    # 샘플 직원 이름
    names = [
        "김철수", "이영희", "박민수", "정수현", "최지영", "윤태훈", "강민지", "임상우", "조하은", "송재현",
        "한지수", "오현우", "권소영", "남궁민", "황지훈", "서예린", "노민석", "구하늘", "도승철", "반지은",
        "석지훈", "천서연", "피정우", "하윤정", "공민수", "금영호", "은소라", "동현석", "방지원", "변태영",
        "사지훈", "아름다", "자윤서", "차민호", "카리나", "타준영", "파지수", "하늘별", "갈현우", "날지은",
        "라민수", "마서연", "바정우", "사윤정", "아현석", "자지원", "차태영", "카지훈", "타소라", "파민지"
    ]
    
    # 부서명
    departments = ["전략기획부", "인사부", "리스크관리부", "IT부", "마케팅부", "영업부", "재무부", "준법감시부"]
    
    # 직급
    positions = ["사원", "주임", "대리", "과장", "차장", "부장"]
    
    # 다양한 등급 형식 (AIRISS가 자동 변환 테스트)
    grade_formats = [
        ["S", "A", "B", "C", "D"],
        ["우수", "양호", "보통", "미흡", "부족"],
        ["1", "2", "3", "4", "5"],
        ["A+", "A", "B+", "B", "C"],
        ["95", "87", "73", "61", "45"]  # 점수 형식
    ]
    
    # 샘플 평가 의견
    opinion_templates = [
        "업무 수행 능력이 뛰어나며 적극적인 자세로 임한다. 커뮤니케이션 능력이 우수하고 팀워크를 중시한다.",
        "성실하고 책임감이 강하다. 전문성을 지속적으로 발전시키고 있으며 리더십 잠재력을 보인다.",
        "창의적인 아이디어를 제시하며 문제 해결 능력이 우수하다. 동료들과의 협업도 원활하다.",
        "꼼꼼하고 정확한 업무 처리로 신뢰를 받고 있다. 학습 의지가 강하고 성장 가능성이 높다.",
        "고객 지향적 사고를 가지고 있으며 서비스 마인드가 뛰어나다. 긍정적인 에너지를 전파한다.",
        "분석적 사고력이 뛰어나며 데이터 기반 의사결정을 선호한다. 체계적이고 논리적이다.",
        "변화에 대한 적응력이 좋고 새로운 도전을 즐긴다. 혁신적인 사고로 업무 개선을 이끈다.",
        "안정적이고 일관된 성과를 보여준다. 팀의 중심 역할을 하며 후배 지도에도 열심이다.",
        "글로벌 감각을 갖추고 있으며 외국어 능력이 우수하다. 국제 업무에 적극적으로 참여한다.",
        "IT 기술에 대한 이해도가 높고 디지털 전환에 기여하고 있다. 효율적인 업무 프로세스를 추구한다."
    ]
    
    for i in range(50):
        # 등급 형식 랜덤 선택
        grade_type = random.choice(grade_formats)
        grade = random.choice(grade_type)
        
        # 평가 점수 (다양한 형식)
        score_formats = ["95점", "87점", "73점", "61점", "45점"]
        kpi_score = random.choice(score_formats)
        
        # 달성률 (백분율)
        achievement_rate = f"{random.randint(70, 120)}%"
        
        employee = {
            "UID": f"EMP{i+1:03d}",  # EMP001, EMP002, ...
            "성명": names[i],
            "부서": random.choice(departments),
            "직급": random.choice(positions),
            "평가등급": grade,
            "KPI점수": kpi_score,
            "목표달성률": achievement_rate,
            "근무태도점수": random.randint(70, 100),
            "교육이수점수": random.randint(60, 100),
            "평가의견": random.choice(opinion_templates) + " " + random.choice([
                "향후 더욱 발전할 것으로 기대된다.",
                "지속적인 성장을 위해 노력하고 있다.",
                "팀에 긍정적인 영향을 미치고 있다.",
                "전문성 강화를 위한 노력이 돋보인다.",
                "조직 목표 달성에 기여하고 있다."
            ]),
            "평가일자": "2024-12-01",
            "평가자": f"관리자{random.randint(1, 10)}"
        }
        employees.append(employee)
    
    return pd.DataFrame(employees)

def save_test_files():
    """테스트 파일들을 다양한 형식으로 저장"""
    
    print("🔧 AIRISS 테스트 데이터 생성 중...")
    
    # 테스트 데이터 생성
    df = generate_test_data()
    
    # 디렉토리 생성
    import os
    os.makedirs('test_data', exist_ok=True)
    
    # 1. Excel 파일 (추천)
    excel_file = 'test_data/AIRISS_테스트_데이터_50명.xlsx'
    df.to_excel(excel_file, index=False, sheet_name='직원평가데이터')
    print(f"✅ Excel 파일 생성: {excel_file}")
    
    # 2. CSV 파일 (UTF-8)
    csv_file = 'test_data/AIRISS_테스트_데이터_50명_UTF8.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"✅ CSV(UTF-8) 파일 생성: {csv_file}")
    
    # 3. CSV 파일 (CP949) - 한글 호환성 테스트
    csv_cp949_file = 'test_data/AIRISS_테스트_데이터_50명_CP949.csv'
    df.to_csv(csv_cp949_file, index=False, encoding='cp949')
    print(f"✅ CSV(CP949) 파일 생성: {csv_cp949_file}")
    
    # 4. 소량 테스트용 (10명)
    df_small = df.head(10)
    small_file = 'test_data/AIRISS_소량_테스트_10명.xlsx'
    df_small.to_excel(small_file, index=False, sheet_name='소량테스트')
    print(f"✅ 소량 테스트 파일 생성: {small_file}")
    
    # 5. 대량 테스트용 (500명) - 성능 테스트용
    df_large = pd.concat([df] * 10, ignore_index=True)  # 50명 x 10 = 500명
    # UID 중복 방지
    for i, row in df_large.iterrows():
        df_large.at[i, 'UID'] = f"EMP{i+1:04d}"
    
    large_file = 'test_data/AIRISS_대량_테스트_500명.xlsx'
    df_large.to_excel(large_file, index=False, sheet_name='대량테스트')
    print(f"✅ 대량 테스트 파일 생성: {large_file}")
    
    print("\n🎯 테스트 데이터 생성 완료!")
    print("📁 test_data/ 폴더에 다음 파일들이 생성되었습니다:")
    print("   - AIRISS_테스트_데이터_50명.xlsx (기본 테스트용)")
    print("   - AIRISS_소량_테스트_10명.xlsx (빠른 테스트용)")  
    print("   - AIRISS_대량_테스트_500명.xlsx (성능 테스트용)")
    print("   - CSV 파일들 (인코딩 테스트용)")
    
    print("\n✨ 다음 단계: 생성된 파일로 AIRISS 업로드 테스트를 진행하세요!")
    
    return df

if __name__ == "__main__":
    save_test_files()