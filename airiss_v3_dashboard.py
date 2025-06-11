# AIRISS v3.0 - OK금융그룹 AI 인재분석시스템 대시보드 통합버전
# v2.0의 모든 기능 + 개인별 UID 조회 시각화 대시보드 추가
# 파일명: airiss_v3_dashboard.py

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
import json
import logging
import re

# 필수 라이브러리 체크 및 자동 설치 (기존 코드 그대로 + numpy 추가)
def check_and_install_requirements():
    required_packages = [
        'fastapi',
        'uvicorn[standard]', 
        'pandas',
        'openpyxl',
        'python-multipart',
        'jinja2',
        'numpy'  # 정량분석용 추가
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'uvicorn[standard]':
                import uvicorn
            elif package == 'python-multipart':
                import multipart
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"🔧 누락된 패키지 설치 중: {', '.join(missing_packages)}")
        import subprocess
        for package in missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("✅ 모든 패키지 설치 완료!")

# 라이브러리 설치 확인
check_and_install_requirements()

# 기존 imports 그대로 유지
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import io
import uuid
import asyncio
import uvicorn

# 로깅 설정 (그대로 유지)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화 (버전 업데이트)
app = FastAPI(
    title="AIRISS v3.0 - OK금융그룹 완전통합 AI Dashboard System",
    description="OK금융그룹 완전 브랜딩 + 텍스트분석 + 평가등급 정량분석 + 개인별 조회 대시보드 통합 AI 기반 직원 성과/역량 종합 스코어링 시스템",
    version="3.0.0"
)

# 정적 파일 서빙 설정 (그대로 유지)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("✅ 정적 파일 디렉토리 마운트 완료 (/static)")
except Exception as e:
    logger.warning(f"⚠️ 정적 파일 디렉토리 설정 오류: {e}")

# 전역 저장소 (그대로 유지)
class DataStore:
    def __init__(self):
        self.files = {}
        self.jobs = {}
        self.results = {}
    
    def add_file(self, file_id: str, data: Dict):
        self.files[file_id] = data
    
    def get_file(self, file_id: str) -> Optional[Dict]:
        return self.files.get(file_id)
    
    def add_job(self, job_id: str, data: Dict):
        self.jobs[job_id] = data
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        return self.jobs.get(job_id)
    
    def update_job(self, job_id: str, updates: Dict):
        if job_id in self.jobs:
            self.jobs[job_id].update(updates)

store = DataStore()

# AIRISS 8대 영역 완전 설계 (기존 그대로 유지)
AIRISS_FRAMEWORK = {
    "업무성과": {
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
        },
        "weight": 0.25,
        "description": "업무 산출물의 양과 질",
        "color": "#FF5722",
        "icon": "📊"
    },
    "KPI달성": {
        "keywords": {
            "positive": [
                "KPI달성", "지표달성", "목표초과", "성과우수", "실적우수", "매출증가", 
                "효율향상", "생산성향상", "수치달성", "성장", "개선", "달성률", "초과"
            ],
            "negative": [
                "KPI미달", "목표미달", "실적부진", "매출감소", "효율저하", 
                "생산성저하", "수치부족", "하락", "퇴보", "미달"
            ]
        },
        "weight": 0.20,
        "description": "핵심성과지표 달성도",
        "color": "#4A4A4A",
        "icon": "🎯"
    },
    "태도마인드": {
        "keywords": {
            "positive": [
                "적극적", "긍정적", "열정", "성실", "책임감", "진취적", "협조적", 
                "성장지향", "학습의지", "도전정신", "주인의식", "헌신", "열심히", "노력"
            ],
            "negative": [
                "소극적", "부정적", "무관심", "불성실", "회피", "냉소적", 
                "비협조적", "안주", "현상유지", "수동적", "태도", "마인드"
            ]
        },
        "weight": 0.15,
        "description": "업무에 대한 태도와 마인드셋",
        "color": "#F89C26",
        "icon": "🧠"
    },
    "커뮤니케이션": {
        "keywords": {
            "positive": [
                "명확", "정확", "신속", "친절", "경청", "소통", "전달", "이해", 
                "설득", "협의", "조율", "공유", "투명", "개방적", "의사소통", "원활"
            ],
            "negative": [
                "불명확", "지연", "무시", "오해", "단절", "침묵", "회피", 
                "독단", "일방적", "폐쇄적", "소통부족", "전달력"
            ]
        },
        "weight": 0.15,
        "description": "의사소통 능력과 스타일",
        "color": "#B3B3B3",
        "icon": "💬"
    },
    "리더십협업": {
        "keywords": {
            "positive": [
                "리더십", "팀워크", "협업", "지원", "멘토링", "동기부여", "조율", 
                "화합", "팀빌딩", "위임", "코칭", "영향력", "협력", "팀플레이"
            ],
            "negative": [
                "독단", "갈등", "비협조", "소외", "분열", "대립", "이기주의", 
                "방해", "무관심", "고립", "개인주의"
            ]
        },
        "weight": 0.10,
        "description": "리더십과 협업 능력",
        "color": "#FF8A50",
        "icon": "👥"
    },
    "전문성학습": {
        "keywords": {
            "positive": [
                "전문", "숙련", "기술", "지식", "학습", "발전", "역량", "능력", 
                "성장", "향상", "습득", "개발", "전문성", "노하우", "스킬", "경험"
            ],
            "negative": [
                "미숙", "부족", "낙후", "무지", "정체", "퇴보", "무능력", 
                "기초부족", "역량부족", "실력부족"
            ]
        },
        "weight": 0.08,
        "description": "전문성과 학습능력",
        "color": "#6A6A6A",
        "icon": "📚"
    },
    "창의혁신": {
        "keywords": {
            "positive": [
                "창의", "혁신", "아이디어", "개선", "효율화", "최적화", "새로운", 
                "도전", "변화", "발상", "창조", "혁신적", "독창적", "창조적"
            ],
            "negative": [
                "보수적", "경직", "틀에박힌", "변화거부", "기존방식", "관습적", 
                "경직된", "고정적", "변화없이"
            ]
        },
        "weight": 0.05,
        "description": "창의성과 혁신 마인드",
        "color": "#FFA726",
        "icon": "💡"
    },
    "조직적응": {
        "keywords": {
            "positive": [
                "적응", "융화", "조화", "문화", "규칙준수", "윤리", "신뢰", 
                "안정", "일관성", "성실성", "조직", "회사", "팀에"
            ],
            "negative": [
                "부적응", "갈등", "위반", "비윤리", "불신", "일탈", 
                "문제행동", "규정위반", "조직과"
            ]
        },
        "weight": 0.02,
        "description": "조직문화 적응도와 윤리성",
        "color": "#9E9E9E",
        "icon": "🏢"
    }
}

# 🆕 NEW: 정량데이터 분석기 추가 (v2.0 코드 그대로)
class QuantitativeAnalyzer:
    """평가등급, 점수 등 정량데이터 분석 전용 클래스"""
    
    def __init__(self):
        self.grade_mappings = self.setup_grade_mappings()
        self.score_weights = self.setup_score_weights()
        logger.info("✅ 정량데이터 분석기 초기화 완료")
    
    def setup_grade_mappings(self) -> Dict[str, Dict]:
        """다양한 평가등급 형식을 점수로 변환하는 매핑 테이블"""
        return {
            # 5단계 등급
            'S': 100, 'A': 85, 'B': 70, 'C': 55, 'D': 40,
            
            # 영문 등급  
            'A+': 100, 'A': 95, 'A-': 90,
            'B+': 85, 'B': 80, 'B-': 75,
            'C+': 70, 'C': 65, 'C-': 60,
            'D+': 55, 'D': 50, 'D-': 45,
            'F': 30,
            
            # 숫자 등급
            '1': 100, '2': 80, '3': 60, '4': 40, '5': 20,
            '1급': 100, '2급': 80, '3급': 60, '4급': 40, '5급': 20,
            
            # 한글 등급
            '우수': 90, '양호': 75, '보통': 60, '미흡': 45, '부족': 30,
            '최우수': 100, '상': 85, '중': 65, '하': 45,
            
            # 백분위/퍼센트
            '상위10%': 95, '상위20%': 85, '상위30%': 75, 
            '상위50%': 65, '하위50%': 50, '하위30%': 35,
            
            # OK금융그룹 맞춤 등급 (예상)
            'OK★★★': 100, 'OK★★': 90, 'OK★': 80, 
            'OK A': 75, 'OK B+': 70, 'OK B': 65, 'OK C': 55, 'OK D': 40
        }
    
    def setup_score_weights(self) -> Dict[str, float]:
        """정량 데이터 항목별 가중치 설정"""
        return {
            'performance_grade': 0.30,    # 성과평가 등급
            'kpi_score': 0.25,           # KPI 점수
            'competency_grade': 0.20,    # 역량평가 등급  
            'attendance_score': 0.10,    # 근태점수
            'training_score': 0.10,      # 교육이수 점수
            'certificate_score': 0.05    # 자격증/인증 점수
        }
    
    def extract_quantitative_data(self, row: pd.Series) -> Dict[str, Any]:
        """행 데이터에서 정량적 요소 추출"""
        quant_data = {}
        
        # 컬럼명에서 정량 데이터 패턴 찾기
        for col_name, value in row.items():
            col_lower = str(col_name).lower()
            
            # 점수 관련 컬럼 찾기
            if any(keyword in col_lower for keyword in ['점수', 'score', '평점', 'rating']):
                quant_data[f'score_{col_name}'] = self.normalize_score(value)
            
            # 등급 관련 컬럼 찾기  
            elif any(keyword in col_lower for keyword in ['등급', 'grade', '평가', 'level']):
                quant_data[f'grade_{col_name}'] = self.convert_grade_to_score(value)
            
            # 달성률/백분율 관련
            elif any(keyword in col_lower for keyword in ['달성률', '비율', 'rate', '%', 'percent']):
                quant_data[f'rate_{col_name}'] = self.normalize_percentage(value)
            
            # 횟수/건수 관련
            elif any(keyword in col_lower for keyword in ['횟수', '건수', 'count', '회', '번']):
                quant_data[f'count_{col_name}'] = self.normalize_count(value)
                
        return quant_data
    
    def convert_grade_to_score(self, grade_value) -> float:
        """등급을 점수로 변환"""
        if pd.isna(grade_value) or grade_value == '':
            return 50.0  # 기본값
        
        grade_str = str(grade_value).strip().upper()
        
        # 직접 매핑 확인
        if grade_str in self.grade_mappings:
            return float(self.grade_mappings[grade_str])
        
        # 숫자 점수인 경우 (0-100)
        try:
            score = float(grade_str)
            if 0 <= score <= 100:
                return score
            elif 0 <= score <= 5:  # 1-5 척도
                return (score - 1) * 25  # 1->0, 2->25, 3->50, 4->75, 5->100
            elif 0 <= score <= 10:  # 1-10 척도
                return score * 10
        except ValueError:
            pass
        
        # 패턴 매칭
        if '우수' in grade_str or 'excellent' in grade_str.lower():
            return 90.0
        elif '양호' in grade_str or 'good' in grade_str.lower():
            return 75.0
        elif '보통' in grade_str or 'average' in grade_str.lower():
            return 60.0
        elif '미흡' in grade_str or 'poor' in grade_str.lower():
            return 45.0
        
        logger.warning(f"알 수 없는 등급 형식: {grade_value}, 기본값 50 적용")
        return 50.0
    
    def normalize_score(self, score_value) -> float:
        """점수 값 정규화 (0-100 범위로)"""
        if pd.isna(score_value) or score_value == '':
            return 50.0
        
        try:
            score = float(str(score_value).replace('%', '').replace('점', ''))
            
            if 0 <= score <= 1:  # 0-1 범위
                return score * 100
            elif 0 <= score <= 5:  # 1-5 범위
                return (score - 1) * 25
            elif 0 <= score <= 10:  # 1-10 범위
                return score * 10
            elif 0 <= score <= 100:  # 0-100 범위
                return score
            else:
                # 범위 초과시 클리핑
                return max(0, min(100, score))
                
        except (ValueError, TypeError):
            logger.warning(f"점수 변환 실패: {score_value}, 기본값 50 적용")
            return 50.0
    
    def normalize_percentage(self, percent_value) -> float:
        """백분율 정규화"""
        if pd.isna(percent_value) or percent_value == '':
            return 50.0
        
        try:
            # % 기호 제거 후 숫자 추출
            percent_str = str(percent_value).replace('%', '').replace('퍼센트', '')
            percent = float(percent_str)
            
            if 0 <= percent <= 1:  # 0-1 범위 (소수)
                return percent * 100
            elif 0 <= percent <= 100:  # 0-100 범위
                return percent
            else:
                return max(0, min(100, percent))
                
        except (ValueError, TypeError):
            logger.warning(f"백분율 변환 실패: {percent_value}, 기본값 50 적용")
            return 50.0
    
    def normalize_count(self, count_value) -> float:
        """횟수/건수를 점수로 변환 (상대적 평가)"""
        if pd.isna(count_value) or count_value == '':
            return 50.0
        
        try:
            count = float(str(count_value).replace('회', '').replace('건', '').replace('번', ''))
            
            # 임시적으로 로그 스케일 적용 (실제로는 조직 평균과 비교해야 함)
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
                
        except (ValueError, TypeError):
            logger.warning(f"횟수 변환 실패: {count_value}, 기본값 50 적용")
            return 50.0
    
    def calculate_quantitative_score(self, quant_data: Dict[str, float]) -> Dict[str, Any]:
        """정량 데이터들을 종합하여 최종 점수 계산"""
        if not quant_data:
            return {
                "quantitative_score": 50.0,
                "confidence": 0.0,
                "contributing_factors": {},
                "data_quality": "없음"
            }
        
        # 가중평균 계산 (데이터 유형별)
        total_score = 0.0
        total_weight = 0.0
        contributing_factors = {}
        
        for data_key, score in quant_data.items():
            # 데이터 유형별 가중치 적용
            if 'grade_' in data_key:
                weight = 0.4  # 등급 데이터는 높은 가중치
            elif 'score_' in data_key:
                weight = 0.3  # 점수 데이터
            elif 'rate_' in data_key:
                weight = 0.2  # 비율 데이터
            else:
                weight = 0.1  # 기타
            
            total_score += score * weight
            total_weight += weight
            contributing_factors[data_key] = {
                "score": round(score, 1),
                "weight": weight,
                "contribution": round(score * weight, 1)
            }
        
        # 최종 점수 계산
        if total_weight > 0:
            final_score = total_score / total_weight
            confidence = min(total_weight * 20, 100)  # 가중치 합에 따른 신뢰도
        else:
            final_score = 50.0
            confidence = 0.0
        
        # 데이터 품질 평가
        data_count = len(quant_data)
        if data_count >= 5:
            data_quality = "높음"
        elif data_count >= 3:
            data_quality = "중간"
        elif data_count >= 1:
            data_quality = "낮음"
        else:
            data_quality = "없음"
        
        return {
            "quantitative_score": round(final_score, 1),
            "confidence": round(confidence, 1),
            "contributing_factors": contributing_factors,
            "data_quality": data_quality,
            "data_count": data_count
        }

