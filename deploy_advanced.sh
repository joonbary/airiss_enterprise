#!/bin/bash
# AIRISS v4.0 고급 배포 스크립트 - 프로덕션 환경 완벽 지원

set -e  # 오류 발생 시 즉시 중단

# 색상 출력을 위한 함수들
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 사용법 표시
show_usage() {
    echo "AIRISS v4.0 Advanced Deployment Script"
    echo ""
    echo "사용법: $0 [환경] [도메인] [포트] [옵션들]"
    echo ""
    echo "환경:"
    echo "  development  - 개발 환경 (기본값)"
    echo "  staging      - 스테이징 환경"
    echo "  production   - 프로덕션 환경"
    echo ""
    echo "옵션:"
    echo "  --ssl        - HTTPS 설정 활성화"
    echo "  --monitoring - 모니터링 도구 설치"
    echo "  --backup     - 데이터베이스 백업 설정"
    echo "  --react      - React 앱도 함께 배포"
    echo "  --cluster    - Docker Swarm 클러스터 모드"
    echo "  --help       - 이 도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 development localhost 8002"
    echo "  $0 production airiss.okfinancial.com 443 --ssl --monitoring"
    echo "  $0 staging staging.airiss.com 8002 --react --backup"
}

# 기본값 설정
ENVIRONMENT=${1:-development}
DOMAIN=${2:-localhost}
PORT=${3:-8002}
ENABLE_SSL=false
ENABLE_MONITORING=false
ENABLE_BACKUP=false
DEPLOY_REACT=false
CLUSTER_MODE=false

# 명령행 옵션 파싱
shift 3 2>/dev/null || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --ssl)
            ENABLE_SSL=true
            shift
            ;;
        --monitoring)
            ENABLE_MONITORING=true
            shift
            ;;
        --backup)
            ENABLE_BACKUP=true
            shift
            ;;
        --react)
            DEPLOY_REACT=true
            shift
            ;;
        --cluster)
            CLUSTER_MODE=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "알 수 없는 옵션: $1"
            show_usage
            exit 1
            ;;
    esac
done

# 배포 정보 출력
print_status "🚀 AIRISS v4.0 Advanced Deployment 시작"
echo "==============================================="
echo "환경: $ENVIRONMENT"
echo "도메인: $DOMAIN"
echo "포트: $PORT"
echo "SSL: $ENABLE_SSL"
echo "모니터링: $ENABLE_MONITORING"
echo "백업: $ENABLE_BACKUP"
echo "React 배포: $DEPLOY_REACT"
echo "클러스터 모드: $CLUSTER_MODE"
echo "==============================================="

# 환경별 설정
case $ENVIRONMENT in
    development)
        COMPOSE_FILE="docker-compose.yml"
        BUILD_TARGET="development"
        REPLICAS=1
        ;;
    staging)
        COMPOSE_FILE="docker-compose.staging.yml"
        BUILD_TARGET="staging"
        REPLICAS=2
        ;;
    production)
        COMPOSE_FILE="docker-compose.production.yml"
        BUILD_TARGET="production"
        REPLICAS=3
        ;;
    *)
        print_error "지원하지 않는 환경: $ENVIRONMENT"
        exit 1
        ;;
esac

# 필수 도구 확인
check_requirements() {
    print_status "필수 도구 확인 중..."
    
    command -v docker >/dev/null 2>&1 || {
        print_error "Docker가 설치되지 않았습니다."
        exit 1
    }
    
    command -v docker-compose >/dev/null 2>&1 || {
        print_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    }
    
    if [ "$DEPLOY_REACT" = true ]; then
        command -v node >/dev/null 2>&1 || {
            print_error "Node.js가 설치되지 않았습니다."
            exit 1
        }
        
        command -v npm >/dev/null 2>&1 || {
            print_error "npm이 설치되지 않았습니다."
            exit 1
        }
    fi
    
    print_success "모든 필수 도구가 설치되어 있습니다."
}

