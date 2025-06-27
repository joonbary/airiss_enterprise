# app/core/analyzers/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAnalyzer(ABC):
    """모든 분석기의 기본 인터페이스"""
    
    @abstractmethod
    async def analyze(self, data: Any) -> Dict[str, Any]:
        """분석 수행"""
        pass
    
    def calculate_grade(self, score: float) -> Dict[str, str]:
        """점수를 OK 등급으로 변환"""
        from .constants import OK_GRADE_SYSTEM
        
        for threshold, grade_info in sorted(OK_GRADE_SYSTEM.items(), reverse=True):
            if score >= threshold:
                return grade_info
        return OK_GRADE_SYSTEM[0]