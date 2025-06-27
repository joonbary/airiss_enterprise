# app/schemas/schemas.py
# AIRISS v4.0 모든 스키마 클래스 - 오류 해결 버전

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# ============================================================================
# 파일 업로드 관련 스키마
# ============================================================================

class DataQuality(BaseModel):
    """데이터 품질 정보"""
    text_completeness: float = Field(..., description="텍스트 데이터 완성도 (%)")
    quant_completeness: float = Field(..., description="정량 데이터 완성도 (%)")
    total_records: int = Field(..., description="전체 레코드 수")
    text_non_empty: Optional[int] = Field(0, description="비어있지 않은 텍스트 레코드 수")
    quant_non_empty: Optional[int] = Field(0, description="비어있지 않은 정량 레코드 수")

class FileUploadResponse(BaseModel):
    """파일 업로드 응답 스키마"""
    id: str = Field(..., description="파일 고유 ID")
    filename: str = Field(..., description="업로드된 파일명")
    total_records: int = Field(..., description="총 레코드 수")
    column_count: int = Field(..., description="컬럼 수")
    columns: List[str] = Field(..., description="모든 컬럼 리스트")
    uid_columns: List[str] = Field(..., description="UID 컬럼 리스트")
    opinion_columns: List[str] = Field(..., description="의견/텍스트 컬럼 리스트")
    quantitative_columns: List[str] = Field(..., description="정량 데이터 컬럼 리스트")
    airiss_ready: bool = Field(..., description="AIRISS 분석 가능 여부")
    hybrid_ready: bool = Field(..., description="하이브리드 분석 가능 여부")
    data_quality: DataQuality = Field(..., description="데이터 품질 정보")
    upload_time: str = Field(..., description="업로드 시간")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    message: str = Field(..., description="업로드 완료 메시지")

class FileInfoResponse(BaseModel):
    """파일 정보 조회 응답 스키마"""
    id: str = Field(..., description="파일 고유 ID")
    filename: str = Field(..., description="파일명")
    total_records: int = Field(..., description="총 레코드 수")
    column_count: int = Field(..., description="컬럼 수")
    columns: List[str] = Field(..., description="모든 컬럼 리스트")
    uid_columns: List[str] = Field(..., description="UID 컬럼 리스트")
    opinion_columns: List[str] = Field(..., description="의견/텍스트 컬럼 리스트")
    quantitative_columns: List[str] = Field(..., description="정량 데이터 컬럼 리스트")
    upload_time: str = Field(..., description="업로드 시간")
    file_size: int = Field(..., description="파일 크기 (bytes)")
    airiss_ready: bool = Field(..., description="AIRISS 분석 가능 여부")
    hybrid_ready: bool = Field(..., description="하이브리드 분석 가능 여부")
    data_quality: DataQuality = Field(..., description="데이터 품질 정보")

# ============================================================================
# 분석 관련 스키마  
# ============================================================================

class AnalysisRequest(BaseModel):
    """분석 요청 스키마"""
    file_id: str = Field(..., description="분석할 파일 ID")
    sample_size: int = Field(10, description="분석할 샘플 크기", ge=1, le=10000)
    analysis_mode: str = Field("hybrid", description="분석 모드", pattern="^(text|quantitative|hybrid)$")
    enable_ai: bool = Field(False, description="AI 피드백 활성화 여부")
    openai_api_key: Optional[str] = Field("", description="OpenAI API 키")
    openai_model: str = Field("gpt-3.5-turbo", description="OpenAI 모델")
    max_tokens: int = Field(1200, description="최대 토큰 수", ge=100, le=4000)

class AnalysisResponse(BaseModel):
    """분석 응답 스키마"""
    success: bool = Field(..., description="분석 성공 여부")
    message: str = Field(..., description="응답 메시지")
    job_id: Optional[str] = Field(None, description="작업 ID")
    file_id: Optional[str] = Field(None, description="파일 ID")

class AnalysisStartRequest(BaseModel):
    """분석 시작 요청 스키마"""
    file_id: str = Field(..., description="분석할 파일 ID")
    sample_size: int = Field(10, description="분석할 샘플 크기")
    analysis_mode: str = Field("hybrid", description="분석 모드")
    enable_ai: bool = Field(False, description="AI 피드백 활성화")
    openai_api_key: Optional[str] = Field("", description="OpenAI API 키")
    openai_model: str = Field("gpt-3.5-turbo", description="OpenAI 모델")
    max_tokens: int = Field(1200, description="최대 토큰 수")

