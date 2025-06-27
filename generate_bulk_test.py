import random
import csv

# 50명의 대량 테스트 데이터 생성
def generate_bulk_test_data():
    headers = ['UID', '이름', '의견', '성과등급', 'KPI점수']
    
    # 다양한 평가 템플릿
    positive_templates = [
        "매우 우수한 성과를 보이고 있으며, 팀에 긍정적인 영향을 미칩니다.",
        "목표를 초과 달성하고 혁신적인 아이디어로 업무 효율을 개선했습니다.",
        "탁월한 리더십과 커뮤니케이션 능력으로 팀을 성공적으로 이끌고 있습니다.",
        "전문성이 뛰어나고 지속적인 학습으로 역량을 향상시키고 있습니다."
    ]
    
    neutral_templates = [
        "평균적인 성과를 보이고 있으며, 일부 영역에서 개선이 필요합니다.",
        "업무는 성실하게 수행하나 창의성과 혁신 면에서 보완이 필요합니다.",
        "기본적인 업무는 잘 처리하지만 리더십 역량 개발이 필요합니다.",
        "안정적인 성과를 유지하고 있으나 도전적인 과제 수행이 부족합니다."
    ]
    
    negative_templates = [
        "업무 성과가 기대에 미치지 못하며 개선 노력이 필요합니다.",
        "커뮤니케이션과 협업에서 어려움을 겪고 있어 지원이 필요합니다.",
        "목표 달성률이 낮고 업무 효율성 개선이 시급합니다.",
        "태도와 마인드셋 개선이 필요하며 적극성이 부족합니다."
    ]
    
    last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
    first_names = ['민수', '지영', '성호', '은지', '준호', '서연', '현우', '수진', '태현', '예진']
    
    data = []
    for i in range(50):
        uid = f"EMP{i+100:03d}"
        name = random.choice(last_names) + random.choice(first_names)
        
        # 성과 분포: 20% 우수, 60% 평균, 20% 개선필요
        rand = random.random()
        if rand < 0.2:  # 우수
            opinion = random.choice(positive_templates)
            grade = random.choice(['S', 'A+', 'A'])
            kpi = random.randint(85, 99)
        elif rand < 0.8:  # 평균
            opinion = random.choice(neutral_templates)
            grade = random.choice(['B+', 'B', 'C+'])
            kpi = random.randint(70, 84)
        else:  # 개선필요
            opinion = random.choice(negative_templates)
            grade = random.choice(['C', 'D'])
            kpi = random.randint(50, 69)
        
        # 추가 의견 덧붙이기
        additional = [
            " 특히 " + random.choice(['업무성과', 'KPI달성', '태도', '커뮤니케이션', '리더십', '전문성']) + " 영역에서 " + 
            random.choice(['뛰어난 역량을', '개선이 필요한 부분을', '안정적인 성과를']) + " 보이고 있습니다.",
            " " + random.choice(['지속적인 성장이', '멘토링이', '교육 프로그램 참여가', '피드백 제공이']) + " 필요합니다."
        ]
        
        opinion += random.choice(additional)
        
        data.append([uid, name, opinion, grade, kpi])
    
    # CSV 파일로 저장
    with open('test_bulk_50.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    print("test_bulk_50.csv 파일이 생성되었습니다.")

# 실행
generate_bulk_test_data()