# 환경별 Docker Compose 파일 생성
create_compose_file() {
    print_status "Docker Compose 파일 생성 중..."
    
    cat > $COMPOSE_FILE << EOF
version: '3.8'

services:
  airiss-app:
    build:
      context: .
      dockerfile: Dockerfile
      target: $BUILD_TARGET
    ports:
      - "${PORT}:8002"
    environment:
      - ENVIRONMENT=${ENVIRONMENT}
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8002
      - WS_HOST=${DOMAIN}
    volumes:
      - airiss_data:/app/data
      - airiss_logs:/app/logs
      - airiss_uploads:/app/uploads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      replicas: ${REPLICAS}
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
EOF

    if [ "$DEPLOY_REACT" = true ]; then
        cat >> $COMPOSE_FILE << EOF

  airiss-frontend:
    build:
      context: ./airiss-v4-frontend
      dockerfile: Dockerfile.react
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://${DOMAIN}:${PORT}
    depends_on:
      - airiss-app
    restart: unless-stopped
EOF
    fi

    if [ "$ENABLE_SSL" = true ]; then
        cat >> $COMPOSE_FILE << EOF

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - airiss-app
    restart: unless-stopped
EOF
    fi

    if [ "$ENABLE_MONITORING" = true ]; then
        cat >> $COMPOSE_FILE << EOF

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
EOF
    fi

    cat >> $COMPOSE_FILE << EOF

volumes:
  airiss_data:
  airiss_logs:
  airiss_uploads:
EOF

    if [ "$ENABLE_MONITORING" = true ]; then
        cat >> $COMPOSE_FILE << EOF
  prometheus_data:
  grafana_data:
EOF
    fi

    print_success "Docker Compose 파일이 생성되었습니다: $COMPOSE_FILE"
}

# Nginx 설정 파일 생성 (SSL 사용 시)
create_nginx_config() {
    if [ "$ENABLE_SSL" = true ]; then
        print_status "Nginx SSL 설정 파일 생성 중..."
        
        mkdir -p ssl
        
        cat > nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream airiss_backend {
        server airiss-app:8002;
    }
    
    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name ${DOMAIN};
        return 301 https://\$server_name\$request_uri;
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name ${DOMAIN};
        
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        location / {
            proxy_pass http://airiss_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        location /ws/ {
            proxy_pass http://airiss_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_cache_bypass \$http_upgrade;
        }
    }
}
EOF
        
        print_success "Nginx 설정 파일이 생성되었습니다."
        print_warning "SSL 인증서를 ssl/ 디렉토리에 배치해주세요:"
        print_warning "  - ssl/fullchain.pem"
        print_warning "  - ssl/privkey.pem"
    fi
}

