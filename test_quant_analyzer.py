# test_quant_analyzer.py
import asyncio
import pandas as pd
from app.core.analyzers.quantitative_analyzer import QuantitativeAnalyzer

async def test_analyzer():
    analyzer = QuantitativeAnalyzer()
    
    # 테스트 데이터
    test_data = pd.DataFrame([
        {
            '직원ID': 'EMP001',
            '성과등급': 'A',
            'KPI달성률': '95%',
            '역량평가점수': 85,
            '교육이수시간': 40,
            '출근율': '98%'
        },
        {
            '직원ID': 'EMP002',
            '성과등급': '우수',
            'KPI달성률': 0.85,
            '역량평가점수': '4.2',  # 5점 만점
            '교육이수시간': 20,
            '출근율': 95
        },
        {
            '직원ID': 'EMP003',
            '성과등급': 'C',
            'KPI달성률': '60%',
            '역량평가점수': 3,  # 5점 만점
            '교육이수시간': 5,
            '출근율': '85%'
        }
    ])
    
    print("🔄 AIRISS v4 QuantitativeAnalyzer 테스트\n")
    
    for idx, row in test_data.iterrows():
        print(f"{'='*60}")
        print(f"직원: {row['직원ID']}")
        
        result = await analyzer.analyze(row)
        
        print(f"\n📊 정량 분석 결과:")
        print(f"   종합 점수: {result['quantitative_score']}")
        print(f"   OK 등급: {result['grade_info']['grade']}")
        print(f"   신뢰도: {result['confidence']}%")
        print(f"   데이터 품질: {result['data_quality']}")
        print(f"   데이터 개수: {result['data_count']}개")
        
        print(f"\n📈 세부 점수:")
        for factor, info in result['contributing_factors'].items():
            print(f"   {factor}: {info['score']}점 (가중치: {info['weight']})")

if __name__ == "__main__":
    asyncio.run(test_analyzer())