# C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\app\core\analyzers\text.py
from typing import Dict, Any, List

class TextAnalyzer:
    """AIRISS 8대 영역 텍스트 분석 엔진"""
    
    def __init__(self):
        self.framework = {
            "업무성과": {
                "keywords": {
                    "positive": ["우수", "탁월", "뛰어남", "성과", "달성", "완료", "성공"],
                    "negative": ["부족", "미흡", "지연", "실패", "문제", "오류"]
                },
                "weight": 0.25
            },
            "KPI달성": {
                "keywords": {
                    "positive": ["KPI달성", "목표초과", "성과우수", "실적우수"],
                    "negative": ["KPI미달", "목표미달", "실적부진"]
                },
                "weight": 0.20
            },
            # ... 나머지 6개 영역
        }
    
    def analyze_text(self, text: str, dimension: str) -> Dict[str, Any]:
        """텍스트에서 긍정/부정 신호를 추출하여 점수 산출"""
        if not text or text.lower() in ['nan', 'null', '']:
            return {"score": 50, "confidence": 0}
        
        keywords = self.framework[dimension]["keywords"]
        text_lower = text.lower()
        
        positive_count = sum(1 for word in keywords["positive"] if word in text_lower)
        negative_count = sum(1 for word in keywords["negative"] if word in text_lower)
        
        # 점수 계산 로직
        base_score = 50
        score = base_score + (positive_count * 8) - (negative_count * 10)
        score = max(10, min(100, score))
        
        return {
            "score": score,
            "confidence": min((positive_count + negative_count) * 15, 100),
            "positive_signals": positive_count,
            "negative_signals": negative_count
        }