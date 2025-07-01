# Changelog

AIRISS 프로젝트의 모든 주요 변경사항이 이 파일에 문서화됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 기반으로 하며,
이 프로젝트는 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)을 따릅니다.

---

## [4.0.0] - 2025-01-27

### Added (추가됨)
- 🎯 **8대 영역 종합 분석 시스템**
  - 업무성과, 리더십협업, 커뮤니케이션, 전문성학습
  - 태도열정, 혁신창의, 고객지향, 윤리준수
- 🧠 **하이브리드 AI 분석 엔진**
  - 텍스트 + 정량 데이터 통합 분석
  - OpenAI GPT 기반 피드백 생성
- 📊 **OK등급 체계** (OK★★★ ~ OK D)
- 🎛️ **실시간 대시보드**
  - React 기반 반응형 웹 인터페이스
  - Chart.js 기반 시각화
  - WebSocket 실시간 업데이트
- 🔐 **보안 시스템**
  - JWT 기반 인증
  - 권한별 접근 제어
  - 개인정보 암호화
- 📱 **PWA 지원**
  - 모바일 최적화
  - 오프라인 캐싱
  - 푸시 알림
- 🔍 **고급 분석 기능**
  - 개인별 상세 분석
  - 부서/팀 비교 분석
  - 시간별 추이 분석
- 📋 **대량 처리 시스템**
  - Excel 파일 업로드
  - 일괄 분석 처리
  - 진행률 실시간 모니터링
- 🎨 **사용자 경험**
  - 다크/라이트 테마
  - 반응형 디자인
  - 키보드 단축키
  - 온보딩 투어

### Technical Features (기술적 특징)
- **Backend**: FastAPI 0.104.1 기반 REST API
- **Frontend**: React 18 + TypeScript
- **Database**: SQLite (개발) / PostgreSQL (운영)
- **AI/ML**: OpenAI GPT-4, scikit-learn
- **Real-time**: WebSocket 연결
- **Caching**: Redis 지원
- **Testing**: 종합 테스트 스위트
- **Monitoring**: 시스템 헬스 체크
- **DevOps**: Docker 지원

### Performance (성능)
- 개별 분석: < 2초 응답시간
- 대량 분석: 1000명 < 5분 처리
- 동시 사용자: 100명 지원
- 데이터 처리량: 10MB Excel 파일 지원

### Security (보안)
- 데이터 암호화 (AES-256)
- HTTPS/TLS 1.3 지원
- SQL Injection 방지
- XSS 보호
- CSRF 토큰 검증
- 접근 로그 기록

---

## [3.x.x] - 이전 버전들

### 3.2.0 - 프로토타입 단계
- 기본 텍스트 분석 구현
- 간단한 점수 산출 로직
- 기본 웹 인터페이스

### 3.1.0 - 개념 검증 (POC)
- 텍스트 감정 분석 테스트
- 정량 데이터 처리 로직
- 기본 통계 분석

### 3.0.0 - 초기 연구
- 요구사항 정의
- 기술 스택 선정
- 아키텍처 설계

---

## 향후 계획 (Upcoming)

### [5.0.0] - AI 고도화 (예정: 2025 Q2)
- 딥러닝 NLP 모델 도입 (BERT, GPT)
- 실시간 편향 탐지 시스템
- 성과 예측 AI 모델
- 다국어 지원 (한/영/중/일)

### [6.0.0] - SaaS 플랫폼화 (예정: 2025 Q4)
- 멀티 테넌트 아키텍처
- 클라우드 네이티브 배포
- API 마켓플레이스
- 제3자 통합 지원

---

## 변경사항 유형

- `Added` (추가됨): 새로운 기능
- `Changed` (변경됨): 기존 기능의 변경사항
- `Deprecated` (지원 중단 예정): 곧 제거될 기능
- `Removed` (제거됨): 제거된 기능
- `Fixed` (수정됨): 버그 수정
- `Security` (보안): 보안 관련 수정사항

---

## 릴리스 노트

각 버전의 상세한 릴리스 노트는 [GitHub Releases](https://github.com/joonbary/airiss_enterprise/releases)에서 확인할 수 있습니다.

---

*이 파일은 매 릴리스마다 업데이트됩니다.*
