# airiss_sdk.py
"""
AIRISS v4.0 B2B Python SDK
기업 고객을 위한 간편한 API 접근 라이브러리
"""

import requests
import pandas as pd
from typing import Dict, List, Optional, Union
import json
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIRISSClient:
    """AIRISS API 클라이언트"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.airiss.ai"):
        """
        Args:
            api_key: AIRISS API 키
            base_url: API 서버 URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def analyze_employees(self, 
                         data: Union[pd.DataFrame, str],
                         text_columns: List[str],
                         quant_columns: List[str],
                         options: Optional[Dict] = None) -> Dict:
        """
        직원 데이터 분석
        
        Args:
            data: 분석할 데이터 (DataFrame 또는 CSV 파일 경로)
            text_columns: 텍스트 분석 대상 컬럼
            quant_columns: 정량 분석 대상 컬럼
            options: 추가 옵션 (bias_check, predictions 등)
        
        Returns:
            분석 결과 딕셔너리
        """
        # DataFrame을 CSV로 변환
        if isinstance(data, pd.DataFrame):
            csv_data = data.to_csv(index=False)
            files = {'file': ('data.csv', csv_data, 'text/csv')}
        else:
            with open(data, 'rb') as f:
                files = {'file': (data, f, 'text/csv')}
        
        # 파일 업로드
        upload_response = self.session.post(
            f"{self.base_url}/api/v2/upload",
            files=files
        )
        upload_response.raise_for_status()
        
        file_id = upload_response.json()['file_id']
        
        # 분석 요청
        analysis_payload = {
            'file_id': file_id,
            'text_columns': text_columns,
            'quant_columns': quant_columns,
            'options': options or {}
        }
        
        analysis_response = self.session.post(
            f"{self.base_url}/api/v2/analyze",
            json=analysis_payload
        )
        analysis_response.raise_for_status()
        
        job_id = analysis_response.json()['job_id']
        
        # 결과 대기
        return self._wait_for_results(job_id)
    
    def check_bias(self, employee_scores: pd.DataFrame) -> Dict:
        """
        편향 검사 실행
        
        Args:
            employee_scores: 직원별 점수 데이터
        
        Returns:
            편향 분석 결과
        """
        response = self.session.post(
            f"{self.base_url}/api/v2/bias-check",
            json={'data': employee_scores.to_dict('records')}
        )
        response.raise_for_status()
        return response.json()
    
    def predict_performance(self, 
                           employee_id: str,
                           historical_data: pd.DataFrame) -> Dict:
        """
        개인 성과 예측
        
        Args:
            employee_id: 직원 ID
            historical_data: 과거 성과 데이터
        
        Returns:
            예측 결과
        """
        response = self.session.post(
            f"{self.base_url}/api/v2/predict",
            json={
                'employee_id': employee_id,
                'historical_data': historical_data.to_dict('records')
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_recommendations(self, employee_id: str) -> Dict:
        """
        개인화된 성장 추천
        
        Args:
            employee_id: 직원 ID
        
        Returns:
            성장 경로 추천
        """
        response = self.session.get(
            f"{self.base_url}/api/v2/employees/{employee_id}/recommendations"
        )
        response.raise_for_status()
        return response.json()
    
    def generate_report(self, 
                       analysis_id: str,
                       report_type: str = 'executive') -> bytes:
        """
        분석 보고서 생성
        
        Args:
            analysis_id: 분석 ID
            report_type: 보고서 유형 (executive, detailed, fairness)
        
        Returns:
            PDF 보고서 바이트
        """
        response = self.session.get(
            f"{self.base_url}/api/v2/reports/{analysis_id}",
            params={'type': report_type}
        )
        response.raise_for_status()
        return response.content
    
    def _wait_for_results(self, job_id: str, timeout: int = 300) -> Dict:
        """분석 결과 대기"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = self.session.get(
                f"{self.base_url}/api/v2/jobs/{job_id}"
            )
            response.raise_for_status()
            
            job_status = response.json()
            
            if job_status['status'] == 'completed':
                return job_status['results']
            elif job_status['status'] == 'failed':
                raise Exception(f"분석 실패: {job_status.get('error')}")
            
            time.sleep(2)
        
        raise TimeoutError("분석 시간 초과")

# 사용 예시
if __name__ == "__main__":
    # 클라이언트 초기화
    client = AIRISSClient(api_key="your-api-key")
    
    # 직원 데이터 준비
    employee_data = pd.DataFrame({
        '직원ID': ['EMP001', 'EMP002'],
        '이름': ['김철수', '이영희'],
        '부서': ['개발', '마케팅'],
        'KPI_달성률': [95, 88],
        '평가_피드백': [
            '우수한 성과를 보이고 있으며 팀워크가 뛰어남',
            '창의적인 아이디어로 프로젝트 성공에 기여'
        ]
    })
    
    # 분석 실행
    results = client.analyze_employees(
        data=employee_data,
        text_columns=['평가_피드백'],
        quant_columns=['KPI_달성률'],
        options={
            'include_bias_check': True,
            'include_predictions': True
        }
    )
    
    print(f"분석 완료: {results['summary']}")
    
    # 편향 검사
    bias_report = client.check_bias(
        pd.DataFrame(results['employee_scores'])
    )
    print(f"편향 분석: {bias_report['summary']}")
    
    # 개인별 추천
    for emp_id in ['EMP001', 'EMP002']:
        recommendations = client.get_recommendations(emp_id)
        print(f"{emp_id} 추천사항: {recommendations}")