class AnalysisStartResponse(BaseModel):
    """분석 시작 응답 스키마"""
    job_id: str = Field(..., description="생성된 작업 ID")
    status: str = Field(..., description="작업 상태")
    message: str = Field(..., description="응답 메시지")
    ai_feedback_enabled: bool = Field(..., description="AI 피드백 활성화 여부")
    analysis_mode: str = Field(..., description="분석 모드")
    estimated_time: Optional[str] = Field(None, description="예상 소요 시간")

class AnalysisProgress(BaseModel):
    """분석 진행률 정보"""
    current: int = Field(..., description="현재 처리된 수")
    total: int = Field(..., description="전체 처리할 수")
    percentage: float = Field(..., description="진행률 (%)")
    current_uid: Optional[str] = Field(None, description="현재 처리 중인 UID")
    current_score: Optional[float] = Field(None, description="현재 처리된 점수")
    elapsed_time: Optional[str] = Field(None, description="경과 시간")

class AnalysisStatusResponse(BaseModel):
    """분석 상태 응답 스키마"""
    job_id: str = Field(..., description="작업 ID")
    status: str = Field(..., description="작업 상태")
    progress: AnalysisProgress = Field(..., description="진행률 정보")
    processed: int = Field(..., description="처리 완료 수")
    failed: int = Field(..., description="실패 수")
    total: int = Field(..., description="전체 수")
    average_score: Optional[float] = Field(None, description="평균 점수")
    start_time: str = Field(..., description="시작 시간")
    end_time: Optional[str] = Field(None, description="종료 시간")
    processing_time: Optional[str] = Field(None, description="처리 시간")
    error: Optional[str] = Field(None, description="오류 메시지")

class AnalysisResult(BaseModel):
    """개별 분석 결과"""
    UID: str = Field(..., description="직원 UID")
    원본의견: Optional[str] = Field("", description="원본 의견 텍스트")
    AIRISS_v4_종합점수: float = Field(..., description="AIRISS v4.0 하이브리드 종합점수")
    OK등급: str = Field(..., description="OK 등급")
    등급설명: str = Field(..., description="등급 설명")
    백분위: str = Field(..., description="백분위 순위")
    분석신뢰도: float = Field(..., description="분석 신뢰도")
    텍스트_종합점수: float = Field(..., description="텍스트 분석 점수")
    텍스트_등급: str = Field(..., description="텍스트 분석 등급")
    정량_종합점수: float = Field(..., description="정량 분석 점수")
    정량_신뢰도: float = Field(..., description="정량 분석 신뢰도")
    정량_데이터품질: str = Field(..., description="정량 데이터 품질")
    정량_데이터개수: int = Field(..., description="정량 데이터 개수")
    분석모드: str = Field(..., description="사용된 분석 모드")
    텍스트_가중치: Union[float, str] = Field(..., description="텍스트 분석 가중치")
    정량_가중치: Union[float, str] = Field(..., description="정량 분석 가중치")
    AI_장점: Optional[str] = Field("", description="AI 분석 장점")
    AI_개선점: Optional[str] = Field("", description="AI 분석 개선점")
    AI_종합피드백: Optional[str] = Field("", description="AI 종합 피드백")
    AI_처리시간: Optional[float] = Field(0, description="AI 처리 시간")
    AI_사용모델: Optional[str] = Field("", description="사용된 AI 모델")
    AI_토큰수: Optional[int] = Field(0, description="사용된 토큰 수")
    AI_오류: Optional[str] = Field("", description="AI 처리 오류")
    분석시간: str = Field(..., description="분석 완료 시간")
    분석시스템: str = Field(..., description="분석 시스템 정보")

class AnalysisResultsResponse(BaseModel):
    """분석 결과 응답 스키마"""
    job_id: str = Field(..., description="작업 ID")
    total_results: int = Field(..., description="총 결과 수")
    results: List[AnalysisResult] = Field(..., description="분석 결과 리스트")
    summary: Dict[str, Any] = Field(..., description="결과 요약 정보")
    analysis_info: Dict[str, Any] = Field(..., description="분석 정보")

# ============================================================================
# 직원 관련 스키마
# ============================================================================

class Employee(BaseModel):
    """직원 정보 스키마"""
    uid: str = Field(..., description="직원 UID")
    name: Optional[str] = Field(None, description="직원 이름")
    department: Optional[str] = Field(None, description="부서")
    position: Optional[str] = Field(None, description="직책")
    email: Optional[str] = Field(None, description="이메일")

