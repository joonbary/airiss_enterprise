# AIRISS v4.0 - OK금융그룹 AI 기반 직원 성과/역량 스코어링 시스템

## 프로젝트 개요

AIRISS(AI-based Intelligent Rating & Insight Scoring System)는 OK금융그룹의 전 직원을 대상으로 하는 AI 기반 종합 성과 평가 시스템입니다.

### 주요 기능
- 8대 영역 기반 다차원 평가
- 텍스트 + 정량 데이터 하이브리드 분석
- OK등급 체계 (OK★★★ ~ OK D)
- OpenAI GPT 기반 상세 피드백
- 실시간 대시보드 및 시각화
- 개인별 성과 조회 및 비교 분석

## 기술 스택

### Backend
- FastAPI (Python 3.10+)
- PostgreSQL 14
- Redis 7
- SQLAlchemy 2.0
- Alembic

### Frontend
- React 18
- TypeScript
- Material-UI
- Chart.js / Recharts

### DevOps
- Docker & Docker Compose
- GitHub Actions
- Prometheus + Grafana

## 설치 및 실행

### 1. 환경 설정
```
cp .env.example .env
# .env 파일 편집하여 환경 변수 설정
```

### 2. Docker Compose로 실행
```
docker-compose up -d
```

### 3. 데이터베이스 마이그레이션
```
docker-compose exec backend alembic upgrade head
```

### 4. 접속
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 라이센스

Copyright (c) 2024 OK Financial Group. All rights reserved.
