# app/core/analyzer.py - 전체 구현
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class AIRISSAnalyzer:
    """AIRISS v4.0 하이브리드 분석 엔진"""
    
    def __init__(self):
        self.dimensions = {
            "업무성과": {
                "weight": 0.25,
                "keywords": {
                    "positive": [
                        "우수", "탁월", "뛰어남", "성과", "달성", "완료", "성공", "효율", "생산적", 
                        "목표달성", "초과달성", "품질", "정확", "신속", "완벽", "전문적", "체계적",
                        "성과가", "결과를", "실적이", "완성도", "만족도"
                    ],
                    "negative": [
                        "부족", "미흡", "지연", "실패", "문제", "오류", "늦음", "비효율", 
                        "목표미달", "품질저하", "부정확", "미완성", "부실", "개선", "보완"
                    ]
                }
            },
            "KPI달성": {
                "weight": 0.20,
                "keywords": {
                    "positive": [
                        "KPI달성", "지표달성", "목표초과", "성과우수", "실적우수", "매출증가", 
                        "효율향상", "생산성향상", "수치달성", "성장", "개선", "달성률", "초과"
                    ],
                    "negative": [
                        "KPI미달", "목표미달", "실적부진", "매출감소", "효율저하", 
                        "생산성저하", "수치부족", "하락", "퇴보", "미달"
                    ]
                }
            },
            "태도마인드": {
                "weight": 0.15,
                "keywords": {
                    "positive": [
                        "적극적", "긍정적", "열정", "성실", "책임감", "진취적", "협조적", 
                        "성장지향", "학습의지", "도전정신", "주인의식", "헌신", "열심히", "노력"
                    ],
                    "negative": [
                        "소극적", "부정적", "무관심", "불성실", "회피", "냉소적", 
                        "비협조적", "안주", "현상유지", "수동적", "태도", "마인드"
                    ]
                }
            },
            "커뮤니케이션": {
                "weight": 0.15,
                "keywords": {
                    "positive": [
                        "명확", "정확", "신속", "친절", "경청", "소통", "전달", "이해", 
                        "설득", "협의", "조율", "공유", "투명", "개방적", "의사소통", "원활"
                    ],
                    "negative": [
                        "불명확", "지연", "무시", "오해", "단절", "침묵", "회피", 
                        "독단", "일방적", "폐쇄적", "소통부족", "전달력"
                    ]
                }
            },
            "리더십협업": {
                "weight": 0.10,
                "keywords": {
                    "positive": [
                        "리더십", "팀워크", "협업", "지원", "멘토링", "동기부여", "조율", 
                        "화합", "팀빌딩", "위임", "코칭", "영향력", "협력", "팀플레이"
                    ],
                    "negative": [
                        "독단", "갈등", "비협조", "소외", "분열", "대립", "이기주의", 
                        "방해", "무관심", "고립", "개인주의"
                    ]
                }
            },
            "전문성학습": {
                "weight": 0.08,
                "keywords": {
                    "positive": [
                        "전문", "숙련", "기술", "지식", "학습", "발전", "역량", "능력", 
                        "성장", "향상", "습득", "개발", "전문성", "노하우", "스킬", "경험"
                    ],
                    "negative": [
                        "미숙", "부족", "낙후", "무지", "정체", "퇴보", "무능력", 
                        "기초부족", "역량부족", "실력부족"
                    ]
                }
            },
            "창의혁신": {
                "weight": 0.05,
                "keywords": {
                    "positive": [
                        "창의", "혁신", "아이디어", "개선", "효율화", "최적화", "새로운", 
                        "도전", "변화", "발상", "창조", "혁신적", "독창적", "창조적"
                    ],
                    "negative": [
                        "보수적", "경직", "틀에박힌", "변화거부", "기존방식", "관습적", 
                        "경직된", "고정적", "변화없이"
                    ]
                }
            },
            "조직적응": {
                "weight": 0.02,
                "keywords": {
                    "positive": [
                        "적응", "융화", "조화", "문화", "규칙준수", "윤리", "신뢰", 
                        "안정", "일관성", "성실성", "조직", "회사", "팀에"
                    ],
                    "negative": [
                        "부적응", "갈등", "위반", "비윤리", "불신", "일탈", 
                        "문제행동", "규정위반", "조직과"
                    ]
                }
            }
        }
        
        # 등급 변환 매핑
        self.grade_mappings = {
            'S': 100, 'A': 85, 'B': 70, 'C': 55, 'D': 40,
            'A+': 100, 'A': 95, 'A-': 90,
            'B+': 85, 'B': 80, 'B-': 75,
            'C+': 70, 'C': 65, 'C-': 60,
            'D+': 55, 'D': 50, 'D-': 45, 'F': 30,
            '1': 100, '2': 80, '3': 60, '4': 40, '5': 20,
            '우수': 90, '양호': 75, '보통': 60, '미흡': 45, '부족': 30,
            '최우수': 100, '상': 85, '중': 65, '하': 45
        }
    
    async def analyze_employee(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """개별 직원 분석"""
        uid = data.get("uid", f"unknown_{datetime.now().timestamp()}")
        opinion = data.get("opinion", "")
        
        # 텍스트 분석
        text_scores = await self.analyze_text(opinion)
        
        # 정량 분석
        quant_scores = await self.analyze_quantitative(data)
        
        # 하이브리드 통합
        hybrid_score = self.calculate_hybrid_score(text_scores, quant_scores)
        
        # OK 등급 산정
        ok_grade = self.get_ok_grade(hybrid_score)
        
        # 신뢰도 계산
        confidence = self.calculate_confidence(data, text_scores, quant_scores)
        
        # 인사이트 생성
        insights = await self.generate_insights(hybrid_score, text_scores, quant_scores)
        
        return {
            "uid": uid,
            "hybrid_score": round(hybrid_score, 1),
            "ok_grade": ok_grade["grade"],
            "grade_description": ok_grade["description"],
            "percentile": ok_grade["percentile"],
            "text_analysis": text_scores,
            "quant_analysis": quant_scores,
            "confidence": round(confidence, 1),
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """텍스트 분석 - 8대 영역별 키워드 분석"""
        if not text or text.lower() in ['nan', 'null', '', 'none']:
            return {
                "overall_score": 50.0,
                "dimension_scores": {dim: 50.0 for dim in self.dimensions.keys()},
                "confidence": 0.0
            }
        
        text_lower = text.lower()
        dimension_scores = {}
        
        for dimension, config in self.dimensions.items():
            keywords = config["keywords"]
            
            # 긍정/부정 키워드 매칭
            positive_matches = [kw for kw in keywords["positive"] if kw in text_lower]
            negative_matches = [kw for kw in keywords["negative"] if kw in text_lower]
            
            # 점수 계산
            base_score = 50
            positive_boost = min(len(positive_matches) * 8, 45)
            negative_penalty = min(len(negative_matches) * 10, 40)
            
            # 텍스트 길이 보너스
            text_length = len(text)
            length_bonus = min((text_length - 50) / 100 * 5, 10) if text_length > 50 else 0
            
            final_score = base_score + positive_boost - negative_penalty + length_bonus
            final_score = max(10, min(100, final_score))
            
            dimension_scores[dimension] = {
                "score": round(final_score, 1),
                "positive_matches": positive_matches[:5],
                "negative_matches": negative_matches[:5],
                "confidence": min(len(positive_matches) + len(negative_matches) * 12, 100)
            }
        
        # 가중 평균 계산
        weighted_sum = sum(
            self.dimensions[dim]["weight"] * dimension_scores[dim]["score"] 
            for dim in self.dimensions.keys()
        )
        
        return {
            "overall_score": round(weighted_sum, 1),
            "dimension_scores": {
                dim: data["score"] for dim, data in dimension_scores.items()
            },
            "dimension_details": dimension_scores,
            "confidence": np.mean([d["confidence"] for d in dimension_scores.values()])
        }
    
    async def analyze_quantitative(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """정량 데이터 분석"""
        quant_scores = {}
        total_score = 0
        total_weight = 0
        
        # 정량 데이터 패턴 찾기
        for key, value in data.items():
            if not value or pd.isna(value):
                continue
                
            key_lower = key.lower()
            
            # 점수 관련
            if any(kw in key_lower for kw in ['점수', 'score', '평점', 'rating']):
                score = self.normalize_score(value)
                quant_scores[key] = score
                total_score += score * 0.3
                total_weight += 0.3
            
            # 등급 관련
            elif any(kw in key_lower for kw in ['등급', 'grade', '평가', 'level']):
                score = self.convert_grade_to_score(value)
                quant_scores[key] = score
                total_score += score * 0.4
                total_weight += 0.4
            
            # 달성률/백분율
            elif any(kw in key_lower for kw in ['달성률', '비율', 'rate', '%', 'percent']):
                score = self.normalize_percentage(value)
                quant_scores[key] = score
                total_score += score * 0.2
                total_weight += 0.2
            
            # 횟수/건수
            elif any(kw in key_lower for kw in ['횟수', '건수', 'count', '회', '번']):
                score = self.normalize_count(value)
                quant_scores[key] = score
                total_score += score * 0.1
                total_weight += 0.1
        
        # 최종 점수
        if total_weight > 0:
            final_score = total_score / total_weight
            confidence = min(total_weight * 20, 100)
        else:
            final_score = 50.0
            confidence = 0.0
        
        return {
            "overall_score": round(final_score, 1),
            "detail_scores": quant_scores,
            "data_count": len(quant_scores),
            "confidence": round(confidence, 1),
            "data_quality": self.assess_data_quality(len(quant_scores))
        }
    
    def normalize_score(self, value) -> float:
        """점수 정규화 (0-100)"""
        try:
            score = float(str(value).replace('%', '').replace('점', ''))
            
            if 0 <= score <= 1:
                return score * 100
            elif 0 <= score <= 5:
                return (score - 1) * 25
            elif 0 <= score <= 10:
                return score * 10
            elif 0 <= score <= 100:
                return score
            else:
                return max(0, min(100, score))
        except:
            return 50.0
    
    def convert_grade_to_score(self, grade) -> float:
        """등급을 점수로 변환"""
        if pd.isna(grade) or grade == '':
            return 50.0
        
        grade_str = str(grade).strip().upper()
        
        # 직접 매핑
        if grade_str in self.grade_mappings:
            return float(self.grade_mappings[grade_str])
        
        # 숫자인 경우
        try:
            score = float(grade_str)
            if 0 <= score <= 100:
                return score
        except:
            pass
        
        return 50.0
    
    def normalize_percentage(self, value) -> float:
        """백분율 정규화"""
        try:
            percent_str = str(value).replace('%', '').replace('퍼센트', '')
            percent = float(percent_str)
            
            if 0 <= percent <= 1:
                return percent * 100
            elif 0 <= percent <= 100:
                return percent
            else:
                return max(0, min(100, percent))
        except:
            return 50.0
    
    def normalize_count(self, value) -> float:
        """횟수/건수 정규화"""
        try:
            count = float(str(value).replace('회', '').replace('건', '').replace('번', ''))
            
            if count <= 0:
                return 30.0
            elif count <= 2:
                return 50.0
            elif count <= 5:
                return 70.0
            elif count <= 10:
                return 85.0
            else:
                return 95.0
        except:
            return 50.0
    
    def calculate_hybrid_score(self, text_scores: Dict, quant_scores: Dict) -> float:
        """하이브리드 점수 계산"""
        text_score = text_scores.get("overall_score", 50)
        quant_score = quant_scores.get("overall_score", 50)
        
        # 데이터 품질에 따른 가중치 조정
        if quant_scores.get("data_quality") == "없음":
            text_weight = 0.8
            quant_weight = 0.2
        elif quant_scores.get("data_quality") == "낮음":
            text_weight = 0.7
            quant_weight = 0.3
        else:
            text_weight = 0.6
            quant_weight = 0.4
        
        return text_score * text_weight + quant_score * quant_weight
    
    def get_ok_grade(self, score: float) -> Dict[str, str]:
        """OK 등급 산정"""
        if score >= 95:
            return {
                "grade": "OK★★★",
                "description": "최우수 등급 (TOP 1%)",
                "percentile": "상위 1%"
            }
        elif score >= 90:
            return {
                "grade": "OK★★",
                "description": "우수 등급 (TOP 5%)",
                "percentile": "상위 5%"
            }
        elif score >= 85:
            return {
                "grade": "OK★",
                "description": "우수+ 등급 (TOP 10%)",
                "percentile": "상위 10%"
            }
        elif score >= 80:
            return {
                "grade": "OK A",
                "description": "양호 등급 (TOP 20%)",
                "percentile": "상위 20%"
            }
        elif score >= 75:
            return {
                "grade": "OK B+",
                "description": "양호- 등급 (TOP 30%)",
                "percentile": "상위 30%"
            }
        elif score >= 70:
            return {
                "grade": "OK B",
                "description": "보통 등급 (TOP 40%)",
                "percentile": "상위 40%"
            }
        elif score >= 60:
            return {
                "grade": "OK C",
                "description": "개선필요 등급 (TOP 60%)",
                "percentile": "상위 60%"
            }
        else:
            return {
                "grade": "OK D",
                "description": "집중개선 등급 (하위 40%)",
                "percentile": "하위 40%"
            }
    
    def calculate_confidence(self, data: Dict, text_scores: Dict, quant_scores: Dict) -> float:
        """분석 신뢰도 계산"""
        text_conf = text_scores.get("confidence", 50)
        quant_conf = quant_scores.get("confidence", 0)
        
        # 데이터 완전성 확인
        data_completeness = sum(1 for v in data.values() if v and str(v).strip()) / len(data) * 100
        
        return (text_conf * 0.5 + quant_conf * 0.3 + data_completeness * 0.2)
    
    def assess_data_quality(self, data_count: int) -> str:
        """데이터 품질 평가"""
        if data_count >= 5:
            return "높음"
        elif data_count >= 3:
            return "중간"
        elif data_count >= 1:
            return "낮음"
        else:
            return "없음"
    
    async def generate_insights(self, hybrid_score: float, text_scores: Dict, quant_scores: Dict) -> Dict[str, Any]:
        """분석 인사이트 생성"""
        insights = {
            "strengths": [],
            "improvements": [],
            "recommendations": []
        }
        
        # 강점 분석
        if hybrid_score >= 80:
            insights["strengths"].append("전반적으로 우수한 성과를 보이고 있습니다")
        
        # 8대 영역별 강점/개선점
        dimension_scores = text_scores.get("dimension_scores", {})
        for dim, score in dimension_scores.items():
            if score >= 80:
                insights["strengths"].append(f"{dim} 영역에서 뛰어난 역량을 보입니다")
            elif score < 60:
                insights["improvements"].append(f"{dim} 영역의 개선이 필요합니다")
        
        # 추천사항
        if text_scores["overall_score"] > quant_scores["overall_score"]:
            insights["recommendations"].append("정성적 평가가 우수하므로 실제 성과로 연결시키는 노력이 필요합니다")
        elif quant_scores["overall_score"] > text_scores["overall_score"]:
            insights["recommendations"].append("정량적 성과는 우수하나 소프트 스킬 강화가 필요합니다")
        
        return insights