# 기존 AIRISSAnalyzer 클래스 (100% 그대로 유지)
class AIRISSAnalyzer:
    def __init__(self):
        self.framework = AIRISS_FRAMEWORK
        self.openai_available = False
        self.openai = None
        try:
            import openai
            self.openai = openai
            self.openai_available = True
            logger.info("✅ OpenAI 모듈 로드 성공")
        except ImportError:
            logger.warning("⚠️ OpenAI 모듈 없음 - 키워드 분석만 가능")
    
    def analyze_text(self, text: str, dimension: str) -> Dict[str, Any]:
        """텍스트 분석하여 점수 산출 - 기존 알고리즘 그대로"""
        if not text or text.lower() in ['nan', 'null', '', 'none']:
            return {"score": 50, "confidence": 0, "signals": {"positive": 0, "negative": 0, "positive_words": [], "negative_words": []}}
        
        keywords = self.framework[dimension]["keywords"]
        text_lower = text.lower()
        
        # 키워드 매칭 - 부분 매칭도 포함
        positive_matches = []
        negative_matches = []
        
        for word in keywords["positive"]:
            if word in text_lower:
                positive_matches.append(word)
        
        for word in keywords["negative"]:
            if word in text_lower:
                negative_matches.append(word)
        
        positive_count = len(positive_matches)
        negative_count = len(negative_matches)
        
        # 점수 계산 (기존 알고리즘 그대로)
        base_score = 50
        positive_boost = min(positive_count * 8, 45)
        negative_penalty = min(negative_count * 10, 40)
        
        text_length = len(text)
        if text_length > 50:
            length_bonus = min((text_length - 50) / 100 * 5, 10)
        else:
            length_bonus = 0
        
        final_score = base_score + positive_boost - negative_penalty + length_bonus
        final_score = max(10, min(100, final_score))
        
        # 신뢰도 계산
        total_signals = positive_count + negative_count
        base_confidence = min(total_signals * 12, 80)
        length_confidence = min(text_length / 20, 20)
        confidence = min(base_confidence + length_confidence, 100)
        
        return {
            "score": round(final_score, 1),
            "confidence": round(confidence, 1),
            "signals": {
                "positive": positive_count,
                "negative": negative_count,
                "positive_words": positive_matches[:5],
                "negative_words": negative_matches[:5]
            }
        }
    
    def calculate_overall_score(self, dimension_scores: Dict[str, float]) -> Dict[str, Any]:
        """종합 점수 계산 - 기존 알고리즘 그대로"""
        weighted_sum = 0
        total_weight = 0
        
        for dimension, score in dimension_scores.items():
            if dimension in self.framework:
                weight = self.framework[dimension]["weight"]
                weighted_sum += score * weight
                total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 50
        
        # 기존 등급 체계 그대로
        if overall_score >= 95:
            grade = "OK★★★"
            grade_desc = "최우수 등급 (TOP 1%)"
            percentile = "상위 1%"
        elif overall_score >= 90:
            grade = "OK★★"
            grade_desc = "우수 등급 (TOP 5%)"
            percentile = "상위 5%"
        elif overall_score >= 85:
            grade = "OK★"
            grade_desc = "우수+ 등급 (TOP 10%)"
            percentile = "상위 10%"
        elif overall_score >= 80:
            grade = "OK A"
            grade_desc = "양호 등급 (TOP 20%)"
            percentile = "상위 20%"
        elif overall_score >= 75:
            grade = "OK B+"
            grade_desc = "양호- 등급 (TOP 30%)"
            percentile = "상위 30%"
        elif overall_score >= 70:
            grade = "OK B"
            grade_desc = "보통 등급 (TOP 40%)"
            percentile = "상위 40%"
        elif overall_score >= 60:
            grade = "OK C"
            grade_desc = "개선필요 등급 (TOP 60%)"
            percentile = "상위 60%"
        else:
            grade = "OK D"
            grade_desc = "집중개선 등급 (하위 40%)"
            percentile = "하위 40%"
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "grade_description": grade_desc,
            "percentile": percentile,
            "weighted_scores": dimension_scores
        }
    
    async def generate_ai_feedback(self, uid: str, opinion: str, api_key: str = None, model: str = "gpt-3.5-turbo", max_tokens: int = 1200) -> Dict[str, Any]:
        """OpenAI를 사용한 상세 AI 피드백 생성 - 기존 코드 그대로"""
        logger.info(f"AI 피드백 생성 시작: {uid}, API 키 존재: {bool(api_key)}, 모델: {model}")
        
        if not self.openai_available:
            logger.warning("OpenAI 모듈이 설치되지 않음")
            return {
                "ai_strengths": "OpenAI 모듈이 설치되지 않았습니다. 'pip install openai'로 설치해주세요.",
                "ai_weaknesses": "OpenAI 모듈이 설치되지 않았습니다.",
                "ai_feedback": "키워드 기반 분석만 제공됩니다. OpenAI 모듈을 설치하면 상세한 AI 피드백을 받을 수 있습니다.",
                "processing_time": 0,
                "model_used": "none",
                "tokens_used": 0,
                "error": "OpenAI 모듈 미설치"
            }
        
        if not api_key or api_key.strip() == "":
            logger.warning("OpenAI API 키가 제공되지 않음")
            return {
                "ai_strengths": "OpenAI API 키가 제공되지 않았습니다.",
                "ai_weaknesses": "API 키를 입력하면 상세한 개선점 분석을 받을 수 있습니다.",
                "ai_feedback": "키워드 기반 분석만 수행되었습니다. OpenAI API 키를 입력하면 더 정확하고 상세한 피드백을 받을 수 있습니다.",
                "processing_time": 0,
                "model_used": "none",
                "tokens_used": 0,
                "error": "API 키 없음"
            }
        
        if not api_key.startswith('sk-'):
            logger.warning("잘못된 API 키 형식")
            return {
                "ai_strengths": "잘못된 API 키 형식입니다.",
                "ai_weaknesses": "올바른 OpenAI API 키를 입력해주세요.",
                "ai_feedback": "API 키는 'sk-'로 시작해야 합니다.",
                "processing_time": 0,
                "model_used": "none",
                "tokens_used": 0,
                "error": "잘못된 API 키 형식"
            }
        
        start_time = datetime.now()
        
        try:
            client = self.openai.OpenAI(api_key=api_key.strip())
            
            prompt = self.create_ok_prompt(uid, opinion, model, max_tokens)
            
            logger.info(f"OpenAI API 호출 시작: 모델={model}, 토큰={max_tokens}")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 OK금융그룹의 전문 HR 분석가입니다. AIRISS 8대 영역(업무성과, KPI달성, 태도마인드, 커뮤니케이션, 리더십협업, 전문성학습, 창의혁신, 조직적응)을 기반으로 직원 평가를 분석하고 OK금융그룹 인재상에 맞는 구체적이고 실행 가능한 피드백을 제공합니다."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                timeout=30
            )
            
            feedback_text = response.choices[0].message.content.strip()
            logger.info(f"OpenAI API 응답 수신 완료: {len(feedback_text)}자")
            
            strengths, weaknesses, complete_feedback = self.parse_ai_response(feedback_text)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "ai_strengths": strengths,
                "ai_weaknesses": weaknesses,
                "ai_feedback": complete_feedback,
                "processing_time": round(processing_time, 2),
                "model_used": model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else max_tokens,
                "error": None
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            logger.error(f"OpenAI API 오류: {error_msg}")
            
            if "api_key" in error_msg.lower():
                error_detail = "API 키가 잘못되었거나 만료되었습니다."
            elif "quota" in error_msg.lower():
                error_detail = "API 사용량 한도를 초과했습니다."
            elif "model" in error_msg.lower():
                error_detail = f"모델 '{model}'에 접근할 수 없습니다."
            elif "timeout" in error_msg.lower():
                error_detail = "API 응답 시간이 초과되었습니다."
            else:
                error_detail = f"API 오류: {error_msg}"
            
            return {
                "ai_strengths": f"AI 분석 오류: {error_detail}",
                "ai_weaknesses": "AI 분석을 완료할 수 없습니다.",
                "ai_feedback": f"OpenAI API 호출 중 오류가 발생했습니다: {error_detail}",
                "processing_time": round(processing_time, 2),
                "model_used": model,
                "tokens_used": 0,
                "error": error_detail
            }
    
    def create_ok_prompt(self, uid: str, opinion: str, model: str, max_tokens: int) -> str:
        """OK금융그룹 맞춤 AI 프롬프트 생성 - 기존 코드 그대로"""
        return f"""
OK금융그룹 직원 {uid}의 평가 의견을 AIRISS 8대 영역을 기반으로 종합 분석해주세요.

【평가 의견】
{opinion[:1500]}

【AIRISS 8대 영역 (OK금융그룹 가중치)】
1. 업무성과 (25%) - 업무 산출물의 양과 질
2. KPI달성 (20%) - 핵심성과지표 달성도  
3. 태도마인드 (15%) - 업무에 대한 태도와 마인드셋
4. 커뮤니케이션 (15%) - 의사소통 능력과 스타일
5. 리더십협업 (10%) - 리더십과 협업 능력
6. 전문성학습 (8%) - 전문성과 학습능력
7. 창의혁신 (5%) - 창의성과 혁신 마인드
8. 조직적응 (2%) - 조직문화 적응도와 윤리성

【출력 형식】
[장점]
1. 핵심장점1 (관련 AIRISS 영역 명시)
2. 핵심장점2 (관련 AIRISS 영역 명시)
3. 핵심장점3 (관련 AIRISS 영역 명시)

[개선점]
1. 개선점1 (관련 AIRISS 영역 명시)
2. 개선점2 (관련 AIRISS 영역 명시)
3. 개선점3 (관련 AIRISS 영역 명시)

[종합 피드백]
OK금융그룹 인재상과 AIRISS 8대 영역을 종합하여 실행 가능한 피드백을 500-700자로 작성:
- 핵심 강점과 OK금융그룹 내 활용 방안
- 우선 개선 영역과 구체적 실행 방법
- 향후 6개월 발전 계획 및 목표
- OK금융그룹 조직 기여도 향상 방안

반드시 각 섹션을 완전히 작성하고 OK금융그룹 실무에 바로 적용할 수 있도록 구체적으로 작성해주세요.
        """
    
    def parse_ai_response(self, response: str) -> tuple:
        """AI 응답 파싱 - 기존 코드 그대로"""
        try:
            sections = response.split('[')
            
            strengths = ""
            weaknesses = ""
            feedback = ""
            
            for section in sections:
                section = section.strip()
                if section.startswith('장점]'):
                    content = section.replace('장점]', '').strip()
                    if '[' in content:
                        content = content.split('[')[0].strip()
                    strengths = content
                        
                elif section.startswith('개선점]'):
                    content = section.replace('개선점]', '').strip()
                    if '[' in content:
                        content = content.split('[')[0].strip()
                    weaknesses = content
                        
                elif section.startswith('종합 피드백]') or section.startswith('종합피드백]'):
                    content = section.replace('종합 피드백]', '').replace('종합피드백]', '').strip()
                    feedback = content
            
            if not strengths.strip():
                strengths = "AIRISS 분석을 통해 다음과 같은 긍정적 특성이 관찰됩니다."
            if not weaknesses.strip():
                weaknesses = "전반적으로 우수하나, 지속적인 성장을 위한 개선 기회가 있습니다."
            if not feedback.strip():
                feedback = response
            
            strengths = self.clean_text(strengths)
            weaknesses = self.clean_text(weaknesses)
            feedback = self.clean_text(feedback)
                
            return strengths, weaknesses, feedback
            
        except Exception as e:
            logger.error(f"AI 응답 파싱 오류: {e}")
            return "장점 분석 중 오류 발생", "개선점 분석 중 오류 발생", response
    
    def clean_text(self, text: str) -> str:
        """텍스트 정리 - 기존 코드 그대로"""
        if not text:
            return ""
        
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        return text.strip()

# 🆕 NEW: 기존 분석기와 정량 분석기를 통합하는 하이브리드 분석기 (v2.0 그대로)
class AIRISSHybridAnalyzer:
    """텍스트 분석 + 정량 분석 통합 클래스"""
    
    def __init__(self):
        # 기존 텍스트 분석기 (100% 그대로 유지)
        self.text_analyzer = AIRISSAnalyzer()
        
        # 새로운 정량 분석기
        self.quantitative_analyzer = QuantitativeAnalyzer()
        
        # 통합 가중치 설정
        self.hybrid_weights = {
            'text_analysis': 0.6,      # 텍스트 분석 60%
            'quantitative_analysis': 0.4  # 정량 분석 40%
        }
        
        logger.info("✅ AIRISS v3.0 하이브리드 분석기 초기화 완료")
    
    def comprehensive_analysis(self, uid: str, opinion: str, row_data: pd.Series) -> Dict[str, Any]:
        """종합 분석: 텍스트 + 정량 데이터"""
        
        # 1. 기존 텍스트 분석 (100% 그대로)
        text_results = {}
        for dimension in AIRISS_FRAMEWORK.keys():
            text_results[dimension] = self.text_analyzer.analyze_text(opinion, dimension)
        
        text_overall = self.text_analyzer.calculate_overall_score(
            {dim: result["score"] for dim, result in text_results.items()}
        )
        
        # 2. 정량 데이터 분석 (신규)
        quant_data = self.quantitative_analyzer.extract_quantitative_data(row_data)
        quant_results = self.quantitative_analyzer.calculate_quantitative_score(quant_data)
        
        # 3. 하이브리드 점수 계산
        text_weight = self.hybrid_weights['text_analysis']
        quant_weight = self.hybrid_weights['quantitative_analysis']
        
        # 정량 데이터가 없으면 텍스트 분석에 더 의존
        if quant_results["data_quality"] == "없음":
            text_weight = 0.8
            quant_weight = 0.2
        elif quant_results["data_quality"] == "낮음":
            text_weight = 0.7
            quant_weight = 0.3
        
        hybrid_score = (text_overall["overall_score"] * text_weight + 
                       quant_results["quantitative_score"] * quant_weight)
        
        # 4. 통합 신뢰도 계산
        hybrid_confidence = (text_overall.get("confidence", 70) * text_weight + 
                           quant_results["confidence"] * quant_weight)
        
        # 5. 하이브리드 등급 산정
        hybrid_grade_info = self.calculate_hybrid_grade(hybrid_score)
        
        return {
            # 기존 텍스트 분석 결과 (그대로 유지)
            "text_analysis": {
                "overall_score": text_overall["overall_score"],
                "grade": text_overall["grade"],
                "dimension_scores": {dim: result["score"] for dim, result in text_results.items()},
                "dimension_details": text_results
            },
            
            # 새로운 정량 분석 결과
            "quantitative_analysis": quant_results,
            
            # 하이브리드 통합 결과 (핵심!)
            "hybrid_analysis": {
                "overall_score": round(hybrid_score, 1),
                "grade": hybrid_grade_info["grade"],
                "grade_description": hybrid_grade_info["grade_description"],
                "percentile": hybrid_grade_info["percentile"],
                "confidence": round(hybrid_confidence, 1),
                "analysis_composition": {
                    "text_weight": round(text_weight * 100, 1),
                    "quantitative_weight": round(quant_weight * 100, 1)
                }
            },
            
            # 메타 정보
            "analysis_metadata": {
                "uid": uid,
                "analysis_version": "AIRISS v3.0",
                "analysis_timestamp": datetime.now().isoformat(),
                "data_sources": {
                    "text_available": bool(opinion and opinion.strip()),
                    "quantitative_available": bool(quant_data),
                    "quantitative_data_quality": quant_results["data_quality"]
                }
            }
        }
    
    def calculate_hybrid_grade(self, score: float) -> Dict[str, str]:
        """하이브리드 점수를 OK등급으로 변환"""
        if score >= 95:
            return {
                "grade": "OK★★★",
                "grade_description": "최우수 등급 (TOP 1%) - 정량+정성 통합분석",
                "percentile": "상위 1%"
            }
        elif score >= 90:
            return {
                "grade": "OK★★",
                "grade_description": "우수 등급 (TOP 5%) - 정량+정성 통합분석",
                "percentile": "상위 5%"
            }
        elif score >= 85:
            return {
                "grade": "OK★",
                "grade_description": "우수+ 등급 (TOP 10%) - 정량+정성 통합분석",
                "percentile": "상위 10%"
            }
        elif score >= 80:
            return {
                "grade": "OK A",
                "grade_description": "양호 등급 (TOP 20%) - 정량+정성 통합분석",
                "percentile": "상위 20%"
            }
        elif score >= 75:
            return {
                "grade": "OK B+",
                "grade_description": "양호- 등급 (TOP 30%) - 정량+정성 통합분석",
                "percentile": "상위 30%"
            }
        elif score >= 70:
            return {
                "grade": "OK B",
                "grade_description": "보통 등급 (TOP 40%) - 정량+정성 통합분석",
                "percentile": "상위 40%"
            }
        elif score >= 60:
            return {
                "grade": "OK C",
                "grade_description": "개선필요 등급 (TOP 60%) - 정량+정성 통합분석",
                "percentile": "상위 60%"
            }
        else:
            return {
                "grade": "OK D",
                "grade_description": "집중개선 등급 (하위 40%) - 정량+정성 통합분석",
                "percentile": "하위 40%"
            }

# 🆕 하이브리드 분석기 인스턴스 생성
hybrid_analyzer = AIRISSHybridAnalyzer()

# 데이터 모델 (기존에 analysis_mode 추가)
class AnalysisRequest(BaseModel):
    file_id: str
    sample_size: int = 10
    analysis_mode: str = "hybrid"  # "text", "quantitative", "hybrid"
    openai_api_key: Optional[str] = None
    enable_ai_feedback: bool = False
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 1200

