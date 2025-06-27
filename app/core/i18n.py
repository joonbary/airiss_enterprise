# app/core/i18n.py
"""
AIRISS v4.0 다국어 지원 시스템
한국어, 영어, 일본어, 중국어 지원
"""

from typing import Dict, Optional
import json
import os

class I18nManager:
    """다국어 관리 시스템"""
    
    def __init__(self, default_lang: str = 'ko'):
        self.default_lang = default_lang
        self.translations = {}
        self.supported_languages = ['ko', 'en', 'ja', 'zh']
        self._load_translations()
    
    def _load_translations(self):
        """번역 파일 로드"""
        base_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'translations'
        )
        
        for lang in self.supported_languages:
            file_path = os.path.join(base_path, f'{lang}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
    
    def t(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        """
        번역 텍스트 반환
        
        Args:
            key: 번역 키
            lang: 언어 코드
            **kwargs: 템플릿 변수
        
        Returns:
            번역된 텍스트
        """
        lang = lang or self.default_lang
        
        if lang not in self.translations:
            lang = self.default_lang
        
        text = self.translations.get(lang, {}).get(key, key)
        
        # 템플릿 변수 치환
        for k, v in kwargs.items():
            text = text.replace(f'{{{k}}}', str(v))
        
        return text
    
    def get_language_name(self, lang_code: str) -> str:
        """언어 이름 반환"""
        language_names = {
            'ko': '한국어',
            'en': 'English',
            'ja': '日本語',
            'zh': '中文'
        }
        return language_names.get(lang_code, lang_code)

# 번역 파일 예시
# translations/ko.json
ko_translations = {
    "app.title": "AIRISS - AI 기반 인재 분석 시스템",
    "app.description": "직원의 성과와 역량을 AI로 분석하고 예측합니다",
    
    "nav.home": "홈",
    "nav.analysis": "분석",
    "nav.reports": "보고서",
    "nav.settings": "설정",
    
    "analysis.upload": "파일 업로드",
    "analysis.select_columns": "분석 컬럼 선택",
    "analysis.text_columns": "텍스트 컬럼",
    "analysis.quant_columns": "정량 컬럼",
    "analysis.start": "분석 시작",
    "analysis.progress": "분석 진행 중... {progress}%",
    
    "bias.title": "공정성 분석",
    "bias.detected": "편향이 감지되었습니다",
    "bias.not_detected": "편향이 감지되지 않았습니다",
    "bias.risk_level": "위험 수준: {level}",
    
    "prediction.title": "성과 예측",
    "prediction.6month": "6개월 후 예상 성과",
    "prediction.attrition_risk": "이직 위험도",
    "prediction.growth_path": "추천 성장 경로",
    
    "report.generating": "보고서 생성 중...",
    "report.download": "보고서 다운로드",
    
    "error.file_type": "지원하지 않는 파일 형식입니다",
    "error.column_missing": "필수 컬럼이 누락되었습니다",
    "error.analysis_failed": "분석 중 오류가 발생했습니다"
}

# translations/en.json
en_translations = {
    "app.title": "AIRISS - AI-based Talent Analytics System",
    "app.description": "Analyze and predict employee performance and capabilities with AI",
    
    "nav.home": "Home",
    "nav.analysis": "Analysis",
    "nav.reports": "Reports",
    "nav.settings": "Settings",
    
    "analysis.upload": "Upload File",
    "analysis.select_columns": "Select Analysis Columns",
    "analysis.text_columns": "Text Columns",
    "analysis.quant_columns": "Quantitative Columns",
    "analysis.start": "Start Analysis",
    "analysis.progress": "Analyzing... {progress}%",
    
    "bias.title": "Fairness Analysis",
    "bias.detected": "Bias detected",
    "bias.not_detected": "No bias detected",
    "bias.risk_level": "Risk Level: {level}",
    
    "prediction.title": "Performance Prediction",
    "prediction.6month": "Expected Performance in 6 Months",
    "prediction.attrition_risk": "Attrition Risk",
    "prediction.growth_path": "Recommended Growth Path",
    
    "report.generating": "Generating report...",
    "report.download": "Download Report",
    
    "error.file_type": "Unsupported file type",
    "error.column_missing": "Required columns are missing",
    "error.analysis_failed": "Analysis failed"
}

# 사용 예시
i18n = I18nManager()

# 기본 언어 (한국어)
print(i18n.t('app.title'))  # AIRISS - AI 기반 인재 분석 시스템

# 영어
print(i18n.t('app.title', lang='en'))  # AIRISS - AI-based Talent Analytics System

# 템플릿 변수 사용
print(i18n.t('analysis.progress', progress=75))  # 분석 진행 중... 75%