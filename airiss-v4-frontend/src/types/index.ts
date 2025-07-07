// 분석 결과 타입
export interface AnalysisResult {
  job_id: string;
  status: string;
  total_analyzed: number;
  average_score: number;
  processing_time: string;
  grade_distribution: {
    [key: string]: number;
  };
  results?: EmployeeResult[];
}

// 직원 분석 결과
export interface EmployeeResult {
  UID: string;
  AIRISS_v4_종합점수: number;
  OK등급: string;
  등급설명: string;
  백분위: string;
  분석신뢰도: number;
  텍스트_종합점수: number;
  정량_종합점수: number;
  AI_장점?: string;
  AI_개선점?: string;
  AI_종합피드백?: string;
  [key: string]: any; // 8대 영역 점수 등 동적 필드
}

// 파일 업로드 응답
export interface FileUploadResponse {
  file_id: string;
  filename: string;
  total_records: number;
  columns: string[];
  uid_columns: string[];
  opinion_columns: string[];
  quantitative_columns: string[];
  airiss_ready: boolean;
  hybrid_ready: boolean;
}

// 분석 시작 응답
export interface AnalysisStartResponse {
  job_id: string;
  status: string;
  message: string;
}

// 분석 상태 응답
export interface AnalysisStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  processed: number;
  total: number;
  error?: string;
}

// 대시보드 통계
export interface DashboardStats {
  total_analyses: number;
  total_employees: number;
  average_score: number;
  recent_analyses: RecentAnalysis[];
}

export interface RecentAnalysis {
  job_id: string;
  filename: string;
  processed: number;
  average_score: number;
  created_at: string;
}

// WebSocket 메시지
export interface WebSocketMessage {
  type: 'progress' | 'complete' | 'error' | 'status';
  data: any;
}