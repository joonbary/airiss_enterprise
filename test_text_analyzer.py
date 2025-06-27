# test_text_analyzer.py
import asyncio
from app.core.analyzers.text_analyzer import TextAnalyzer

async def test_analyzer():
    analyzer = TextAnalyzer()
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "긍정적 평가",
            "text": "매우 우수한 성과를 달성했으며, 탁월한 리더십과 적극적인 태도로 팀의 목표를 초과달성했습니다. 전문성이 뛰어나고 창의적인 아이디어로 혁신을 주도했습니다."
        },
        {
            "name": "부정적 평가",
            "text": "업무 성과가 미흡하고 목표 달성에 실패했습니다. 소극적인 태도와 소통 부족으로 팀워크에 문제가 있었으며, 개선이 필요합니다."
        },
        {
            "name": "중립적 평가",
            "text": "평균적인 수준의 업무를 수행했습니다. 특별히 뛰어나거나 부족한 점은 없었습니다."
        },
        {
            "name": "빈 텍스트",
            "text": ""
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"테스트: {test['name']}")
        print(f"텍스트: {test['text'][:100]}...")
        
        result = await analyzer.analyze(test['text'])
        
        print(f"\n📊 분석 결과:")
        print(f"   종합 점수: {result['overall_score']}")
        print(f"   OK 등급: {result['grade_info']['grade']}")
        print(f"   설명: {result['grade_info']['description']}")
        print(f"   신뢰도: {result['confidence']}%")
        
        print(f"\n📈 영역별 점수:")
        for dimension, scores in result['dimension_results'].items():
            print(f"   {dimension}: {scores['score']}점 (긍정: {scores['signals']['positive']}, 부정: {scores['signals']['negative']})")

if __name__ == "__main__":
    asyncio.run(test_analyzer())