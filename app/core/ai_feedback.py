# app/core/ai_feedback.py
"""AI 피드백 생성 엔진"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIFeedbackEngine:
    def __init__(self):
        self.openai_available = False
        try:
            import openai
            self.openai = openai
            self.openai_available = True
            logger.info("✅ OpenAI 모듈 로드 성공")
        except ImportError:
            logger.warning("⚠️ OpenAI 모듈 없음 - AI 피드백 사용 불가")
    
    async def generate_feedback(
        self,
        uid: str,
        opinion: str,
        analysis_result: Dict[str, Any],
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1200
    ) -> Dict[str, Any]:
        """AI 피드백 생성"""
        
        if not self.openai_available:
            return self._get_default_feedback("OpenAI 모듈이 설치되지 않았습니다.")
        
        if not api_key:
            return self._get_default_feedback("API 키가 제공되지 않았습니다.")
        
        start_time = datetime.now()
        
        try:
            client = self.openai.OpenAI(api_key=api_key.strip())
            
            # 프롬프트 생성
            prompt = self._create_prompt(uid, opinion, analysis_result)
            
            # OpenAI API 호출
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 OK금융그룹의 전문 HR 분석가입니다. AIRISS 8대 영역을 기반으로 직원 평가를 분석하고 구체적인 피드백을 제공합니다."
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
            strengths, weaknesses, complete_feedback = self._parse_response(feedback_text)
            
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
            logger.error(f"OpenAI API 오류: {e}")
            return self._get_default_feedback(f"AI 분석 오류: {str(e)}")
    
    def _create_prompt(self, uid: str, opinion: str, analysis_result: Dict[str, Any]) -> str:
        """AI 프롬프트 생성"""
        hybrid_score = analysis_result.get("hybrid_analysis", {}).get("overall_score", 0)
        grade = analysis_result.get("hybrid_analysis", {}).get("grade", "")
        text_score = analysis_result.get("text_analysis", {}).get("overall_score", 0)
        quant_score = analysis_result.get("quantitative_analysis", {}).get("quantitative_score", 0)
        
        return f"""
OK금융그룹 직원 {uid}의 평가 의견을 AIRISS 8대 영역을 기반으로 종합 분석해주세요.

【평가 의견】
{opinion[:1500]}

【분석 결과】
- 하이브리드 종합점수: {hybrid_score}점
- OK등급: {grade}
- 텍스트 분석: {text_score}점
- 정량 분석: {quant_score}점

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
"""
    
    def _parse_response(self, response: str) -> tuple:
        """AI 응답 파싱"""
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
                elif section.startswith('종합 피드백]'):
                    content = section.replace('종합 피드백]', '').strip()
                    feedback = content
            
            return strengths, weaknesses, feedback
            
        except Exception as e:
            logger.error(f"AI 응답 파싱 오류: {e}")
            return "장점 분석 중 오류", "개선점 분석 중 오류", response
    
    def _get_default_feedback(self, error_msg: str) -> Dict[str, Any]:
        """기본 피드백 반환"""
        return {
            "ai_strengths": error_msg,
            "ai_weaknesses": "AI 분석을 사용할 수 없습니다.",
            "ai_feedback": "키워드 기반 분석만 수행되었습니다.",
            "processing_time": 0,
            "model_used": "none",
            "tokens_used": 0,
            "error": error_msg
        }