# React 앱 빌드
build_react_app() {
    if [ "$DEPLOY_REACT" = true ]; then
        print_status "React 앱 빌드 중..."
        
        cd airiss-v4-frontend
        
        # 환경별 설정
        cat > .env.production << EOF
REACT_APP_API_URL=http://${DOMAIN}:${PORT}
REACT_APP_WS_URL=ws://${DOMAIN}:${PORT}
REACT_APP_ENVIRONMENT=${ENVIRONMENT}
EOF
        
        npm ci
        npm run build
        
        # React용 Dockerfile 생성
        cat > Dockerfile.react << EOF
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.react.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
EOF

        # React용 Nginx 설정
        cat > nginx.react.conf << EOF
server {
    listen 3000;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://airiss-app:8002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
        
        cd ..
        print_success "React 앱 빌드가 완료되었습니다."
    fi
}

# 모니터링 설정
setup_monitoring() {
    if [ "$ENABLE_MONITORING" = true ]; then
        print_status "모니터링 설정 중..."
        
        # Prometheus 설정
        cat > prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'airiss-app'
    static_configs:
      - targets: ['airiss-app:8002']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
EOF
        
        print_success "모니터링 설정이 완료되었습니다."
    fi
}

# 백업 스크립트 생성
create_backup_script() {
    if [ "$ENABLE_BACKUP" = true ]; then
        print_status "백업 스크립트 생성 중..."
        
        cat > backup.sh << 'EOF'
#!/bin/bash
# AIRISS v4.0 백업 스크립트

BACKUP_DIR="/backup/airiss"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 데이터베이스 백업
docker exec $(docker ps -q -f "name=airiss-app") cp /app/airiss.db /tmp/airiss_backup_$DATE.db
docker cp $(docker ps -q -f "name=airiss-app"):/tmp/airiss_backup_$DATE.db $BACKUP_DIR/

# 업로드 파일 백업
docker run --rm -v airiss_uploads:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/uploads_$DATE.tar.gz -C /data .

# 로그 백업
docker run --rm -v airiss_logs:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/logs_$DATE.tar.gz -C /data .

# 오래된 백업 삭제 (30일 이상)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "백업 완료: $DATE"
EOF
        
        chmod +x backup.sh
        
        # Crontab 등록을 위한 안내
        print_success "백업 스크립트가 생성되었습니다: backup.sh"
        print_warning "자동 백업을 위해 crontab에 다음을 추가하세요:"
        print_warning "0 2 * * * /path/to/backup.sh"
    fi
}

# 애플리케이션 배포
deploy_application() {
    print_status "애플리케이션 배포 중..."
    
    # 기존 컨테이너 정리
    if [ -f $COMPOSE_FILE ]; then
        docker-compose -f $COMPOSE_FILE down 2>/dev/null || true
    fi
    
    # 이미지 빌드 및 시작
    if [ "$CLUSTER_MODE" = true ]; then
        print_status "Docker Swarm 클러스터 모드로 배포 중..."
        
        # Swarm 초기화 (이미 초기화되어 있으면 무시)
        docker swarm init 2>/dev/null || true
        
        # Stack 배포
        docker stack deploy -c $COMPOSE_FILE airiss-stack
        
        print_success "클러스터 배포가 완료되었습니다."
        print_status "서비스 상태 확인: docker service ls"
    else
        print_status "표준 Docker Compose 모드로 배포 중..."
        
        docker-compose -f $COMPOSE_FILE build
        docker-compose -f $COMPOSE_FILE up -d
        
        print_success "배포가 완료되었습니다."
    fi
}

# 헬스 체크
health_check() {
    print_status "애플리케이션 헬스 체크 중..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://$DOMAIN:$PORT/health >/dev/null 2>&1; then
            print_success "애플리케이션이 정상적으로 실행 중입니다!"
            break
        fi
        
        print_warning "헬스 체크 시도 $attempt/$max_attempts..."
        sleep 5
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "헬스 체크 실패. 로그를 확인해주세요."
        docker-compose -f $COMPOSE_FILE logs --tail=50 airiss-app
        exit 1
    fi
}

# 배포 후 정보 출력
show_deployment_info() {
    print_success "🎉 AIRISS v4.0 배포가 완료되었습니다!"
    echo ""
    echo "==============================================="
    echo "📱 접속 정보:"
    if [ "$ENABLE_SSL" = true ]; then
        echo "   메인 URL: https://$DOMAIN"
        echo "   API 문서: https://$DOMAIN/docs"
        echo "   대시보드: https://$DOMAIN/dashboard"
    else
        echo "   메인 URL: http://$DOMAIN:$PORT"
        echo "   API 문서: http://$DOMAIN:$PORT/docs"
        echo "   대시보드: http://$DOMAIN:$PORT/dashboard"
    fi
    
    if [ "$DEPLOY_REACT" = true ]; then
        echo "   React 앱: http://$DOMAIN:3000"
    fi
    
    if [ "$ENABLE_MONITORING" = true ]; then
        echo "   모니터링: http://$DOMAIN:3001 (Grafana)"
        echo "   메트릭: http://$DOMAIN:9090 (Prometheus)"
    fi
    
    echo ""
    echo "🔧 관리 명령어:"
    echo "   로그 확인: docker-compose -f $COMPOSE_FILE logs -f"
    echo "   서비스 재시작: docker-compose -f $COMPOSE_FILE restart"
    echo "   서비스 중지: docker-compose -f $COMPOSE_FILE down"
    
    if [ "$ENABLE_BACKUP" = true ]; then
        echo "   백업 실행: ./backup.sh"
    fi
    
    echo "==============================================="
}

# 메인 실행 함수
main() {
    print_status "AIRISS v4.0 Advanced Deployment 시작"
    
    check_requirements
    create_compose_file
    create_nginx_config
    build_react_app
    setup_monitoring
    create_backup_script
    deploy_application
    health_check
    show_deployment_info
    
    print_success "모든 배포 과정이 완료되었습니다! 🚀"
}

# 스크립트 실행
main "$@"