# 🆕 NEW: v3.0 메인 페이지 HTML (검색 링크 추가)
@app.get("/", response_class=HTMLResponse)
async def get_main_page():
    """메인 페이지 - OK금융그룹 v3.0 브랜딩 + 대시보드 링크"""
    html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIRISS v3.0 | OK금융그룹 완전통합 AI Dashboard System</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        /* 기존 CSS 그대로 유지 + v3.0 업데이트 */
        @font-face {
            font-family: 'OK';
            src: url('/static/fonts/OKmedium.woff2') format('woff2'),
                 url('/static/fonts/OKmedium.woff') format('woff'),
                 url('/static/fonts/OKmedium.ttf') format('truetype');
            font-weight: 500;
            font-style: normal;
            font-display: swap;
        }
        
        :root {
            --ok-orange: #FF5722;
            --ok-dark-brown: #4A4A4A;
            --ok-yellow: #F89C26;
            --ok-bright-grey: #B3B3B3;
            --ok-white: #FFFFFF;
            --ok-light-grey: #F5F5F5;
            --ok-text-dark: #2C2C2C;
            --ok-text-light: #666666;
            --ok-green: #4CAF50;  /* 하이브리드 강조용 */
            --ok-purple: #9C27B0;  /* v3.0 대시보드용 */
        }
        
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body {
            font-family: 'OK', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, var(--ok-orange) 0%, var(--ok-yellow) 100%);
            min-height: 100vh; 
            color: var(--ok-text-dark);
            line-height: 1.6;
        }
        
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        
        .header {
            text-align: center; 
            color: var(--ok-white); 
            margin-bottom: 40px; 
            padding: 40px 20px;
            position: relative;
        }
        
        .ok-logo {
            font-size: 4rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
            letter-spacing: -2px;
        }
        
        .ok-logo .exclamation {
            color: var(--ok-yellow);
            font-size: 4.5rem;
        }
        
        .header h1 {
            font-size: 2.5rem; 
            font-weight: 700; 
            margin: 15px 0;
            text-shadow: 0 2px 15px rgba(0,0,0,0.3);
        }
        
        .version-badge {
            display: inline-block;
            background: linear-gradient(135deg, var(--ok-purple), #BA68C8);
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 1rem;
            font-weight: 700;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(156, 39, 176, 0.3);
        }
        
        .header .subtitle { 
            font-size: 1.3rem; 
            opacity: 0.95; 
            margin-bottom: 30px;
            font-weight: 300;
        }
        
        .status-badge {
            display: inline-block; 
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px); 
            padding: 12px 24px; 
            border-radius: 25px;
            border: 2px solid rgba(255,255,255,0.3);
            font-weight: 500;
            font-size: 0.9rem;
        }
        
        /* 🆕 NEW: 네비게이션 카드 추가 */
        .nav-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .nav-card {
            background: var(--ok-white);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 40px 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            border: 2px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
            text-align: center;
            text-decoration: none;
            color: inherit;
        }
        
        .nav-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 30px 80px rgba(255, 87, 34, 0.2);
        }
        
        .nav-card.upload-card {
            border-top: 6px solid var(--ok-orange);
        }
        
        .nav-card.dashboard-card {
            border-top: 6px solid var(--ok-purple);
        }
        
        .nav-card h2 {
            font-size: 1.8rem;
            margin-bottom: 15px;
            color: var(--ok-text-dark);
        }
        
        .nav-card i {
            font-size: 3rem;
            margin-bottom: 20px;
        }
        
        .nav-card.upload-card i {
            color: var(--ok-orange);
        }
        
        .nav-card.dashboard-card i {
            color: var(--ok-purple);
        }
        
        .nav-card p {
            color: var(--ok-text-light);
            font-size: 1.1rem;
            line-height: 1.5;
        }
        
        .nav-card .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.9rem;
            font-weight: 700;
            margin-top: 15px;
        }
        
        .nav-card.upload-card .badge {
            background: linear-gradient(135deg, var(--ok-orange), var(--ok-yellow));
            color: white;
        }
        
        .nav-card.dashboard-card .badge {
            background: linear-gradient(135deg, var(--ok-purple), #BA68C8);
            color: white;
        }
        
        .main-grid {
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 30px; 
            margin-bottom: 40px;
        }
        
        @media (max-width: 1024px) { 
            .main-grid { grid-template-columns: 1fr; }
            .nav-grid { grid-template-columns: 1fr; }
        }
        
        .card {
            background: var(--ok-white); 
            backdrop-filter: blur(20px);
            border-radius: 20px; 
            padding: 30px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            border: 2px solid rgba(255,255,255,0.2); 
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--ok-orange), var(--ok-yellow));
        }
        
        .card.hybrid-card::before {
            background: linear-gradient(90deg, var(--ok-green), var(--ok-orange), var(--ok-yellow));
            height: 6px;
        }
        
        .card:hover { 
            transform: translateY(-5px); 
            box-shadow: 0 30px 80px rgba(255, 87, 34, 0.15); 
        }
        
        .card h3 {
            color: var(--ok-text-dark); 
            font-size: 1.5rem; 
            margin-bottom: 20px;
            display: flex; 
            align-items: center; 
            gap: 12px;
            font-weight: 700;
        }
        
        .card h3 i {
            color: var(--ok-orange);
            font-size: 1.3rem;
        }
        
        .hybrid-highlight {
            background: linear-gradient(135deg, #e8f5e8, #f1f8e9);
            border: 2px solid var(--ok-green);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
        }
        
        .hybrid-highlight h4 {
            color: var(--ok-green);
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .dimensions-grid {
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px; 
            margin-top: 20px;
        }
        
        .dimension-card {
            background: linear-gradient(135deg, var(--ok-light-grey), var(--ok-white)); 
            border: 2px solid var(--ok-bright-grey);
            border-radius: 12px; 
            padding: 16px; 
            text-align: center; 
            transition: all 0.3s ease;
            position: relative; 
            overflow: hidden;
        }
        
        .dimension-card::before {
            content: ''; 
            position: absolute; 
            top: 0; 
            left: 0; 
            right: 0; 
            height: 4px;
            background: var(--color);
        }
        
        .dimension-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-color: var(--color);
        }
        
        .dimension-card h4 {
            font-size: 0.9rem; 
            font-weight: 700; 
            margin-bottom: 8px; 
            color: var(--ok-text-dark);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        
        .dimension-card p { 
            font-size: 0.8rem; 
            color: var(--ok-text-light); 
            line-height: 1.4; 
            font-weight: 300;
        }
        
        .dimension-card .weight {
            position: absolute; 
            top: 8px; 
            right: 8px; 
            background: var(--color);
            color: var(--ok-white); 
            font-size: 0.7rem; 
            padding: 3px 8px; 
            border-radius: 12px;
            font-weight: 700;
        }
        
        .upload-area {
            border: 3px dashed var(--ok-bright-grey); 
            border-radius: 16px; 
            padding: 40px 20px;
            text-align: center; 
            background: linear-gradient(135deg, var(--ok-light-grey), var(--ok-white));
            transition: all 0.3s ease; 
            cursor: pointer; 
            position: relative; 
            overflow: hidden;
        }
        
        .upload-area:hover {
            border-color: var(--ok-orange); 
            background: linear-gradient(135deg, #fff3e0, #fafafa);
        }
        
        .upload-area.dragover {
            border-color: var(--ok-yellow); 
            background: linear-gradient(135deg, #fff8e1, #f3e5f5);
            transform: scale(1.02);
        }
        
        .upload-area input[type="file"] {
            position: absolute; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%;
            opacity: 0; 
            cursor: pointer;
        }
        
        .upload-content { pointer-events: none; }
        .upload-content i { 
            font-size: 3rem; 
            color: var(--ok-orange); 
            margin-bottom: 15px; 
        }
        
        .upload-content h4 {
            color: var(--ok-text-dark);
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .upload-content p {
            color: var(--ok-text-light);
            font-weight: 300;
        }
        
        .btn {
            background: linear-gradient(135deg, var(--ok-orange), var(--ok-yellow)); 
            color: var(--ok-white);
            border: none; 
            padding: 14px 28px; 
            border-radius: 12px; 
            font-size: 1rem;
            font-weight: 700; 
            cursor: pointer; 
            transition: all 0.3s ease;
            text-decoration: none; 
            display: inline-block; 
            position: relative;
            overflow: hidden;
            font-family: 'OK', sans-serif;
        }
        
        .btn:hover {
            transform: translateY(-2px); 
            box-shadow: 0 10px 30px rgba(255, 87, 34, 0.4);
        }
        
        .btn:active { transform: translateY(0); }
        
        .btn:disabled {
            background: var(--ok-bright-grey); 
            cursor: not-allowed; 
            transform: none; 
            box-shadow: none;
        }
        
        .btn-success { 
            background: linear-gradient(135deg, #4CAF50, #66BB6A); 
        }
        .btn-success:hover { 
            box-shadow: 0 10px 30px rgba(76, 175, 80, 0.4); 
        }
        
        .btn-dashboard {
            background: linear-gradient(135deg, var(--ok-purple), #BA68C8);
        }
        .btn-dashboard:hover {
            box-shadow: 0 10px 30px rgba(156, 39, 176, 0.4);
        }
        
        .result-card {
            background: linear-gradient(135deg, #e8f5e8, #f1f8e9); 
            border: 2px solid #c8e6c9;
            border-radius: 12px; 
            padding: 20px; 
            margin: 20px 0; 
            animation: slideInUp 0.5s ease;
        }
        
        .error-card {
            background: linear-gradient(135deg, #ffebee, #fce4ec); 
            border: 2px solid #f8bbd9;
            border-radius: 12px; 
            padding: 20px; 
            margin: 20px 0; 
            animation: slideInUp 0.5s ease;
        }
        
        .stats-grid {
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px; 
            margin: 20px 0;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.9); 
            border-radius: 12px; 
            padding: 20px;
            text-align: center; 
            border: 2px solid rgba(255, 87, 34, 0.1);
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-2px); 
            border-color: rgba(255, 87, 34, 0.3);
        }
        
        .stat-number {
            font-size: 2.2rem; 
            font-weight: 700;
            color: var(--ok-orange);
            margin-bottom: 5px;
        }
        
        .stat-label { 
            color: var(--ok-text-light); 
            font-size: 0.9rem; 
            font-weight: 500; 
        }
        
        .progress-container { 
            margin: 20px 0; 
            display: none; 
        }
        
        .progress-bar {
            background: var(--ok-bright-grey); 
            border-radius: 10px; 
            height: 8px;
            overflow: hidden; 
            position: relative;
        }
        
        .progress-fill {
            background: linear-gradient(90deg, var(--ok-orange), var(--ok-yellow)); 
            height: 100%;
            width: 0%; 
            transition: width 0.3s ease; 
            position: relative;
        }
        
        .progress-fill::after {
            content: ''; 
            position: absolute; 
            top: 0; 
            left: 0; 
            right: 0; 
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 2s infinite;
        }
        
        .analysis-controls {
            display: grid; 
            grid-template-columns: 1fr 1fr 1fr; 
            gap: 20px; 
            margin: 20px 0;
        }
        
        .form-group { 
            display: flex; 
            flex-direction: column; 
            gap: 8px; 
        }
        
        .form-group label { 
            font-weight: 700; 
            color: var(--ok-text-dark);
            font-size: 0.9rem;
        }
        
        select, input[type="number"], input[type="password"] {
            padding: 12px; 
            border: 2px solid var(--ok-bright-grey); 
            border-radius: 8px;
            font-size: 1rem; 
            transition: border-color 0.3s ease;
            font-family: 'OK', sans-serif;
        }
        
        select:focus, input[type="number"]:focus, input[type="password"]:focus {
            outline: none; 
            border-color: var(--ok-orange);
            box-shadow: 0 0 0 3px rgba(255, 87, 34, 0.1);
        }
        
        .log-container {
            background: var(--ok-dark-brown); 
            color: var(--ok-white); 
            border-radius: 12px; 
            padding: 20px;
            font-family: 'Monaco', 'Menlo', monospace; 
            font-size: 0.9rem;
            max-height: 300px; 
            overflow-y: auto; 
            margin: 20px 0; 
            display: none;
        }
        
        .log-entry {
            margin-bottom: 5px; 
            opacity: 0; 
            animation: fadeInLog 0.3s ease forwards;
        }
        
        .log-timestamp { 
            color: var(--ok-yellow); 
            margin-right: 10px; 
        }
        
        .full-width { 
            grid-column: 1 / -1; 
        }
        
        .ai-settings {
            background: linear-gradient(135deg, #fff3e0, #f3e5f5); 
            padding: 25px;
            border-radius: 15px; 
            margin: 25px 0; 
            border: 2px solid var(--ok-orange);
        }
        
        .ai-toggle {
            display: flex; 
            align-items: center; 
            gap: 15px; 
            cursor: pointer;
            padding: 15px; 
            border-radius: 10px; 
            background: rgba(255,255,255,0.8);
            border: 2px solid transparent; 
            transition: all 0.3s ease;
        }
        
        .ai-toggle:hover {
            background: rgba(255,255,255,0.95); 
            border-color: var(--ok-orange);
        }
        
        .ai-toggle input[type="checkbox"] {
            width: 20px; 
            height: 20px; 
            accent-color: var(--ok-orange);
        }
        
        .ai-status {
            display: inline-block; 
            padding: 8px 16px; 
            border-radius: 20px;
            font-size: 0.9rem; 
            font-weight: 700; 
            margin-left: auto;
        }
        
        .ai-status.enabled { 
            background: #e8f5e8; 
            color: #2e7d32; 
        }
        .ai-status.disabled { 
            background: #ffebee; 
            color: #c62828; 
        }
        
        .ai-advanced-settings {
            margin-top: 20px; 
            padding: 20px; 
            background: rgba(255,255,255,0.6);
            border-radius: 12px; 
            border: 2px solid var(--ok-yellow);
        }
        
        .cost-estimate {
            background: #fff8e1; 
            border: 2px solid var(--ok-yellow); 
            border-radius: 8px;
            padding: 15px; 
            margin: 15px 0; 
            font-size: 0.9rem;
        }
        
        .cost-estimate strong { 
            color: var(--ok-orange); 
        }
        
        @keyframes slideInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        @keyframes fadeInLog { 
            to { opacity: 1; } 
        }
        
        .download-section {
            text-align: center; 
            padding: 30px;
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            border-radius: 16px; 
            margin-top: 20px;
        }
        
        .features-list { 
            list-style: none; 
            margin: 15px 0; 
        }
        
        .features-list li { 
            padding: 5px 0; 
            color: var(--ok-text-light); 
            font-size: 0.9rem; 
        }
        
        .features-list li::before { 
            content: '✅'; 
            margin-right: 8px; 
        }
        
        @media (max-width: 768px) {
            .ok-logo {
                font-size: 3rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .analysis-controls {
                grid-template-columns: 1fr;
            }
            
            .card {
                padding: 20px;
            }
            
            .dimensions-grid {
                grid-template-columns: 1fr 1fr;
            }
            
            .nav-card {
                padding: 30px 20px;
            }
        }
        
        @media (max-width: 480px) {
            .dimensions-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- OK금융그룹 v3.0 브랜드 헤더 -->
        <div class="header">
            <div class="ok-logo">
                OK<span class="exclamation">!</span>
            </div>
            <h1>AIRISS v3.0</h1>
            <div class="version-badge">
                🚀 완전통합 대시보드 버전
            </div>
            <div class="subtitle">AI-Powered Employee Performance & Competency Complete Dashboard System</div>
            <div class="status-badge">
                <i class="fas fa-check-circle"></i> 분석 + 업로드 + 개인조회 + 시각화 • 완전통합 플랫폼 • Version 3.0
            </div>
        </div>
        
        <!-- 🆕 NEW: 네비게이션 그리드 -->
        <div class="nav-grid">
            <!-- 데이터 분석 카드 -->
            <a href="#upload-section" class="nav-card upload-card" onclick="scrollToSection('upload-section')">
                <i class="fas fa-chart-line"></i>
                <h2>데이터 분석</h2>
                <p>Excel/CSV 파일을 업로드하여 AIRISS v3.0 하이브리드 분석을 실행하세요</p>
                <div class="badge">분석 시작하기</div>
            </a>
            
            <!-- 개인별 조회 카드 -->
            <a href="/search" class="nav-card dashboard-card">
                <i class="fas fa-user-chart"></i>
                <h2>개인별 조회</h2>
                <p>완료된 분석 결과에서 개별 직원의 성과를 시각적으로 확인하세요</p>
                <div class="badge">🆕 대시보드 조회</div>
            </a>
        </div>
        
        <div class="main-grid" id="upload-section">
            <!-- AIRISS 8대 분석 영역 카드 -->
            <div class="card">
                <h3><i class="fas fa-chart-line"></i> AIRISS 8대 분석 영역</h3>
                <div class="dimensions-grid">
                    <div class="dimension-card" style="--color: #FF5722;">
                        <div class="weight">25%</div>
                        <h4>📊 업무성과</h4>
                        <p>업무 산출물의 양과 질</p>
                    </div>
                    <div class="dimension-card" style="--color: #4A4A4A;">
                        <div class="weight">20%</div>
                        <h4>🎯 KPI달성</h4>
                        <p>핵심성과지표 달성도</p>
                    </div>
                    <div class="dimension-card" style="--color: #F89C26;">
                        <div class="weight">15%</div>
                        <h4>🧠 태도마인드</h4>
                        <p>업무 태도와 마인드셋</p>
                    </div>
                    <div class="dimension-card" style="--color: #B3B3B3;">
                        <div class="weight">15%</div>
                        <h4>💬 커뮤니케이션</h4>
                        <p>의사소통 능력</p>
                    </div>
                    <div class="dimension-card" style="--color: #FF8A50;">
                        <div class="weight">10%</div>
                        <h4>👥 리더십협업</h4>
                        <p>리더십과 협업 능력</p>
                    </div>
                    <div class="dimension-card" style="--color: #6A6A6A;">
                        <div class="weight">8%</div>
                        <h4>📚 전문성학습</h4>
                        <p>전문성과 학습능력</p>
                    </div>
                    <div class="dimension-card" style="--color: #FFA726;">
                        <div class="weight">5%</div>
                        <h4>💡 창의혁신</h4>
                        <p>창의성과 혁신 마인드</p>
                    </div>
                    <div class="dimension-card" style="--color: #9E9E9E;">
                        <div class="weight">2%</div>
                        <h4>🏢 조직적응</h4>
                        <p>조직문화 적응도</p>
                    </div>
                </div>
            </div>
            
            <!-- 파일 업로드 카드 -->
            <div class="card">
                <h3><i class="fas fa-cloud-upload-alt"></i> 데이터 업로드</h3>
                
                <div class="hybrid-highlight">
                    <h4><i class="fas fa-magic"></i> AIRISS v3.0 하이브리드 분석</h4>
                    <p><strong>텍스트 분석</strong> (의견, 피드백) + <strong>정량 분석</strong> (평가등급, 점수)</p>
                    <ul style="margin: 10px 0; padding-left: 20px; color: #2e7d32;">
                        <li>평가등급: S, A, B, C, D / 우수, 양호, 보통</li>
                        <li>점수 데이터: 0-100점, 1-5점, 백분율</li>
                        <li>KPI 달성률, 근태점수, 교육이수 등</li>
                        <li>지능형 융합으로 신뢰도 향상!</li>
                        <li>🆕 분석 후 개인별 대시보드 조회 가능</li>
                    </ul>
                </div>
                
                <div class="upload-area" id="uploadArea">
                    <input type="file" id="fileInput" accept=".csv,.xlsx,.xls" multiple>
                    <div class="upload-content">
                        <i class="fas fa-file-upload"></i>
                        <h4>평가데이터를 드래그하거나 클릭하여 선택하세요</h4>
                        <p>Excel (.xlsx, .xls) 또는 CSV 파일을 지원합니다<br>
                        <small>💡 텍스트(의견) + 등급/점수 컬럼 모두 포함 권장</small></p>
                    </div>
                </div>
                <div id="uploadResult"></div>
                <button class="btn" onclick="processUpload()" id="uploadBtn" disabled>
                    <i class="fas fa-magic"></i> v3.0 하이브리드 분석 시작
                </button>
            </div>
        </div>
        
        <!-- 분석 설정 (기존 코드 그대로 유지) -->
        <div class="card full-width" id="analysisCard" style="display: none;">
            <h3><i class="fas fa-cogs"></i> AIRISS v3.0 분석 설정</h3>
            <div class="analysis-controls">
                <div class="form-group">
                    <label for="sampleSize">분석 샘플 수</label>
                    <select id="sampleSize">
                        <option value="10">10개 (빠른 테스트)</option>
                        <option value="25" selected>25개 (표준)</option>
                        <option value="50">50개 (상세)</option>
                        <option value="100">100개 (정밀)</option>
                        <option value="all">전체 데이터</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="analysisMode">🆕 분석 모드</label>
                    <select id="analysisMode">
                        <option value="text">텍스트 분석만</option>
                        <option value="quantitative">정량 분석만</option>
                        <option value="hybrid" selected>하이브리드 통합분석 (추천)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="hybridWeight">하이브리드 가중치</label>
                    <select id="hybridWeight">
                        <option value="balanced">균형 (텍스트60% + 정량40%)</option>
                        <option value="text_heavy">텍스트 중심 (텍스트80% + 정량20%)</option>
                        <option value="quant_heavy">정량 중심 (텍스트40% + 정량60%)</option>
                        <option value="adaptive" selected>적응형 (데이터 품질에 따라 자동조정)</option>
                    </select>
                </div>
            </div>
            
            <!-- AI 설정 섹션 -->
            <div class="ai-settings">
                <h4 style="margin-bottom: 20px; color: var(--ok-text-dark); font-weight: 700;">
                    <i class="fas fa-robot" style="color: var(--ok-orange);"></i> AI 피드백 설정
                </h4>
                
                <div class="ai-toggle" onclick="toggleAISettings()">
                    <input type="checkbox" id="enableAI" onclick="event.stopPropagation();">
                    <div style="flex: 1;">
                        <strong>OpenAI GPT를 사용한 상세 AI 피드백</strong>
                        <p style="margin: 5px 0 0 0; color: var(--ok-text-light); font-size: 0.9rem;">
                            하이브리드 분석 결과를 바탕으로 OK금융그룹 인재상에 맞는 정확하고 구체적인 개인별 피드백
                        </p>
                    </div>
                    <div class="ai-status disabled" id="aiStatus">비활성화</div>
                </div>
                
                <div id="aiAdvancedSettings" class="ai-advanced-settings" style="display: none;">
                    <div class="analysis-controls" style="grid-template-columns: 1fr 1fr;">
                        <div class="form-group">
                            <label for="openaiModel">AI 모델 선택</label>
                            <select id="openaiModel" onchange="updateCostEstimate()">
                                <option value="gpt-3.5-turbo" selected>GPT-3.5 Turbo (빠름, 저비용)</option>
                                <option value="gpt-4-turbo">GPT-4 Turbo (느림, 고품질)</option>
                                <option value="gpt-4">GPT-4 (균형)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="maxTokens">응답 길이</label>
                            <select id="maxTokens" onchange="updateCostEstimate()">
                                <option value="800">간단 (800토큰)</option>
                                <option value="1200" selected>표준 (1200토큰)</option>
                                <option value="1500">상세 (1500토큰)</option>
                                <option value="2000">완전 (2000토큰)</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group" style="margin-top: 20px;">
                        <label for="openaiKey">
                            <i class="fas fa-key"></i> OpenAI API 키
                            <span style="color: #e53e3e;">*</span>
                        </label>
                        <input type="password" id="openaiKey" placeholder="sk-proj-..." 
                               style="width: 100%;" onchange="validateApiKey()">
                        <small style="color: var(--ok-text-light); margin-top: 8px; display: block;">
                            <i class="fas fa-shield-alt"></i> API 키는 안전하게 처리되며 서버에 저장되지 않습니다
                        </small>
                    </div>
                    
                    <div class="cost-estimate" id="costEstimate">
                        <strong>💰 예상 비용:</strong> 25개 샘플 기준 약 $0.10 (GPT-3.5 Turbo, 1200토큰)
                    </div>
                </div>
            </div>
            
            <button class="btn btn-success" onclick="startAnalysis()" id="analyzeBtn">
                <i class="fas fa-rocket"></i> AIRISS v3.0 하이브리드 분석 실행
            </button>
            
            <div class="progress-container" id="progressContainer">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <p id="progressText">분석 준비 중...</p>
            </div>
            
            <div class="log-container" id="logContainer"></div>
            
            <div id="analysisResult"></div>
        </div>
        
        <!-- 결과 다운로드 -->
        <div class="card full-width download-section" id="downloadCard" style="display: none;">
            <h3><i class="fas fa-download"></i> OK금융그룹 AIRISS v3.0 분석 결과</h3>
            <div id="downloadContent"></div>
            
            <!-- 🆕 NEW: 개인별 조회 안내 -->
            <div style="margin-top: 30px; padding: 25px; background: linear-gradient(135deg, #f3e5f5, #e1bee7); border-radius: 15px; border: 2px solid var(--ok-purple);">
                <h4 style="color: var(--ok-purple); margin-bottom: 15px;">
                    <i class="fas fa-user-chart"></i> 분석 완료! 이제 개인별 상세 조회가 가능합니다
                </h4>
                <p style="margin-bottom: 20px; color: #4A148C;">
                    방금 완료된 분석 결과를 바탕으로 개별 직원의 성과를 시각적 대시보드로 확인할 수 있습니다.
                </p>
                <a href="/search" class="btn btn-dashboard" style="font-size: 1.1rem; padding: 16px 32px;">
                    <i class="fas fa-search"></i> 개인별 대시보드 조회하기
                </a>
            </div>
        </div>
    </div>

    <script>
        // 전역 변수 (기존 코드 그대로)
        let currentFileData = null;
        let analysisJobId = null;
        
        // 네비게이션 함수
        function scrollToSection(sectionId) {
            document.getElementById(sectionId).scrollIntoView({ behavior: 'smooth' });
        }
        
        // 유틸리티 함수 (기존 코드 그대로)
        function formatNumber(num) {
            return new Intl.NumberFormat('ko-KR').format(num);
        }
        
        function getCurrentTime() {
            return new Date().toLocaleTimeString('ko-KR');
        }
        
        function addLog(message) {
            const logContainer = document.getElementById('logContainer');
            logContainer.style.display = 'block';
            
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `<span class="log-timestamp">[${getCurrentTime()}]</span> ${message}`;
            
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        function updateProgress(percentage, text) {
            const progressContainer = document.getElementById('progressContainer');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            progressContainer.style.display = 'block';
            progressFill.style.width = percentage + '%';
            progressText.textContent = text;
        }
        
        // AI 설정 관련 함수들 (기존 코드 그대로)
        function toggleAISettings() {
            const checkbox = document.getElementById('enableAI');
            const settings = document.getElementById('aiAdvancedSettings');
            const status = document.getElementById('aiStatus');
            
            checkbox.checked = !checkbox.checked;
            
            if (checkbox.checked) {
                settings.style.display = 'block';
                status.textContent = '활성화';
                status.className = 'ai-status enabled';
                addLog('🤖 AI 피드백 기능 활성화됨 (AIRISS v3.0 하이브리드 분석 기반)');
                updateCostEstimate();
            } else {
                settings.style.display = 'none';
                status.textContent = '비활성화';
                status.className = 'ai-status disabled';
                addLog('📊 하이브리드 분석만 사용됨');
            }
        }
        
        function validateApiKey() {
            const apiKey = document.getElementById('openaiKey').value.trim();
            const input = document.getElementById('openaiKey');
            
            if (apiKey === '') {
                input.style.borderColor = 'var(--ok-bright-grey)';
                return false;
            } else if (!apiKey.startsWith('sk-')) {
                input.style.borderColor = '#e53e3e';
                addLog('⚠️ API 키는 "sk-"로 시작해야 합니다');
                return false;
            } else {
                input.style.borderColor = 'var(--ok-orange)';
                addLog('✅ API 키 형식이 올바릅니다');
                return true;
            }
        }
        
        function updateCostEstimate() {
            const model = document.getElementById('openaiModel').value;
            const tokens = parseInt(document.getElementById('maxTokens').value);
            const sampleSize = document.getElementById('sampleSize').value;
            const samples = sampleSize === 'all' ? 100 : parseInt(sampleSize);
            
            let costPerToken = 0;
            if (model === 'gpt-3.5-turbo') {
                costPerToken = 0.002 / 1000;
            } else if (model === 'gpt-4-turbo') {
                costPerToken = 0.01 / 1000;
            } else if (model === 'gpt-4') {
                costPerToken = 0.03 / 1000;
            }
            
            const estimatedCost = samples * tokens * costPerToken;
            const costText = estimatedCost < 0.01 ? '< $0.01' : `${estimatedCost.toFixed(2)}`;
            
            document.getElementById('costEstimate').innerHTML = `
                <strong>💰 예상 비용:</strong> ${samples}개 샘플 기준 약 ${costText} (${model}, ${tokens}토큰)
                <br><small>하이브리드 분석 결과를 바탕으로 한 AI 피드백 비용입니다</small>
            `;
        }
        
        // 파일 업로드 관련 (기존 코드 그대로)
        function setupFileUpload() {
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            
            // 드래그 앤 드롭
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    handleFileSelection();
                }
            });
            
            // 파일 선택
            fileInput.addEventListener('change', handleFileSelection);
        }
        
        function handleFileSelection() {
            const fileInput = document.getElementById('fileInput');
            const uploadBtn = document.getElementById('uploadBtn');
            const file = fileInput.files[0];
            
            if (file) {
                document.getElementById('uploadResult').innerHTML = `
                    <div class="result-card">
                        <h4><i class="fas fa-file-check"></i> 파일 선택됨</h4>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-number">${file.name}</div>
                                <div class="stat-label">파일명</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${(file.size / 1024 / 1024).toFixed(2)}MB</div>
                                <div class="stat-label">파일 크기</div>
                            </div>
                        </div>
                        <p style="text-align: center; margin-top: 15px; color: var(--ok-green); font-weight: 600;">
                            <i class="fas fa-magic"></i> AIRISS v3.0이 텍스트와 정량데이터를 자동으로 감지합니다
                        </p>
                    </div>
                `;
                uploadBtn.disabled = false;
                addLog(`✅ 파일 선택: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB)`);
                addLog('🔍 AIRISS v3.0이 하이브리드 분석을 위한 데이터 구조를 분석할 준비가 되었습니다');
            }
        }
        
        // 기존 모든 함수들 (processUpload, displayUploadResult, showAnalysisCard, startAnalysis, pollAnalysisProgress, displayAnalysisResult, showDownloadCard, downloadResult) 그대로 유지
        
        async function processUpload() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('파일을 선택해주세요.');
                return;
            }
            
            const uploadBtn = document.getElementById('uploadBtn');
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> v3.0 데이터 분석 중...';
            
            addLog('🚀 OK금융그룹 AIRISS v3.0 서버로 파일 업로드 시작...');
            addLog('🔬 텍스트 데이터와 정량 데이터 동시 감지 진행중...');
            updateProgress(20, '하이브리드 데이터 분석 중...');
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    currentFileData = result;
                    addLog(`✅ 업로드 성공: ${result.total_records}개 레코드 감지`);
                    
                    // v3.0 전용 로깅
                    if (result.quantitative_columns && result.quantitative_columns.length > 0) {
                        addLog(`📊 정량 데이터 발견: ${result.quantitative_columns.length}개 컬럼`);
                        addLog(`🎯 하이브리드 분석 가능: 텍스트 + 정량 통합분석 권장`);
                    } else {
                        addLog(`📝 텍스트 데이터 중심: 기존 분석방식 적용`);
                    }
                    
                    updateProgress(100, '데이터 분석 완료!');
                    
                    displayUploadResult(result);
                    showAnalysisCard();
                } else {
                    throw new Error(result.detail || '업로드 실패');
                }
            } catch (error) {
                addLog(`❌ 업로드 오류: ${error.message}`);
                document.getElementById('uploadResult').innerHTML = `
                    <div class="error-card">
                        <h4><i class="fas fa-exclamation-triangle"></i> 업로드 실패</h4>
                        <p>${error.message}</p>
                    </div>
                `;
            } finally {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = '<i class="fas fa-magic"></i> v3.0 하이브리드 분석 시작';
                setTimeout(() => {
                    document.getElementById('progressContainer').style.display = 'none';
                }, 2000);
            }
        }
        
        function displayUploadResult(data) {
            const hasQuantData = data.quantitative_columns && data.quantitative_columns.length > 0;
            const analysisType = hasQuantData ? '하이브리드 통합분석' : '텍스트 중심 분석';
            const analysisIcon = hasQuantData ? '🔬' : '📝';
            
            document.getElementById('uploadResult').innerHTML = `
                <div class="result-card">
                    <h4><i class="fas fa-check-circle"></i> AIRISS v3.0 데이터 검증 완료</h4>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${formatNumber(data.total_records)}</div>
                            <div class="stat-label">총 레코드</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.column_count}</div>
                            <div class="stat-label">전체 컬럼</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.opinion_columns.length}</div>
                            <div class="stat-label">텍스트 컬럼</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${hasQuantData ? data.quantitative_columns.length : 0}</div>
                            <div class="stat-label">정량 컬럼</div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; text-align: center;">
                        <div style="background: linear-gradient(135deg, #e8f5e8, #f1f8e9); padding: 15px; border-radius: 10px; border: 2px solid var(--ok-green);">
                            <strong style="color: var(--ok-green);">${analysisIcon} 권장 분석 모드: ${analysisType}</strong>
                            <br><small style="color: #2e7d32;">
                                ${hasQuantData ? 
                                    '텍스트 데이터와 정량 데이터가 모두 감지되어 하이브리드 분석이 가능합니다!' : 
                                    '주로 텍스트 데이터가 감지되었습니다. 기존 AIRISS 분석을 진행합니다.'
                                }
                            </small>
                        </div>
                    </div>
                </div>
            `;
        }
        
        function showAnalysisCard() {
            document.getElementById('analysisCard').style.display = 'block';
            document.getElementById('analysisCard').scrollIntoView({ behavior: 'smooth' });
        }
        
        async function startAnalysis() {
            if (!currentFileData) {
                alert('먼저 파일을 업로드해주세요.');
                return;
            }
            
            const sampleSize = document.getElementById('sampleSize').value;
            const analysisMode = document.getElementById('analysisMode').value;
            const enableAI = document.getElementById('enableAI').checked;
            const openaiKey = document.getElementById('openaiKey').value.trim();
            const openaiModel = document.getElementById('openaiModel').value;
            const maxTokens = parseInt(document.getElementById('maxTokens').value);
            const analyzeBtn = document.getElementById('analyzeBtn');
            
            // AI 피드백 설정 검증
            if (enableAI && !openaiKey) {
                alert('AI 피드백을 사용하려면 OpenAI API 키를 입력해주세요.');
                document.getElementById('openaiKey').focus();
                return;
            }
            
            if (enableAI && !validateApiKey()) {
                alert('올바른 OpenAI API 키를 입력해주세요.');
                document.getElementById('openaiKey').focus();
                return;
            }
            
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> AIRISS v3.0 분석 진행 중...';
            
            addLog('🚀 OK금융그룹 AIRISS v3.0 하이브리드 AI 분석 시작...');
            addLog(`📊 설정: ${sampleSize}개 샘플, ${analysisMode} 모드`);
            if (enableAI) {
                addLog(`🤖 AI 피드백: ${openaiModel} 모델, ${maxTokens} 토큰`);
            } else {
                addLog('🔬 하이브리드 키워드+정량 분석만 수행');
            }
            updateProgress(0, 'AIRISS v3.0 AI 분석 엔진 초기화...');
            
            try {
                const requestData = {
                    file_id: currentFileData.file_id,
                    sample_size: sampleSize === 'all' ? currentFileData.total_records : parseInt(sampleSize),
                    analysis_mode: analysisMode,
                    enable_ai_feedback: enableAI,
                    openai_api_key: enableAI ? openaiKey : null,
                    openai_model: openaiModel,
                    max_tokens: maxTokens
                };
                
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    analysisJobId = result.job_id;
                    addLog(`✅ AIRISS v3.0 분석 작업 시작: ${result.job_id}`);
                    
                    // 진행상황 폴링
                    pollAnalysisProgress(result.job_id);
                } else {
                    throw new Error(result.detail || '분석 시작 실패');
                }
            } catch (error) {
                addLog(`❌ 분석 오류: ${error.message}`);
                document.getElementById('analysisResult').innerHTML = `
                    <div class="error-card">
                        <h4><i class="fas fa-exclamation-triangle"></i> 분석 실패</h4>
                        <p>${error.message}</p>
                    </div>
                `;
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<i class="fas fa-rocket"></i> AIRISS v3.0 하이브리드 분석 실행';
            }
        }
        
        async function pollAnalysisProgress(jobId) {
            const pollInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/status/${jobId}`);
                    const status = await response.json();
                    
                    const progress = status.progress || 0;
                    updateProgress(progress, `AIRISS v3.0 분석: ${status.processed}/${status.total} (${progress.toFixed(1)}%)`);
                    
                    if (status.status === 'completed') {
                        clearInterval(pollInterval);
                        addLog('🎉 OK금융그룹 AIRISS v3.0 하이브리드 분석 완료!');
                        displayAnalysisResult(status);
                        showDownloadCard(jobId);
                        
                        const analyzeBtn = document.getElementById('analyzeBtn');
                        analyzeBtn.disabled = false;
                        analyzeBtn.innerHTML = '<i class="fas fa-rocket"></i> AIRISS v3.0 하이브리드 분석 실행';
                        
                    } else if (status.status === 'failed') {
                        clearInterval(pollInterval);
                        addLog(`❌ 분석 실패: ${status.error}`);
                        
                        const analyzeBtn = document.getElementById('analyzeBtn');
                        analyzeBtn.disabled = false;
                        analyzeBtn.innerHTML = '<i class="fas fa-rocket"></i> AIRISS v3.0 하이브리드 분석 실행';
                        
                    } else if (status.status === 'processing') {
                        addLog(`⏳ 하이브리드 분석 진행: ${status.processed}/${status.total} 레코드`);
                    }
                    
                } catch (error) {
                    addLog(`⚠️ 상태 확인 오류: ${error.message}`);
                }
            }, 2000);
        }
        
        function displayAnalysisResult(status) {
            const hybridInfo = status.hybrid_analysis_info || {};
            
            document.getElementById('analysisResult').innerHTML = `
                <div class="result-card">
                    <h4><i class="fas fa-chart-bar"></i> OK금융그룹 AIRISS v3.0 하이브리드 분석 결과</h4>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${formatNumber(status.processed)}</div>
                            <div class="stat-label">성공 분석</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${status.failed || 0}</div>
                            <div class="stat-label">실패 분석</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${((status.processed / status.total) * 100).toFixed(1)}%</div>
                            <div class="stat-label">성공률</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${status.average_score || 0}</div>
                            <div class="stat-label">평균 하이브리드 점수</div>
                        </div>
                        ${status.ai_success_count ? `
                        <div class="stat-card">
                            <div class="stat-number">${status.ai_success_count}</div>
                            <div class="stat-label">AI 피드백 성공</div>
                        </div>
                        ` : ''}
                        ${hybridInfo.quantitative_data_count ? `
                        <div class="stat-card">
                            <div class="stat-number">${hybridInfo.quantitative_data_count}</div>
                            <div class="stat-label">정량데이터 활용</div>
                        </div>
                        ` : ''}
                    </div>
                    <div style="margin-top: 20px; text-align: center;">
                        <div style="background: linear-gradient(135deg, #e8f5e8, #f1f8e9); padding: 15px; border-radius: 10px; border: 2px solid var(--ok-green);">
                            <strong style="color: var(--ok-green);">
                                🔬 하이브리드 분석 완료: 텍스트 분석 + 정량 데이터 통합
                            </strong>
                            <br><small style="color: #2e7d32;">
                                처리 시간: ${status.processing_time || '계산 중...'} | 신뢰도 대폭 향상!
                            </small>
                        </div>
                    </div>
                </div>
            `;
        }
        
        function showDownloadCard(jobId) {
            const downloadCard = document.getElementById('downloadCard');
            downloadCard.style.display = 'block';
            
            document.getElementById('downloadContent').innerHTML = `
                <button class="btn btn-success" onclick="downloadResult('${jobId}')" style="font-size: 1.2rem; padding: 18px 36px;">
                    <i class="fas fa-download"></i> AIRISS v3.0 하이브리드 분석 결과 다운로드
                </button>
                <ul class="features-list" style="margin-top: 20px; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto;">
                    <li>✨ AIRISS v3.0 하이브리드 스코어링</li>
                    <li>📊 8대 영역별 텍스트 + 정량 통합 점수</li>
                    <li>🎯 OK등급 체계 (OK★★★~OK D)</li>
                    <li>🔬 정량데이터 자동 변환 및 융합</li>
                    <li>🤖 AI 피드백 및 개선방향</li>
                    <li>📈 신뢰도 및 데이터 품질 분석</li>
                    <li>🏢 OK금융그룹 실무 적용 리포트</li>
                    <li>🆕 개인별 대시보드 조회 지원</li>
                </ul>
            `;
            
            downloadCard.scrollIntoView({ behavior: 'smooth' });
        }
        
        function downloadResult(jobId) {
            addLog('📥 OK금융그룹 AIRISS v3.0 하이브리드 분석 결과 다운로드 시작...');
            window.open(`/download/${jobId}`, '_blank');
        }
        
        // 초기화
        document.addEventListener('DOMContentLoaded', function() {
            setupFileUpload();
            addLog('🎯 OK금융그룹 AIRISS v3.0 완전통합 시스템 초기화 완료');
            addLog('📁 평가데이터 파일을 업로드하여 하이브리드 분석을 시작하세요');
            addLog('🔬 텍스트 의견 + 평가등급/점수 = 통합 스코어링');
            addLog('🤖 AI 피드백을 원하시면 설정에서 활성화해주세요');
            addLog('🏢 OK체 폰트와 브랜드 컬러가 적용되었습니다');
            addLog('⭐ AIRISS v3.0 모든 기능이 완전히 통합되었습니다');
            addLog('🆕 분석 완료 후 개인별 대시보드 조회가 가능합니다');
        });
    </script>
</body>
</html>
    """
    return html_content

# 🆕 NEW: 개인별 조회 대시보드 페이지
@app.get("/search", response_class=HTMLResponse)
async def get_search_page():
    """개인별 조회 화면 - 차트 크기 및 가독성 개선 버전"""
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIRISS v3.0 개인별 조회</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <style>
        :root {
            --ok-orange: #FF5722;
            --ok-white: #FFFFFF;
            --ok-dark-brown: #4A4A4A;
            --ok-yellow: #F89C26;
            --ok-green: #4CAF50;
            --ok-red: #f44336;
            --ok-grey: #9E9E9E;
        }
        
        * {
            box-sizing: border-box;
        }
        
        html {
            scroll-behavior: smooth;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, var(--ok-orange), var(--ok-yellow));
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .back-nav {
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        
        .back-nav a {
            color: white;
            text-decoration: none;
            font-weight: bold;
        }
        
        .search-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            position: relative;
        }
        
        .search-form {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr auto;
            gap: 15px;
            align-items: end;
        }
        
        .form-group label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: var(--ok-dark-brown);
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: var(--ok-orange);
        }
        
        .search-btn {
            background: var(--ok-orange);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .search-btn:hover:not(:disabled) {
            background: #E64A19;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .search-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            opacity: 0.6;
        }
        
        /* 통계 요약 카드 */
        .stats-summary-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            display: none;
        }
        
        .stats-summary-card h3 {
            color: var(--ok-dark-brown);
            margin-bottom: 20px;
            font-size: 1.3rem;
        }
        
        .stats-info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            transition: all 0.3s;
        }
        
        .stat-item:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--ok-orange);
        }
        
        /* 프로필 카드 */
        .profile-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            display: none;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .profile-header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .profile-avatar {
            width: 80px;
            height: 80px;
            background: var(--ok-orange);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 2rem;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(255,87,34,0.3);
            flex-shrink: 0;
        }
        
        .profile-info h2 {
            margin: 0 0 10px 0;
            color: var(--ok-dark-brown);
        }
        
        .profile-badges {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .grade {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .grade-star { background: var(--ok-green); color: white; }
        .grade-a { background: var(--ok-orange); color: white; }
        .grade-b { background: var(--ok-yellow); color: white; }
        .grade-c { background: var(--ok-grey); color: white; }
        .grade-d { background: #757575; color: white; }
        
        .percentile-badge {
            display: inline-block;
            background: linear-gradient(135deg, #4CAF50, #66BB6A);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* 점수 카드 그리드 */
        .scores-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .score-card {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .score-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-color: var(--ok-orange);
        }
        
        .score-card h3 {
            margin: 0 0 15px 0;
            color: var(--ok-dark-brown);
            font-size: 1rem;
        }
        
        .score-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--ok-orange);
            margin-bottom: 5px;
        }
        
        .score-comparison {
            font-size: 0.9rem;
            margin: 8px 0;
            font-weight: 600;
        }
        
        .score-comparison.positive {
            color: var(--ok-green);
        }
        
        .score-comparison.negative {
            color: var(--ok-red);
        }
        
        .score-description {
            color: #666;
            font-size: 0.9rem;
            margin-top: 10px;
        }
        
        /* 🔥 차트 컨테이너 - 크기 증가 */
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            height: 650px;  /* 500px → 650px */
            position: relative;
            overflow: hidden;
        }
        
        .chart-container h3 {
            text-align: center;
            margin-bottom: 20px;
            color: var(--ok-dark-brown);
            font-size: 1.3rem;  /* 제목 크기도 증가 */
        }
        
        #radarChart {
            max-height: 550px !important;  /* 430px → 550px */
            width: 100% !important;  /* 너비 100% 추가 */
        }
        
        /* 피드백 섹션 */
        .feedback-section {
            background: #e8f5e8;
            border: 2px solid var(--ok-green);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .feedback-title {
            color: #2e7d32;
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .feedback-content {
            line-height: 1.6;
            color: #333;
        }
        
        /* 기타 */
        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #666;
            display: none;
            background: white;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255,255,255,0.9);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            border-radius: 15px;
        }
        
        .loading-content {
            text-align: center;
        }
        
        .loading-spinner {
            font-size: 3rem;
            color: var(--ok-orange);
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error-message {
            background: #ffebee;
            border: 2px solid #f44336;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            color: #c62828;
            display: none;
            animation: shake 0.5s ease;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        @media (max-width: 768px) {
            .search-form {
                grid-template-columns: 1fr;
            }
            .scores-grid {
                grid-template-columns: 1fr;
            }
            .chart-container {
                height: 500px;  /* 모바일에서는 조금 작게 */
                padding: 20px;
            }
            #radarChart {
                max-height: 420px !important;
            }
            .profile-badges {
                flex-wrap: wrap;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="back-nav">
                <a href="/"><i class="fas fa-arrow-left"></i> 메인으로 돌아가기</a>
            </div>
            <h1><i class="fas fa-search"></i> AIRISS v3.0 개인별 조회</h1>
            <p>직원별 하이브리드 성과 분석 결과를 확인하세요</p>
        </div>
        
        <!-- 검색 카드 -->
        <div class="search-card">
            <h3><i class="fas fa-filter"></i> 직원 검색</h3>
            <div class="search-form">
                <div class="form-group">
                    <label for="jobSelect">분석 작업 선택</label>
                    <select id="jobSelect">
                        <option value="">작업을 선택하세요...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="uidInput">직원 UID</label>
                    <input type="text" id="uidInput" placeholder="직원 ID를 입력하세요">
                </div>
                <div class="form-group">
                    <label for="gradeFilter">등급 필터</label>
                    <select id="gradeFilter">
                        <option value="">전체 등급</option>
                        <option value="OK★★★">OK★★★ (최우수)</option>
                        <option value="OK★★">OK★★ (우수)</option>
                        <option value="OK★">OK★ (우수+)</option>
                        <option value="OK A">OK A (양호)</option>
                        <option value="OK B+">OK B+ (양호-)</option>
                        <option value="OK B">OK B (보통)</option>
                        <option value="OK C">OK C (개선필요)</option>
                        <option value="OK D">OK D (집중개선)</option>
                    </select>
                </div>
                <button class="search-btn" onclick="searchEmployee()" id="searchBtn">
                    <i class="fas fa-search"></i> 검색
                </button>
            </div>
            
            <div class="loading-overlay" id="loadingOverlay">
                <div class="loading-content">
                    <div class="loading-spinner">
                        <i class="fas fa-spinner"></i>
                    </div>
                    <p>검색 중입니다...</p>
                </div>
            </div>
        </div>
        
        <!-- 에러 메시지 -->
        <div class="error-message" id="errorMessage">
            <i class="fas fa-exclamation-triangle"></i> <span id="errorText"></span>
        </div>
        
        <!-- 전체 통계 요약 카드 -->
        <div class="stats-summary-card" id="statsSummaryCard">
            <h3><i class="fas fa-chart-bar"></i> 전체 분석 대상 통계</h3>
            <div class="stats-info-grid">
                <div class="stat-item">
                    <div class="stat-label">총 인원</div>
                    <div class="stat-value" id="totalCount">0명</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">평균 점수</div>
                    <div class="stat-value" id="avgScore">0점</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">최고 등급 비율</div>
                    <div class="stat-value" id="topGradeRatio">0%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">평균 신뢰도</div>
                    <div class="stat-value" id="avgConfidence">0%</div>
                </div>
            </div>
        </div>
        
        <!-- 프로필 카드 -->
        <div class="profile-card" id="profileCard">
            <div class="profile-header">
                <div class="profile-avatar" id="profileAvatar">U</div>
                <div class="profile-info">
                    <h2 id="profileUID">직원 ID</h2>
                    <div class="profile-badges">
                        <div class="grade" id="profileGrade">OK A</div>
                        <div class="percentile-badge" id="percentileRank">상위 0%</div>
                    </div>
                    <p id="profileDescription">양호 등급 - 정량+정성 통합분석</p>
                </div>
            </div>
            
            <div class="scores-grid">
                <div class="score-card">
                    <h3>🔬 하이브리드 종합점수</h3>
                    <div class="score-value" id="hybridScore">0</div>
                    <div class="score-comparison" id="hybridComparison">평균: 0</div>
                    <div class="score-description">텍스트 + 정량데이터 통합</div>
                </div>
                <div class="score-card">
                    <h3>📝 텍스트 분석점수</h3>
                    <div class="score-value" id="textScore">0</div>
                    <div class="score-comparison" id="textComparison">평균: 0</div>
                    <div class="score-description">AIRISS 8대 영역 키워드</div>
                </div>
                <div class="score-card">
                    <h3>📊 정량 분석점수</h3>
                    <div class="score-value" id="quantScore">0</div>
                    <div class="score-comparison" id="quantComparison">평균: 0</div>
                    <div class="score-description">등급/점수 객관적 평가</div>
                </div>
                <div class="score-card">
                    <h3>🎯 분석 신뢰도</h3>
                    <div class="score-value" id="confidenceScore">0</div>
                    <div class="score-comparison" id="confidenceComparison">평균: 0</div>
                    <div class="score-description">데이터 품질 기반</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>AIRISS 8대 영역 분석 (개인 vs 평균)</h3>
                <canvas id="radarChart"></canvas>
            </div>
            
            <div class="feedback-section" id="aiFeedback" style="display: none;">
                <div class="feedback-title">
                    <i class="fas fa-robot"></i> AI 종합 피드백
                </div>
                <div class="feedback-content" id="aiFeedbackContent"></div>
            </div>
            
            <div class="feedback-section">
                <div class="feedback-title">
                    <i class="fas fa-thumbs-up"></i> 핵심 장점
                </div>
                <div class="feedback-content" id="strengthsContent">분석된 장점이 여기에 표시됩니다.</div>
            </div>
            
            <div class="feedback-section">
                <div class="feedback-title">
                    <i class="fas fa-target"></i> 개선 방향
                </div>
                <div class="feedback-content" id="improvementContent">개선 방향이 여기에 표시됩니다.</div>
            </div>
        </div>
        
        <!-- 검색 결과 없음 -->
        <div class="no-results" id="noResults">
            <i class="fas fa-user-slash" style="font-size: 3rem; color: #ccc; margin-bottom: 15px;"></i>
            <h3>검색 결과가 없습니다</h3>
            <p>입력하신 조건에 맞는 직원을 찾을 수 없습니다.</p>
        </div>
    </div>

    <script>
        // 전역 변수
        let radarChart = null;
        let currentStats = null;
        
        // 페이지 로드시 초기화
        document.addEventListener('DOMContentLoaded', function() {
            console.log('[AIRISS v3.0] 페이지 로드 완료');
            
            // Chart.js 확인
            if (typeof Chart !== 'undefined') {
                console.log('[AIRISS v3.0] Chart.js 로딩 성공');
            } else {
                console.warn('[AIRISS v3.0] Chart.js 로딩 실패');
            }
            
            // 작업 목록 로드
            loadJobList();
            
            // 엔터 키 이벤트
            document.getElementById('uidInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchEmployee();
                }
            });
        });
        
        // 작업 목록 로드
        async function loadJobList() {
            try {
                const response = await fetch('/api/jobs');
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const jobs = await response.json();
                console.log('[AIRISS v3.0] 작업 목록:', jobs.length + '개');
                
                const jobSelect = document.getElementById('jobSelect');
                jobSelect.innerHTML = '<option value="">작업을 선택하세요...</option>';
                
                if (jobs && jobs.length > 0) {
                    jobs.forEach(job => {
                        const option = document.createElement('option');
                        option.value = job.job_id;
                        option.textContent = `${job.filename} (${job.processed}명, ${job.end_time || '시간 정보 없음'})`;
                        jobSelect.appendChild(option);
                    });
                } else {
                    jobSelect.innerHTML = '<option value="">완료된 작업이 없습니다</option>';
                    showError('분석 완료된 작업이 없습니다. 먼저 데이터 분석을 진행해주세요.');
                }
            } catch (error) {
                console.error('[AIRISS v3.0] 작업 목록 로드 오류:', error);
                showError('작업 목록을 불러올 수 없습니다.');
            }
        }
        
        // 직원 검색
        async function searchEmployee() {
            const jobId = document.getElementById('jobSelect').value;
            const uid = document.getElementById('uidInput').value.trim();
            const gradeFilter = document.getElementById('gradeFilter').value;
            
            // 검증
            if (!jobId) {
                showError('분석 작업을 선택해주세요.');
                return;
            }
            
            if (!uid && !gradeFilter) {
                showError('직원 UID를 입력하거나 등급을 선택해주세요.');
                return;
            }
            
            // UI 상태 변경
            showLoading(true);
            hideError();
            hideAllResults();
            
            try {
                // API URL 구성
                let url = `/api/employee/${jobId}`;
                const params = new URLSearchParams();
                if (uid) params.append('uid', uid);
                if (gradeFilter) params.append('grade', gradeFilter);
                
                if (params.toString()) {
                    url += '?' + params.toString();
                }
                
                // API 호출
                const response = await fetch(url);
                const result = await response.json();
                
                console.log('[AIRISS v3.0] 검색 결과:', result);
                
                if (response.ok && result.employee) {
                    // 통계 데이터 저장
                    currentStats = result.statistics;
                    
                    // 통계 카드 표시
                    displayStatistics(currentStats);
                    
                    // 프로필 표시
                    displayEmployeeProfile(result.employee, currentStats);
                } else {
                    // 결과 없음
                    showNoResults();
                }
                
            } catch (error) {
                console.error('[AIRISS v3.0] 검색 오류:', error);
                showError('검색 중 오류가 발생했습니다.');
            } finally {
                showLoading(false);
            }
        }
        
        // 통계 정보 표시
        function displayStatistics(stats) {
            if (!stats) return;
            
            document.getElementById('statsSummaryCard').style.display = 'block';
            document.getElementById('totalCount').textContent = stats.total_count + '명';
            document.getElementById('avgScore').textContent = stats.average_scores.hybrid_avg.toFixed(1) + '점';
            document.getElementById('topGradeRatio').textContent = stats.top_grade_ratio + '%';
            document.getElementById('avgConfidence').textContent = stats.average_scores.confidence_avg.toFixed(1) + '%';
        }
        
        // 직원 프로필 표시
        function displayEmployeeProfile(employee, stats) {
            try {
                // 모든 결과 숨기기
                hideAllResults();
                
                // 프로필 데이터 설정
                const uid = employee.UID || employee.uid || 'Unknown';
                document.getElementById('profileAvatar').textContent = uid.charAt(0).toUpperCase();
                document.getElementById('profileUID').textContent = uid;
                
                // 등급 설정
                const grade = employee.OK등급 || employee['OK등급'] || 'OK C';
                const gradeElement = document.getElementById('profileGrade');
                gradeElement.textContent = grade;
                gradeElement.className = 'grade ' + getGradeClass(grade);
                
                // 상위 퍼센트 표시
                if (employee.percentile_rank) {
                    const percentile = employee.percentile_rank;
                    document.getElementById('percentileRank').textContent = `상위 ${(100 - percentile).toFixed(1)}%`;
                }
                
                const description = employee.등급설명 || employee['등급설명'] || '분석 결과';
                document.getElementById('profileDescription').textContent = description;
                
                // 점수 및 평균 비교 설정
                const scores = {
                    hybrid: parseFloat(employee.AIRISS_v2_종합점수 || employee['AIRISS_v2_종합점수'] || 0),
                    text: parseFloat(employee.텍스트_종합점수 || employee['텍스트_종합점수'] || 0),
                    quant: parseFloat(employee.정량_종합점수 || employee['정량_종합점수'] || 0),
                    confidence: parseFloat(employee.분석신뢰도 || employee['분석신뢰도'] || 0)
                };
                
                // 점수 표시
                document.getElementById('hybridScore').textContent = scores.hybrid.toFixed(1);
                document.getElementById('textScore').textContent = scores.text.toFixed(1);
                document.getElementById('quantScore').textContent = scores.quant.toFixed(1);
                document.getElementById('confidenceScore').textContent = scores.confidence.toFixed(1) + '%';
                
                // 평균 비교 표시
                if (stats && stats.average_scores) {
                    displayScoreComparisons(scores, stats.average_scores);
                }
                
                // 차트 그리기 (평균 포함)
                if (stats && stats.dimension_averages) {
                    drawRadarChartWithAverage(employee, stats.dimension_averages);
                } else {
                    drawRadarChart(employee);
                }
                
                // AI 피드백
                const aiFeedbackText = employee.AI_종합피드백 || employee['AI_종합피드백'] || '';
                if (aiFeedbackText && aiFeedbackText !== 'AI 피드백이 비활성화되어 있습니다.') {
                    document.getElementById('aiFeedback').style.display = 'block';
                    document.getElementById('aiFeedbackContent').textContent = aiFeedbackText;
                } else {
                    document.getElementById('aiFeedback').style.display = 'none';
                }
                
                // 장점과 개선점
                const strengths = employee.AI_장점 || employee['AI_장점'] || '키워드 분석을 통해 도출된 긍정적 특성들이 있습니다.';
                const improvements = employee.AI_개선점 || employee['AI_개선점'] || '지속적인 성장을 위한 개선 기회가 있습니다.';
                
                document.getElementById('strengthsContent').textContent = strengths;
                document.getElementById('improvementContent').textContent = improvements;
                
                // 프로필 카드 표시
                document.getElementById('profileCard').style.display = 'block';
                
                console.log('[AIRISS v3.0] 프로필 표시 완료');
                
            } catch (error) {
                console.error('[AIRISS v3.0] 프로필 표시 오류:', error);
                showError('직원 정보를 표시하는 중 오류가 발생했습니다.');
            }
        }
        
        // 점수 비교 표시
        function displayScoreComparisons(scores, avgScores) {
            // 하이브리드 점수 비교
            const hybridDiff = scores.hybrid - avgScores.hybrid_avg;
            const hybridComp = document.getElementById('hybridComparison');
            hybridComp.textContent = `평균: ${avgScores.hybrid_avg.toFixed(1)} (${hybridDiff >= 0 ? '+' : ''}${hybridDiff.toFixed(1)})`;
            hybridComp.className = 'score-comparison ' + (hybridDiff >= 0 ? 'positive' : 'negative');
            
            // 텍스트 점수 비교
            const textDiff = scores.text - avgScores.text_avg;
            const textComp = document.getElementById('textComparison');
            textComp.textContent = `평균: ${avgScores.text_avg.toFixed(1)} (${textDiff >= 0 ? '+' : ''}${textDiff.toFixed(1)})`;
            textComp.className = 'score-comparison ' + (textDiff >= 0 ? 'positive' : 'negative');
            
            // 정량 점수 비교
            const quantDiff = scores.quant - avgScores.quant_avg;
            const quantComp = document.getElementById('quantComparison');
            quantComp.textContent = `평균: ${avgScores.quant_avg.toFixed(1)} (${quantDiff >= 0 ? '+' : ''}${quantDiff.toFixed(1)})`;
            quantComp.className = 'score-comparison ' + (quantDiff >= 0 ? 'positive' : 'negative');
            
            // 신뢰도 비교
            const confDiff = scores.confidence - avgScores.confidence_avg;
            const confComp = document.getElementById('confidenceComparison');
            confComp.textContent = `평균: ${avgScores.confidence_avg.toFixed(1)}% (${confDiff >= 0 ? '+' : ''}${confDiff.toFixed(1)}%)`;
            confComp.className = 'score-comparison ' + (confDiff >= 0 ? 'positive' : 'negative');
        }
        
        // 🔥 평균선이 포함된 레이더 차트 - 크기 및 가독성 개선
        function drawRadarChartWithAverage(employee, dimensionAvgs) {
            if (typeof Chart === 'undefined') {
                console.warn('[AIRISS v3.0] Chart.js 사용 불가');
                return;
            }
            
            try {
                const ctx = document.getElementById('radarChart').getContext('2d');
                
                // 기존 차트 제거
                if (radarChart) {
                    radarChart.destroy();
                    radarChart = null;
                }
                
                // 8대 영역 데이터
                const dimensions = ['업무성과', 'KPI달성', '태도마인드', '커뮤니케이션',
                                  '리더십협업', '전문성학습', '창의혁신', '조직적응'];
                
                const individualScores = dimensions.map(dim => {
                    const key = dim + '_텍스트점수';
                    const value = employee[key] || 50;
                    return parseFloat(value);
                });
                
                const averageScores = dimensions.map(dim => dimensionAvgs[dim] || 50);
                
                // 새 차트 생성
                radarChart = new Chart(ctx, {
                    type: 'radar',
                    data: {
                        labels: dimensions,
                        datasets: [
                            {
                                label: '개인 점수',
                                data: individualScores,
                                backgroundColor: 'rgba(255, 87, 34, 0.2)',
                                borderColor: '#FF5722',
                                borderWidth: 4,  // 3 → 4
                                pointBackgroundColor: '#FF5722',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 3,  // 2 → 3
                                pointRadius: 8,  // 6 → 8
                                pointHoverRadius: 10  // 8 → 10
                            },
                            {
                                label: '전체 평균',
                                data: averageScores,
                                backgroundColor: 'rgba(158, 158, 158, 0.1)',
                                borderColor: '#9E9E9E',
                                borderWidth: 3,  // 2 → 3
                                borderDash: [5, 5],
                                pointBackgroundColor: '#9E9E9E',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2,
                                pointRadius: 6,  // 4 → 6
                                pointHoverRadius: 8  // 6 → 8
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        layout: {
                            padding: {
                                top: 20,
                                bottom: 60,  // 범례 공간 확보
                                left: 20,
                                right: 20
                            }
                        },
                        scales: {
                            r: {
                                beginAtZero: true,
                                max: 100,
                                ticks: {
                                    stepSize: 20,
                                    font: {
                                        size: 16  // 12 → 16
                                    }
                                },
                                pointLabels: {
                                    font: {
                                        size: 16  // 레이블 폰트 크기 증가
                                    }
                                },
                                grid: {
                                    color: 'rgba(0, 0, 0, 0.1)'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'bottom',
                                labels: {
                                    font: {
                                        size: 16  // 14 → 16
                                    },
                                    padding: 25,  // 20 → 25
                                    boxWidth: 20,
                                    boxHeight: 20
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.dataset.label;
                                        const value = context.parsed.r.toFixed(1);
                                        return `${label}: ${value}점`;
                                    }
                                },
                                bodyFont: {
                                    size: 14
                                }
                            }
                        },
                        animation: {
                            duration: 1000
                        }
                    }
                });
                
                console.log('[AIRISS v3.0] 비교 차트 생성 완료');
                
            } catch (error) {
                console.error('[AIRISS v3.0] 차트 생성 오류:', error);
                // 실패시 기본 차트 그리기
                drawRadarChart(employee);
            }
        }
        
        // 기본 레이더 차트 (평균 없이) - 크기 개선
        function drawRadarChart(employee) {
            if (typeof Chart === 'undefined') {
                console.warn('[AIRISS v3.0] Chart.js 사용 불가');
                return;
            }
            
            try {
                const ctx = document.getElementById('radarChart').getContext('2d');
                
                // 기존 차트 제거
                if (radarChart) {
                    radarChart.destroy();
                    radarChart = null;
                }
                
                // 8대 영역 데이터
                const dimensions = [
                    '업무성과', 'KPI달성', '태도마인드', '커뮤니케이션',
                    '리더십협업', '전문성학습', '창의혁신', '조직적응'
                ];
                
                const scores = dimensions.map(dim => {
                    const key = dim + '_텍스트점수';
                    const value = employee[key] || 50;
                    return parseFloat(value);
                });
                
                // 새 차트 생성
                radarChart = new Chart(ctx, {
                    type: 'radar',
                    data: {
                        labels: dimensions,
                        datasets: [{
                            label: 'AIRISS 8대 영역 점수',
                            data: scores,
                            backgroundColor: 'rgba(255, 87, 34, 0.2)',
                            borderColor: '#FF5722',
                            borderWidth: 4,
                            pointBackgroundColor: '#FF5722',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 3,
                            pointRadius: 8,
                            pointHoverRadius: 10
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        layout: {
                            padding: {
                                top: 20,
                                bottom: 60,
                                left: 20,
                                right: 20
                            }
                        },
                        scales: {
                            r: {
                                beginAtZero: true,
                                max: 100,
                                ticks: {
                                    stepSize: 20,
                                    font: {
                                        size: 16
                                    }
                                },
                                pointLabels: {
                                    font: {
                                        size: 16
                                    }
                                },
                                grid: {
                                    color: 'rgba(0, 0, 0, 0.1)'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'bottom',
                                labels: {
                                    font: {
                                        size: 16
                                    },
                                    padding: 25,
                                    boxWidth: 20,
                                    boxHeight: 20
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return context.dataset.label + ': ' + context.parsed.r.toFixed(1) + '점';
                                    }
                                },
                                bodyFont: {
                                    size: 14
                                }
                            }
                        },
                        animation: {
                            duration: 1000
                        }
                    }
                });
                
                console.log('[AIRISS v3.0] 차트 생성 완료');
                
            } catch (error) {
                console.error('[AIRISS v3.0] 차트 생성 오류:', error);
            }
        }
        
        // 등급에 따른 CSS 클래스
        function getGradeClass(grade) {
            if (grade.includes('★')) return 'grade-star';
            if (grade.includes('A')) return 'grade-a';
            if (grade.includes('B+')) return 'grade-a';
            if (grade.includes('B')) return 'grade-b';
            if (grade.includes('C')) return 'grade-c';
            return 'grade-d';
        }
        
        // UI 헬퍼 함수들
        function showLoading(show) {
            document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
            document.getElementById('searchBtn').disabled = show;
        }
        
        function showError(message) {
            document.getElementById('errorMessage').style.display = 'block';
            document.getElementById('errorText').textContent = message;
        }
        
        function hideError() {
            document.getElementById('errorMessage').style.display = 'none';
        }
        
        function showNoResults() {
            hideAllResults();
            document.getElementById('noResults').style.display = 'block';
        }
        
        function hideAllResults() {
            document.getElementById('profileCard').style.display = 'none';
            document.getElementById('noResults').style.display = 'none';
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('statsSummaryCard').style.display = 'none';
        }
    </script>
</body>
</html>""", status_code=200) 
# 🆕 NEW: 검색 API 엔드포인트들 추가
@app.get("/api/jobs")
async def get_completed_jobs():
    """완료된 분석 작업 목록 조회"""
    try:
        completed_jobs = []
        for job_id, job_data in store.jobs.items():
            if job_data.get("status") == "completed" and job_data.get("results"):
                file_data = store.get_file(job_data["file_id"])
                completed_jobs.append({
                    "job_id": job_id,
                    "filename": file_data["filename"] if file_data else "Unknown",
                    "processed": job_data["processed"],
                    "end_time": job_data["end_time"].strftime("%Y-%m-%d %H:%M") if job_data.get("end_time") else "",
                    "analysis_mode": job_data.get("analysis_mode", "hybrid")
                })
        
        # 최신순 정렬
        completed_jobs.sort(key=lambda x: x["end_time"], reverse=True)
        return completed_jobs
        
    except Exception as e:
        logger.error(f"작업 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="작업 목록 조회 실패")

@app.get("/api/employee/{job_id}")
async def search_employee(job_id: str, uid: str = None, grade: str = None):
    """개별 직원 데이터 검색 - 전체 평균 및 통계 포함"""
    try:
        job_data = store.get_job(job_id)
        if not job_data or job_data.get("status") != "completed":
            raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
        
        results = job_data.get("results", [])
        if not results:
            raise HTTPException(status_code=404, detail="분석 결과가 없습니다")
        
        # 전체 통계 데이터 계산
        df_results = pd.DataFrame(results)
        
        # 평균 점수 계산
        avg_scores = {
            "hybrid_avg": round(df_results["AIRISS_v2_종합점수"].mean(), 1),
            "text_avg": round(df_results["텍스트_종합점수"].mean(), 1),
            "quant_avg": round(df_results["정량_종합점수"].mean(), 1),
            "confidence_avg": round(df_results["분석신뢰도"].mean(), 1)
        }
        
        # 8대 영역별 평균
        dimensions = ['업무성과', 'KPI달성', '태도마인드', '커뮤니케이션',
                     '리더십협업', '전문성학습', '창의혁신', '조직적응']
        
        dimension_avgs = {}
        for dim in dimensions:
            col_name = f"{dim}_텍스트점수"
            if col_name in df_results.columns:
                dimension_avgs[dim] = round(df_results[col_name].mean(), 1)
        
        # 등급 분포
        grade_distribution = df_results["OK등급"].value_counts().to_dict()
        total_count = len(results)
        
        # 최고 등급 비율 계산
        top_grades = ["OK★★★", "OK★★", "OK★"]
        top_grade_count = sum(grade_distribution.get(g, 0) for g in top_grades)
        top_grade_ratio = round((top_grade_count / total_count) * 100, 1) if total_count > 0 else 0
        
        # UID로 검색
        employee_data = None
        if uid:
            for employee in results:
                if str(employee.get("UID", "")).lower() == uid.lower():
                    employee_data = employee
                    
                    # 개인의 상대적 위치 계산
                    hybrid_score = employee.get("AIRISS_v2_종합점수", 0)
                    higher_count = (df_results["AIRISS_v2_종합점수"] > hybrid_score).sum()
                    percentile_rank = round(((total_count - higher_count) / total_count) * 100, 1)
                    employee_data["percentile_rank"] = percentile_rank
                    
                    # 각 점수별 평균 대비 차이 계산
                    employee_data["score_differences"] = {
                        "hybrid_diff": round(hybrid_score - avg_scores["hybrid_avg"], 1),
                        "text_diff": round(employee.get("텍스트_종합점수", 0) - avg_scores["text_avg"], 1),
                        "quant_diff": round(employee.get("정량_종합점수", 0) - avg_scores["quant_avg"], 1),
                        "confidence_diff": round(employee.get("분석신뢰도", 0) - avg_scores["confidence_avg"], 1)
                    }
                    
                    break
        
        # 등급으로 필터링
        if grade and not employee_data:
            for employee in results:
                if employee.get("OK등급") == grade:
                    employee_data = employee
                    # 상대적 위치 계산
                    hybrid_score = employee.get("AIRISS_v2_종합점수", 0)
                    higher_count = (df_results["AIRISS_v2_종합점수"] > hybrid_score).sum()
                    percentile_rank = round(((total_count - higher_count) / total_count) * 100, 1)
                    employee_data["percentile_rank"] = percentile_rank
                    break
        
        if not employee_data and results:
            employee_data = results[0]
        
        return {
            "employee": employee_data,
            "statistics": {
                "total_count": total_count,
                "average_scores": avg_scores,
                "dimension_averages": dimension_avgs,
                "grade_distribution": grade_distribution,
                "top_grade_ratio": top_grade_ratio
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"직원 검색 오류: {e}")
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다")

@app.get("/api/employees/{job_id}")
async def get_employees_list(job_id: str, limit: int = 50):
    """직원 목록 조회 (자동완성용)"""
    try:
        job_data = store.get_job(job_id)
        if not job_data or job_data.get("status") != "completed":
            raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
        
        results = job_data.get("results", [])
        employee_list = []
        
        for employee in results[:limit]:
            employee_list.append({
                "uid": employee.get("UID"),
                "grade": employee.get("OK등급"),
                "score": employee.get("AIRISS_v2_종합점수", 0)
            })
        
        return {"employees": employee_list}
        
    except Exception as e:
        logger.error(f"직원 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="목록 조회 실패")
# 🆕 업로드 엔드포인트 수정 (정량데이터 감지 추가) - v2.0 코드 그대로
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """파일 업로드 및 기초 분석 - v3.0 정량데이터 감지 추가"""
    try:
        logger.info(f"AIRISS v3.0 파일 업로드 시작: {file.filename}")
        
        # 파일 내용 읽기 (기존 코드 그대로)
        contents = await file.read()
        
        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
            logger.info("Excel 파일 처리 완료")
        elif file.filename.endswith('.csv'):
            encodings = ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(io.StringIO(contents.decode(encoding)))
                    logger.info(f"CSV 파일 처리 완료 (인코딩: {encoding})")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.warning(f"인코딩 {encoding} 실패: {e}")
                    continue
            
            if df is None:
                raise HTTPException(status_code=400, detail="CSV 파일 인코딩을 인식할 수 없습니다")
        else:
            raise HTTPException(status_code=400, detail="지원되지 않는 파일 형식입니다")
        
        # 파일 ID 생성 및 저장
        file_id = str(uuid.uuid4())
        os.makedirs('temp', exist_ok=True)
        
        # 기존 컬럼 분석
        all_columns = list(df.columns)
        uid_columns = [col for col in all_columns if any(keyword in col.lower() 
                      for keyword in ['uid', 'id', '아이디', '사번', '직원', 'user', 'emp'])]
        opinion_columns = [col for col in all_columns if any(keyword in col.lower() 
                          for keyword in ['의견', 'opinion', '평가', 'feedback', '내용', '코멘트', '피드백', 'comment', 'review'])]
        
        # 🆕 NEW: 정량데이터 컬럼 감지
        quantitative_columns = []
        for col in all_columns:
            col_lower = col.lower()
            # 점수, 등급, 달성률 등 정량 데이터 패턴 감지
            if any(keyword in col_lower for keyword in [
                '점수', 'score', '평점', 'rating', '등급', 'grade', 'level',
                '달성률', '비율', 'rate', '%', 'percent', '횟수', '건수', 'count'
            ]):
                # 실제 데이터가 정량적인지 확인
                sample_data = df[col].dropna().head(10)
                if len(sample_data) > 0:
                    quantitative_score = 0
                    for value in sample_data:
                        str_val = str(value).strip()
                        # 숫자, 등급, 퍼센트 패턴 확인
                        if (str_val.replace('.', '').replace('%', '').replace('점', '').isdigit() or
                            any(grade in str_val.upper() for grade in ['A', 'B', 'C', 'D', 'S', '우수', '양호', '보통']) or
                            any(grade in str_val for grade in ['1', '2', '3', '4', '5'])):
                            quantitative_score += 1
                    
                    # 샘플의 70% 이상이 정량적이면 정량 컬럼으로 분류
                    if quantitative_score / len(sample_data) >= 0.7:
                        quantitative_columns.append(col)
        
        # 데이터 품질 체크
        total_records = len(df)
        non_empty_records = len(df.dropna(subset=opinion_columns if opinion_columns else []))
        
        # 🆕 정량데이터 품질 체크
        quantitative_data_quality = 0
        if quantitative_columns:
            quantitative_non_empty = len(df.dropna(subset=quantitative_columns))
            quantitative_data_quality = round((quantitative_non_empty / total_records) * 100, 1) if total_records > 0 else 0
        
        # 저장 (기존 + 정량데이터 정보 추가)
        store.add_file(file_id, {
            'dataframe': df,
            'filename': file.filename,
            'upload_time': datetime.now(),
            'total_records': total_records,
            'columns': all_columns,
            'uid_columns': uid_columns,
            'opinion_columns': opinion_columns,
            'quantitative_columns': quantitative_columns  # 🆕 추가
        })
        
        logger.info(f"AIRISS v3.0 파일 저장 완료: {file_id}")
        logger.info(f"정량 컬럼 감지: {len(quantitative_columns)}개")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "total_records": total_records,
            "column_count": len(all_columns),
            "uid_columns": uid_columns,
            "opinion_columns": opinion_columns,
            "quantitative_columns": quantitative_columns,  # 🆕 추가
            "airiss_ready": len(uid_columns) > 0 and len(opinion_columns) > 0,
            "hybrid_ready": len(quantitative_columns) > 0,  # 🆕 추가
            "data_quality": {
                "non_empty_records": non_empty_records,
                "completeness": round((non_empty_records / total_records) * 100, 1) if total_records > 0 else 0,
                "quantitative_completeness": quantitative_data_quality  # 🆕 추가
            }
        }
        
    except Exception as e:
        logger.error(f"AIRISS v3.0 파일 업로드 오류: {e}")
        raise HTTPException(status_code=400, detail=f"파일 처리 오류: {str(e)}")

# 🆕 분석 엔드포인트 수정 (하이브리드 분석 지원) - v2.0 코드 그대로
@app.post("/analyze")
async def start_analysis(request: AnalysisRequest):
    """분석 작업 시작 - v3.0 하이브리드 분석 지원"""
    try:
        # 파일 데이터 확인
        file_data = store.get_file(request.file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        # 작업 ID 생성
        job_id = str(uuid.uuid4())
        
        # 작업 정보 초기화 (v3.0 정보 추가)
        store.add_job(job_id, {
            "status": "processing",
            "file_id": request.file_id,
            "sample_size": request.sample_size,
            "analysis_mode": request.analysis_mode,
            "enable_ai_feedback": request.enable_ai_feedback,
            "openai_api_key": request.openai_api_key,
            "openai_model": request.openai_model,
            "max_tokens": request.max_tokens,
            "start_time": datetime.now(),
            "total": request.sample_size,
            "processed": 0,
            "failed": 0,
            "progress": 0.0,
            "results": [],
            "version": "3.0",  # 🆕 추가
            "hybrid_analysis_info": {}  # 🆕 추가
        })
        
        # 백그라운드에서 분석 실행
        asyncio.create_task(process_analysis_v3(job_id))
        
        logger.info(f"AIRISS v3.0 분석 작업 시작: {job_id}")
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "OK금융그룹 AIRISS v3.0 하이브리드 분석이 시작되었습니다",
            "ai_feedback_enabled": request.enable_ai_feedback,
            "analysis_mode": request.analysis_mode
        }
        
    except Exception as e:
        logger.error(f"AIRISS v3.0 분석 시작 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 🆕 NEW: v3.0 하이브리드 분석 처리 함수 (v2.0과 동일하지만 버전명 업데이트)
async def process_analysis_v3(job_id: str):
    """AIRISS v3.0 하이브리드 백그라운드 분석 처리"""
    try:
        job_data = store.get_job(job_id)
        file_data = store.get_file(job_data["file_id"])
        
        df = file_data["dataframe"]
        sample_size = job_data["sample_size"]
        analysis_mode = job_data.get("analysis_mode", "hybrid")
        enable_ai = job_data.get("enable_ai_feedback", False)
        api_key = job_data.get("openai_api_key", None)
        model = job_data.get("openai_model", "gpt-3.5-turbo")
        max_tokens = job_data.get("max_tokens", 1200)
        
        logger.info(f"AIRISS v3.0 분석 처리 시작: 샘플={sample_size}, 모드={analysis_mode}, AI={enable_ai}")
        
        # 샘플 데이터 선택
        if sample_size == "all" or sample_size >= len(df):
            sample_df = df.copy()
        else:
            sample_df = df.head(sample_size).copy()
        
        # 컬럼 확인
        uid_cols = file_data["uid_columns"]
        opinion_cols = file_data["opinion_columns"]
        quantitative_cols = file_data.get("quantitative_columns", [])
        
        if not uid_cols or not opinion_cols:
            store.update_job(job_id, {
                "status": "failed",
                "error": "필수 컬럼(UID, 의견)을 찾을 수 없습니다"
            })
            return
        
        results = []
        total_rows = len(sample_df)
        ai_success_count = 0
        ai_fail_count = 0
        quantitative_data_count = 0
        
        for idx, row in sample_df.iterrows():
            try:
                # UID와 의견 추출
                uid = str(row[uid_cols[0]]) if uid_cols else f"user_{idx}"
                opinion = str(row[opinion_cols[0]]) if opinion_cols else ""
                
                # 빈 의견 처리
                if not opinion or opinion.lower() in ['nan', 'null', '', 'none']:
                    # 정량데이터만 있는 경우도 처리 가능하도록 수정
                    if analysis_mode != "quantitative" and not quantitative_cols:
                        store.update_job(job_id, {"failed": job_data["failed"] + 1})
                        continue
                    opinion = ""  # 빈 의견으로 설정
                
                # 🆕 분석 모드에 따른 처리
                if analysis_mode == "text":
                    # 텍스트 분석만
                    analysis_result = hybrid_analyzer.text_analyzer.calculate_overall_score({
                        dim: hybrid_analyzer.text_analyzer.analyze_text(opinion, dim)["score"] 
                        for dim in AIRISS_FRAMEWORK.keys()
                    })
                    comprehensive_result = {
                        "text_analysis": analysis_result,
                        "quantitative_analysis": {"quantitative_score": 50, "confidence": 0},
                        "hybrid_analysis": analysis_result,
                        "analysis_metadata": {"analysis_version": "AIRISS v3.0 - Text Only"}
                    }
                
                elif analysis_mode == "quantitative":
                    # 정량 분석만
                    quant_data = hybrid_analyzer.quantitative_analyzer.extract_quantitative_data(row)
                    quant_result = hybrid_analyzer.quantitative_analyzer.calculate_quantitative_score(quant_data)
                    grade_info = hybrid_analyzer.calculate_hybrid_grade(quant_result["quantitative_score"])
                    
                    comprehensive_result = {
                        "text_analysis": {"overall_score": 50, "grade": "OK C"},
                        "quantitative_analysis": quant_result,
                        "hybrid_analysis": {
                            "overall_score": quant_result["quantitative_score"],
                            "grade": grade_info["grade"],
                            "grade_description": grade_info["grade_description"],
                            "confidence": quant_result["confidence"]
                        },
                        "analysis_metadata": {"analysis_version": "AIRISS v3.0 - Quantitative Only"}
                    }
                
                else:  # hybrid (기본값)
                    # 하이브리드 통합 분석
                    comprehensive_result = hybrid_analyzer.comprehensive_analysis(uid, opinion, row)
                
                # 정량데이터 사용 여부 체크
                if comprehensive_result["quantitative_analysis"]["data_count"] > 0:
                    quantitative_data_count += 1
                
                # 결과 레코드 생성 (v3.0 형식)
                result_record = {
                    "UID": uid,
                    "원본의견": opinion[:500] + "..." if len(opinion) > 500 else opinion,
                    
                    # 🆕 하이브리드 통합 점수 (메인)
                    "AIRISS_v2_종합점수": comprehensive_result["hybrid_analysis"]["overall_score"],
                    "OK등급": comprehensive_result["hybrid_analysis"]["grade"],
                    "등급설명": comprehensive_result["hybrid_analysis"]["grade_description"],
                    "백분위": comprehensive_result["hybrid_analysis"]["percentile"],
                    "분석신뢰도": comprehensive_result["hybrid_analysis"]["confidence"],
                    
                    # 텍스트 분석 결과 (기존 유지)
                    "텍스트_종합점수": comprehensive_result["text_analysis"]["overall_score"],
                    "텍스트_등급": comprehensive_result["text_analysis"]["grade"],
                    
                    # 정량 분석 결과 (신규)
                    "정량_종합점수": comprehensive_result["quantitative_analysis"]["quantitative_score"],
                    "정량_신뢰도": comprehensive_result["quantitative_analysis"]["confidence"],
                    "정량_데이터품질": comprehensive_result["quantitative_analysis"]["data_quality"],
                    "정량_데이터개수": comprehensive_result["quantitative_analysis"]["data_count"],
                    
                    # 분석 구성 정보
                    "분석모드": analysis_mode,
                    "텍스트_가중치": comprehensive_result["hybrid_analysis"].get("analysis_composition", {}).get("text_weight", "N/A"),
                    "정량_가중치": comprehensive_result["hybrid_analysis"].get("analysis_composition", {}).get("quantitative_weight", "N/A")
                }
                
                # 8대 영역별 텍스트 점수 추가 (기존 유지)
                if "dimension_scores" in comprehensive_result["text_analysis"]:
                    for dimension, score in comprehensive_result["text_analysis"]["dimension_scores"].items():
                        result_record[f"{dimension}_텍스트점수"] = score
                        if "dimension_details" in comprehensive_result["text_analysis"]:
                            details = comprehensive_result["text_analysis"]["dimension_details"].get(dimension, {})
                            result_record[f"{dimension}_신뢰도"] = details.get("confidence", 0)
                            result_record[f"{dimension}_긍정신호"] = details.get("signals", {}).get("positive", 0)
                            result_record[f"{dimension}_부정신호"] = details.get("signals", {}).get("negative", 0)
                
                # 정량 데이터 세부 정보 추가 (신규)
                if comprehensive_result["quantitative_analysis"]["contributing_factors"]:
                    for factor_name, factor_info in comprehensive_result["quantitative_analysis"]["contributing_factors"].items():
                        clean_name = factor_name.replace("grade_", "").replace("score_", "").replace("rate_", "").replace("count_", "")
                        result_record[f"정량_{clean_name}"] = factor_info["score"]
                        result_record[f"정량_{clean_name}_기여도"] = factor_info["contribution"]
                
                # AI 피드백 생성 (활성화된 경우)
                if enable_ai and api_key:
                    # 하이브리드 결과를 포함한 상세 정보로 AI 피드백 생성
                    enhanced_opinion = f"""
                    평가 의견: {opinion}
                    
                    하이브리드 분석 결과:
                    - 종합 점수: {comprehensive_result["hybrid_analysis"]["overall_score"]}점
                    - OK 등급: {comprehensive_result["hybrid_analysis"]["grade"]}
                    - 텍스트 분석: {comprehensive_result["text_analysis"]["overall_score"]}점
                    - 정량 분석: {comprehensive_result["quantitative_analysis"]["quantitative_score"]}점
                    - 분석 신뢰도: {comprehensive_result["hybrid_analysis"]["confidence"]}%
                    """
                    
                    ai_feedback = await hybrid_analyzer.text_analyzer.generate_ai_feedback(uid, enhanced_opinion, api_key, model, max_tokens)
                    result_record["AI_장점"] = ai_feedback["ai_strengths"]
                    result_record["AI_개선점"] = ai_feedback["ai_weaknesses"]
                    result_record["AI_종합피드백"] = ai_feedback["ai_feedback"]
                    result_record["AI_처리시간"] = ai_feedback["processing_time"]
                    result_record["AI_사용모델"] = ai_feedback.get("model_used", model)
                    result_record["AI_토큰수"] = ai_feedback.get("tokens_used", max_tokens)
                    result_record["AI_오류"] = ai_feedback.get("error", "")
                    
                    if ai_feedback.get("error"):
                        ai_fail_count += 1
                    else:
                        ai_success_count += 1
                else:
                    result_record["AI_장점"] = "AI 피드백이 비활성화되어 있습니다." if not enable_ai else "API 키가 제공되지 않았습니다."
                    result_record["AI_개선점"] = "AI 피드백이 비활성화되어 있습니다." if not enable_ai else "API 키가 제공되지 않았습니다."
                    result_record["AI_종합피드백"] = "하이브리드 키워드+정량 분석만 수행되었습니다."
                
                result_record["분석시간"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result_record["분석시스템"] = "AIRISS v3.0 - OK금융그룹 완전통합 대시보드 시스템"
                
                results.append(result_record)
                
                # 진행률 업데이트
                current_processed = len(results)
                progress = (current_processed + job_data["failed"]) / total_rows * 100
                store.update_job(job_id, {
                    "processed": current_processed,
                    "progress": min(progress, 100)
                })
                
                # 속도 조절
                if enable_ai and api_key:
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"개별 하이브리드 분석 오류 - UID {uid}: {e}")
                current_failed = job_data["failed"] + 1
                store.update_job(job_id, {"failed": current_failed})
                continue
        
        # 결과 저장
        end_time = datetime.now()
        processing_time = end_time - job_data["start_time"]
        
        # 평균 점수 계산 (하이브리드 기준)
        avg_score = 0
        if results:
            avg_score = sum(r["AIRISS_v2_종합점수"] for r in results) / len(results)
        
        # 하이브리드 분석 통계
        hybrid_stats = {
            "quantitative_data_count": quantitative_data_count,
            "quantitative_usage_rate": round((quantitative_data_count / len(results)) * 100, 1) if results else 0,
            "analysis_mode": analysis_mode,
            "total_quantitative_columns": len(quantitative_cols)
        }
        
        store.update_job(job_id, {
            "results": results,
            "status": "completed",
            "end_time": end_time,
            "processing_time": f"{processing_time.seconds}초",
            "average_score": round(avg_score, 1),
            "ai_success_count": ai_success_count,
            "ai_fail_count": ai_fail_count,
            "hybrid_analysis_info": hybrid_stats  # 🆕 추가
        })
        
        # Excel 파일 생성 (v3.0)
        if results:
            await create_excel_report_v3(job_id, results, enable_ai, analysis_mode, hybrid_stats)
        
        logger.info(f"AIRISS v3.0 분석 완료: {job_id}, 성공: {len(results)}, 실패: {job_data['failed']}")
        
    except Exception as e:
        logger.error(f"AIRISS v3.0 분석 처리 오류: {e}")
        store.update_job(job_id, {
            "status": "failed",
            "error": str(e)
        })

# 🆕 NEW: v3.0 Excel 보고서 생성 함수 (v2.0과 거의 동일)
async def create_excel_report_v3(job_id: str, results: List[Dict], enable_ai: bool = False, analysis_mode: str = "hybrid", hybrid_stats: Dict = {}):
    """AIRISS v3.0 Excel 보고서 생성"""
    try:
        os.makedirs('results', exist_ok=True)
        
        # 결과 데이터프레임 생성
        df_results = pd.DataFrame(results)
        
        # OK등급별 분포 계산
        grade_distribution = df_results["OK등급"].value_counts()
        
        # v3.0 통계 요약 생성
        summary_stats = []
        summary_stats.append({
            "항목": "AIRISS 버전",
            "값": "v3.0 완전통합 대시보드",
            "설명": "텍스트 + 정량데이터 통합분석 + 개인별 조회"
        })
        
        summary_stats.append({
            "항목": "전체 분석 건수",
            "값": len(results),
            "설명": "총 분석된 직원 수"
        })
        
        summary_stats.append({
            "항목": "분석 모드",
            "값": analysis_mode,
            "설명": "적용된 분석 방식"
        })
        
        summary_stats.append({
            "항목": "평균 하이브리드 점수",
            "값": round(df_results["AIRISS_v2_종합점수"].mean(), 1),
            "설명": "전체 직원 평균 통합 점수"
        })
        
        if "정량_데이터개수" in df_results.columns:
            avg_quant_data = round(df_results["정량_데이터개수"].mean(), 1)
            summary_stats.append({
                "항목": "평균 정량데이터 수",
                "값": avg_quant_data,
                "설명": "개인당 평균 정량데이터 개수"
            })
        
        if hybrid_stats.get("quantitative_usage_rate"):
            summary_stats.append({
                "항목": "정량데이터 활용률",
                "값": f"{hybrid_stats['quantitative_usage_rate']}%",
                "설명": "정량데이터가 포함된 분석 비율"
            })
        
        # OK등급별 분포
        for grade, count in grade_distribution.items():
            percentage = (count / len(results)) * 100
            summary_stats.append({
                "항목": f"{grade} 등급",
                "값": f"{count}명 ({percentage:.1f}%)",
                "설명": f"{grade} 등급 직원 수 (하이브리드 기준)"
            })
        
        # 8대 영역별 평균 점수 (텍스트 기준)
        for dimension in AIRISS_FRAMEWORK.keys():
            col_name = f"{dimension}_텍스트점수"
            if col_name in df_results.columns:
                avg_score = round(df_results[col_name].mean(), 1)
                summary_stats.append({
                    "항목": f"{dimension} 평균",
                    "값": avg_score,
                    "설명": f"{dimension} 영역 평균 점수 (텍스트 분석)"
                })
        
        df_summary = pd.DataFrame(summary_stats)
        
        # Excel 파일 생성 (v3.0 브랜딩)
        ai_suffix = "_AI완전분석" if enable_ai else "_하이브리드분석"
        mode_suffix = f"_{analysis_mode}모드"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = f'results/OK금융그룹_AIRISS_v3.0{mode_suffix}{ai_suffix}_대시보드_{timestamp}.xlsx'
        
        with pd.ExcelWriter(result_path, engine='openpyxl') as writer:
            # 메인 결과 시트
            df_results.to_excel(writer, index=False, sheet_name='AIRISS_v3.0_분석결과')
            
            # 통계 요약 시트
            df_summary.to_excel(writer, index=False, sheet_name='v3.0_통계요약')
            
            # 8대 영역별 상세 시트 (텍스트 분석 기준)
            dimension_analysis = []
            for dimension in AIRISS_FRAMEWORK.keys():
                dimension_info = AIRISS_FRAMEWORK[dimension]
                col_name = f"{dimension}_텍스트점수"
                
                if col_name in df_results.columns:
                    scores = df_results[col_name]
                    dimension_analysis.append({
                        "영역": dimension,
                        "아이콘": dimension_info['icon'],
                        "가중치": f"{dimension_info['weight']*100}%",
                        "설명": dimension_info['description'],
                        "브랜드컬러": dimension_info['color'],
                        "평균점수": round(scores.mean(), 1),
                        "최고점수": round(scores.max(), 1),
                        "최저점수": round(scores.min(), 1),
                        "표준편차": round(scores.std(), 1),
                        "우수자수": len(scores[scores >= 80]),
                        "개선필요자수": len(scores[scores < 60])
                    })
            
            df_dimensions = pd.DataFrame(dimension_analysis)
            df_dimensions.to_excel(writer, index=False, sheet_name='영역별_텍스트분석')
            
            # 🆕 NEW: 하이브리드 분석 상세 시트
            hybrid_analysis = []
            if "AIRISS_v2_종합점수" in df_results.columns and "텍스트_종합점수" in df_results.columns:
                hybrid_scores = df_results["AIRISS_v2_종합점수"]
                text_scores = df_results["텍스트_종합점수"]
                quant_scores = df_results["정량_종합점수"] if "정량_종합점수" in df_results.columns else pd.Series([50] * len(results))
                
                hybrid_analysis.append({
                    "분석유형": "하이브리드 통합",
                    "평균점수": round(hybrid_scores.mean(), 1),
                    "최고점수": round(hybrid_scores.max(), 1),
                    "최저점수": round(hybrid_scores.min(), 1),
                    "표준편차": round(hybrid_scores.std(), 1),
                    "신뢰도": "높음 (다중소스)"
                })
                
                hybrid_analysis.append({
                    "분석유형": "텍스트 분석",
                    "평균점수": round(text_scores.mean(), 1),
                    "최고점수": round(text_scores.max(), 1),
                    "최저점수": round(text_scores.min(), 1),
                    "표준편차": round(text_scores.std(), 1),
                    "신뢰도": "중간 (키워드 기반)"
                })
                
                hybrid_analysis.append({
                    "분석유형": "정량 분석",
                    "평균점수": round(quant_scores.mean(), 1),
                    "최고점수": round(quant_scores.max(), 1),
                    "최저점수": round(quant_scores.min(), 1),
                    "표준편차": round(quant_scores.std(), 1),
                    "신뢰도": "높음 (객관적 데이터)"
                })
            
            df_hybrid = pd.DataFrame(hybrid_analysis)
            df_hybrid.to_excel(writer, index=False, sheet_name='하이브리드_비교분석')
        
        # 작업 정보에 파일 경로 저장
        store.update_job(job_id, {"result_file": result_path})
        
        logger.info(f"AIRISS v3.0 하이브리드 Excel 보고서 생성 완료: {result_path}")
        
    except Exception as e:
        logger.error(f"AIRISS v3.0 Excel 보고서 생성 오류: {e}")

# 기존 상태 확인, 다운로드 엔드포인트는 그대로 유지
@app.get("/status/{job_id}")
async def get_analysis_status(job_id: str):
    """분석 진행 상황 확인 - v3.0 정보 추가"""
    job_data = store.get_job(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    # 처리 시간 계산
    if job_data["status"] == "completed" and "end_time" in job_data:
        processing_time = job_data["end_time"] - job_data["start_time"]
    else:
        processing_time = datetime.now() - job_data["start_time"]
    
    minutes = int(processing_time.total_seconds() // 60)
    seconds = int(processing_time.total_seconds() % 60)
    time_str = f"{minutes}분 {seconds}초" if minutes > 0 else f"{seconds}초"
    
    return {
        "job_id": job_id,
        "status": job_data["status"],
        "total": job_data["total"],
        "processed": job_data["processed"],
        "failed": job_data["failed"],
        "progress": job_data["progress"],
        "processing_time": time_str,
        "average_score": job_data.get("average_score", 0),
        "error": job_data.get("error", ""),
        "ai_success_count": job_data.get("ai_success_count", 0),
        "ai_fail_count": job_data.get("ai_fail_count", 0),
        "version": job_data.get("version", "3.0"),  # 🆕 추가
        "hybrid_analysis_info": job_data.get("hybrid_analysis_info", {})  # 🆕 추가
    }

@app.get("/download/{job_id}")
async def download_results(job_id: str):
    """분석 결과 다운로드 - v3.0"""
    job_data = store.get_job(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    if job_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="아직 완료되지 않은 작업입니다")
    
    result_file = job_data.get("result_file")
    if not result_file or not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail="결과 파일을 찾을 수 없습니다")
    
    # 다운로드용 파일명 생성 (v3.0)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ai_suffix = "AI완전분석" if job_data.get("enable_ai_feedback", False) else "하이브리드분석"
    analysis_mode = job_data.get("analysis_mode", "hybrid")
    filename = f"OK금융그룹_AIRISS_v3.0_{analysis_mode}_{ai_suffix}_대시보드_{timestamp}.xlsx"
    
    return FileResponse(
        result_file,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=filename
    )

@app.get("/health")
async def health_check():
    """시스템 상태 확인 - v3.0"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "name": "AIRISS v3.0",
        "branding": "OK금융그룹 완전통합 대시보드 시스템",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "ok_branding_complete": True,
            "ok_fonts": True,
            "ok_grade_system": True,
            "8_dimension_analysis": True,
            "text_analysis": True,  # 기존 기능
            "quantitative_analysis": True,  # v2.0 기능
            "hybrid_analysis": True,  # v2.0 핵심 기능
            "dashboard_search": True,  # 🆕 v3.0 신규 기능
            "individual_profile": True,  # 🆕 v3.0 신규 기능
            "radar_chart": True,  # 🆕 v3.0 신규 기능
            "ai_feedback_enhanced": True,
            "excel_export": True,
            "real_time_progress": True,
            "batch_processing": True,
            "openai_integration": hybrid_analyzer.text_analyzer.openai_available,
            "grade_conversion": True,  # v2.0 등급 변환
            "score_normalization": True,  # v2.0 점수 정규화
            "all_functions_preserved": True,
            "complete_dashboard_system": True  # 🆕 v3.0 완전통합 대시보드
        },
        "analysis_modes": ["text", "quantitative", "hybrid"],
        "supported_grade_formats": [
            "S/A/B/C/D", "A+/A/A-/B+/B", "1/2/3/4/5", 
            "우수/양호/보통", "점수(0-100)", "백분율(%)"
        ],
        "dashboard_features": [
            "개인별 UID 검색", "실시간 레이더 차트", "하이브리드 점수 시각화",
            "AI 피드백 표시", "등급별 필터링", "작업 이력 관리"
        ]
    }

# 메인 실행부
if __name__ == "__main__":
    # 필요한 디렉토리 생성
    os.makedirs('temp', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    os.makedirs('static/fonts', exist_ok=True)
    
    # Render.com을 위한 설정 추가
    port = int(os.environ.get("PORT", 8000))
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8000")
    
    print("🎯" + "="*100)
    print("🚀 AIRISS v3.0 - OK금융그룹 완전통합 AI 대시보드 시스템")
    print("="*104)
    print("✅ v2.0 텍스트+정량 하이브리드 분석 기능 100% 완전 유지")
    print("🆕 개인별 UID 조회 시각화 대시보드 신규 추가")
    print("🔍 실시간 검색 + 레이더 차트 + 점수 시각화")
    print("✅ OK금융그룹 CI 가이드라인 완벽 적용")
    print("✅ OK체 폰트 (OKBold, OKMedium, OKLight) 지원")
    print("✅ OK브랜드 컬러 (Orange #FF5722, Brown #4A4A4A)")
    print("✅ OK등급 체계 (OK★★★~OK D) 적용")
    print("✅ OpenAI GPT-3.5/GPT-4 완전 통합")
    print("✅ 8대 영역 정밀 분석 엔진")
    print("✅ 평가등급 자동 변환 (S/A/B/C, 우수/양호/보통 등)")
    print("✅ 점수 정규화 (0-100, 1-5, 백분율 등)")
    print("✅ 하이브리드 가중 평균 스코어링")
    print("✅ 정량데이터 품질 분석")
    print("🆕 개인별 대시보드 조회 시스템")
    print("🆕 실시간 레이더 차트 시각화")
    print("🆕 작업 이력 관리 및 검색")
    print("🆕 등급별 필터링 기능")
    print("🆕 Chart.js 기반 인터랙티브 차트")
    print("✅ 실시간 진행률 모니터링")
    print("✅ 완전한 Excel 보고서 생성")
    print("="*104)
    print(f"🌐 메인 페이지: {render_url}")
    print(f"🔍 개인별 조회: {render_url}/search")
    print(f"📊 API 문서: {render_url}/docs")
    print(f"❤️  시스템 상태: {render_url}/health")
    print("🤖 OpenAI 모듈:", "설치됨" if hybrid_analyzer.text_analyzer.openai_available else "미설치")
    print("🎨 OK체 폰트 경로: /static/fonts/")
    print("🔬 지원 분석 모드: 텍스트 | 정량 | 하이브리드")
    print("📊 지원 등급 형식: S/A/B/C/D, 우수/양호/보통, 1-5점, 0-100점, 백분율")
    print("🆕 완전통합 대시보드: 분석 + 업로드 + 조회 + 시각화")
    print("⭐ AIRISS v3.0 완전통합 대시보드 시스템 완성!")
    print("="*104)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",  # 변경!
            port=port,       # 변경!
            reload=False,
            access_log=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 서버 시작 오류: {e}")
        print("📋 해결 방법:")
        print("1. 포트가 사용 중인지 확인")
        print("2. 관리자 권한으로 실행")
        print("3. 방화벽 설정 확인")
        print("4. OK체 폰트 파일 확인: static/fonts/")
        print("5. NumPy 설치: pip install numpy")
        print("6. OpenAI 모듈 설치: pip install openai")
        print("7. Chart.js는 CDN에서 자동 로드됩니다")
        # Render에서는 input() 사용 불가이므로 제거
        # input("엔터를 눌러 종료...")