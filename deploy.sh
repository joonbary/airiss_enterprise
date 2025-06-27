#!/bin/bash

# AIRISS v4.0 Enhanced - 웹 배포 스크립트
# 이 스크립트는 AIRISS v4.0을 프로덕션 환경에 배포합니다.

set -e  # 오류 발생 시 스크립트 중단

echo "=============================================="
echo "   AIRISS v4.0 Enhanced 웹 배포 스크립트"
echo "=============================================="
echo

# 컬러 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 설정
AIRISS_VERSION="4.0.1"
DEPLOY_ENV=${1:-production}
DOMAIN=${2:-localhost}
PORT=${3:-8002}

print_status "배포 환경: $DEPLOY_ENV"
print_status "도메인: $DOMAIN"
print_status "포트: $PORT"
echo

# 1. 사전 요구사항 확인
print_status "1. 사전 요구사항 확인 중..."

# Docker 확인
if ! command -v docker &> /dev/null; then
    print_error "Docker가 설치되지 않았습니다."
    print_warning "Docker를 설치해주세요: https://docs.docker.com/get-docker/"
    exit 1
fi

# Docker Compose 확인
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose가 설치되지 않았습니다."
    print_warning "Docker Compose를 설치해주세요: https://docs.docker.com/compose/install/"
    exit 1
fi

print_success "Docker 및 Docker Compose 확인 완료"

# 2. 기존 컨테이너 정리
print_status "2. 기존 AIRISS 컨테이너 정리 중..."

if [ "$(docker ps -q -f name=airiss)" ]; then
    print_warning "기존 AIRISS 컨테이너를 중지합니다..."
    docker-compose down
fi

print_success "컨테이너 정리 완료"

# 3. 이미지 빌드
print_status "3. AIRISS v$AIRISS_VERSION 이미지 빌드 중..."

if [ "$DEPLOY_ENV" == "development" ]; then
    docker-compose build --no-cache
else
    docker-compose -f docker-compose.yml build --no-cache
fi

print_success "이미지 빌드 완료"

# 4. 환경 설정 파일 생성
print_status "4. 환경 설정 파일 생성 중..."

cat > .env << EOF
# AIRISS v4.0 Enhanced 환경 설정
AIRISS_ENV=$DEPLOY_ENV
SERVER_HOST=0.0.0.0
SERVER_PORT=$PORT
WS_HOST=$DOMAIN
DOMAIN=$DOMAIN

# 보안 설정
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=http://$DOMAIN:$PORT,https://$DOMAIN

# 데이터베이스 설정
DB_PATH=/app/data/airiss.db

# 로그 설정
LOG_LEVEL=INFO
LOG_FILE=/app/logs/airiss.log

# 생성 시간
CREATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

print_success "환경 설정 파일 생성 완료"

# 5. 컨테이너 시작
print_status "5. AIRISS v$AIRISS_VERSION 컨테이너 시작 중..."

if [ "$DEPLOY_ENV" == "development" ]; then
    docker-compose up -d
else
    docker-compose -f docker-compose.yml up -d
fi

print_success "컨테이너 시작 완료"

# 6. 헬스체크
print_status "6. 서비스 헬스체크 중..."

max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        print_success "헬스체크 통과 (시도 $attempt/$max_attempts)"
        break
    else
        print_warning "헬스체크 대기 중... (시도 $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    print_error "헬스체크 실패 - 서비스가 정상적으로 시작되지 않았습니다."
    print_warning "로그를 확인해주세요: docker-compose logs airiss-app"
    exit 1
fi

# 7. 배포 완료 정보 출력
echo
echo "=============================================="
print_success "AIRISS v$AIRISS_VERSION 배포 완료!"
echo "=============================================="
echo
echo "📋 접속 정보:"
echo "   🌐 메인 UI (Enhanced): http://$DOMAIN:$PORT/"
echo "   📊 개발자 대시보드:     http://$DOMAIN:$PORT/dashboard"
echo "   📖 API 문서:           http://$DOMAIN:$PORT/docs"
echo "   💊 헬스체크:           http://$DOMAIN:$PORT/health"
echo
echo "🐳 Docker 명령어:"
echo "   컨테이너 상태 확인:     docker-compose ps"
echo "   로그 확인:             docker-compose logs -f airiss-app"
echo "   컨테이너 중지:         docker-compose down"
echo "   컨테이너 재시작:       docker-compose restart"
echo
echo "📁 데이터 위치:"
echo "   SQLite DB:            /app/data/airiss.db"
echo "   업로드 파일:          /app/uploads/"
echo "   로그 파일:            /app/logs/"
echo
echo "🔧 관리 도구:"
echo "   모니터링:             docker stats airiss-v4-enhanced"
echo "   데이터 백업:          docker exec airiss-v4-enhanced cp /app/data/airiss.db /backup/"
echo
print_warning "중요: 프로덕션 환경에서는 HTTPS 설정과 방화벽 구성을 완료해주세요."
echo
print_success "배포 스크립트 완료!"
