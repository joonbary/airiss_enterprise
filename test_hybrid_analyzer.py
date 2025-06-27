# test_hybrid_analyzer.py
import asyncio
import pandas as pd
from app.core.analyzers.hybrid_analyzer import HybridAnalyzer

async def test_analyzer():
    analyzer = HybridAnalyzer()
    
    # 테스트 케이스
    test_cases = [
        {
            'name': '우수 직원 (텍스트+정량 모두 우수)',
            'data': {
                'uid': 'EMP001',
                'opinion': '매우 우수한 성과를 달성했으며, 탁월한 리더십과 적극적인 태도로 팀의 목표를 초과달성했습니다. 전문성이 뛰어나고 창의적인 아이디어로 혁신을 주도했습니다.',
                'row_data': pd.Series({
                    '성과등급': 'A',
                    'KPI달성률': '95%',
                    '역량평가점수': 90
                })
            }
        },
        {
            'name': '보통 직원 (텍스트 우수, 정량 보통)',
            'data': {
                'uid': 'EMP002',
                'opinion': '성실하고 책임감 있게 업무를 수행했으며, 팀워크가 좋고 커뮤니케이션이 원활합니다.',
                'row_data': pd.Series({
                    '성과등급': 'C',
                    'KPI달성률': '70%',
                    '역량평가점수': 65
                })
            }
        },
        {
            'name': '개선필요 직원 (텍스트 부정적, 정량 낮음)',
            'data': {
                'uid': 'EMP003',
                'opinion': '업무 성과가 미흡하고 목표 달성에 실패했습니다. 소극적인 태도로 개선이 필요합니다.',
                'row_data': pd.Series({
                    '성과등급': 'D',
                    'KPI달성률': '50%',
                    '역량평가점수': 45
                })
            }
        }
    ]
    
    print("🔄 AIRISS v4 HybridAnalyzer 통합 테스트\n")
    
    for test in test_cases:
        print(f"\n{'='*70}")
        print(f"📋 테스트: {test['name']}")
        print(f"   직원 ID: {test['data']['uid']}")
        
        result = await analyzer.analyze(test['data'])
        
        print(f"\n🎯 하이브리드 종합 결과:")
        print(f"   종합 점수: {result['hybrid_score']}점")
        print(f"   OK 등급: {result['ok_grade']}")
        print(f"   설명: {result['grade_description']}")
        print(f"   백분위: {result['percentile']}")
        print(f"   신뢰도: {result['hybrid_confidence']}%")
        
        print(f"\n📊 세부 분석 결과:")
        print(f"   텍스트 분석: {result['text_overall_score']}점 (신뢰도 {result['text_confidence']}%)")
        print(f"   정량 분석: {result['quant_overall_score']}점 (신뢰도 {result['quant_confidence']}%)")
        print(f"   데이터 품질: {result['quant_data_quality']}")
        
        print(f"\n⚖️ 분석 구성:")
        composition = result['analysis_composition']
        print(f"   텍스트 가중치: {composition['text_weight']}%")
        print(f"   정량 가중치: {composition['quantitative_weight']}%")
        
        print(f"\n📈 8대 영역 점수:")
        for dimension, score in result['dimension_scores'].items():
            print(f"   {dimension}: {score}점")

if __name__ == "__main__":
    asyncio.run(test_analyzer())