class EmployeeSearchRequest(BaseModel):
    """직원 검색 요청 스키마"""
    job_id: Optional[str] = Field(None, description="작업 ID")
    uid: Optional[str] = Field(None, description="직원 UID")
    grade: Optional[str] = Field(None, description="등급 필터")
    department: Optional[str] = Field(None, description="부서 필터")
    limit: int = Field(50, description="결과 제한 수", ge=1, le=1000)

class EmployeeSearchResponse(BaseModel):
    """직원 검색 응답 스키마"""
    employees: List[AnalysisResult] = Field(..., description="검색된 직원 리스트")
    total_count: int = Field(..., description="총 검색 결과 수")
    query_info: Dict[str, Any] = Field(..., description="검색 쿼리 정보")

# ============================================================================
# 일반 응답 스키마
# ============================================================================

class HealthResponse(BaseModel):
    """헬스체크 응답 스키마"""
    status: str = Field(..., description="서비스 상태")
    version: str = Field(..., description="버전 정보")
    timestamp: str = Field(..., description="응답 시간")
    database: Optional[Dict[str, Any]] = Field(None, description="데이터베이스 상태")

class ErrorResponse(BaseModel):
    """오류 응답 스키마"""
    detail: str = Field(..., description="오류 상세 메시지")
    error_code: Optional[str] = Field(None, description="오류 코드")
    timestamp: str = Field(..., description="오류 발생 시간")

class SuccessResponse(BaseModel):
    """성공 응답 스키마"""
    message: str = Field(..., description="성공 메시지")
    data: Optional[Dict[str, Any]] = Field(None, description="응답 데이터")
    timestamp: str = Field(..., description="응답 시간")

# ============================================================================
# WebSocket 관련 스키마
# ============================================================================

class WebSocketMessage(BaseModel):
    """WebSocket 메시지 스키마"""
    type: str = Field(..., description="메시지 타입")
    data: Dict[str, Any] = Field(..., description="메시지 데이터")
    timestamp: str = Field(..., description="메시지 시간")
    client_id: Optional[str] = Field(None, description="클라이언트 ID")

class AnalysisProgressMessage(BaseModel):
    """분석 진행률 WebSocket 메시지"""
    type: str = Field("analysis_progress", description="메시지 타입")
    job_id: str = Field(..., description="작업 ID")
    progress: AnalysisProgress = Field(..., description="진행률 정보")
    timestamp: str = Field(..., description="메시지 시간")

# ============================================================================
# 작업 관리 스키마
# ============================================================================

class JobInfo(BaseModel):
    """작업 정보 스키마"""
    job_id: str = Field(..., description="작업 ID")
    file_id: str = Field(..., description="파일 ID")
    status: str = Field(..., description="작업 상태")
    analysis_mode: str = Field(..., description="분석 모드")
    sample_size: int = Field(..., description="샘플 크기")
    start_time: str = Field(..., description="시작 시간")
    end_time: Optional[str] = Field(None, description="종료 시간")
    processed: int = Field(..., description="처리 완료 수")
    total: int = Field(..., description="전체 수")

class JobListResponse(BaseModel):
    """작업 목록 응답 스키마"""
    jobs: List[JobInfo] = Field(..., description="작업 목록")
    total_count: int = Field(..., description="총 작업 수")
    active_jobs: int = Field(..., description="활성 작업 수")
    completed_jobs: int = Field(..., description="완료된 작업 수")

# ============================================================================
# 구성 및 설정 스키마
# ============================================================================

class SystemConfig(BaseModel):
    """시스템 설정 스키마"""
    version: str = Field(..., description="시스템 버전")
    analysis_modes: List[str] = Field(..., description="지원 분석 모드")
    max_file_size: int = Field(..., description="최대 파일 크기")
    supported_formats: List[str] = Field(..., description="지원 파일 형식")
    features: Dict[str, bool] = Field(..., description="기능 활성화 상태")

class DatabaseConfig(BaseModel):
    """데이터베이스 설정 스키마"""
    db_type: str = Field(..., description="데이터베이스 타입")
    db_path: str = Field(..., description="데이터베이스 경로")
    connection_status: str = Field(..., description="연결 상태")
    total_files: int = Field(..., description="총 파일 수")
    total_jobs: int = Field(..., description="총 작업 수")