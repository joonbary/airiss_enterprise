# 🚀 AWS EC2 + Docker 배포 가이드

## 📋 왜 EC2 + Docker인가?
- 완전한 제어권
- 사용자 정의 환경
- 비용 효율적 (장기 사용 시)
- 확장성
- 다른 서비스와 쉬운 통합

## 🎯 Step 1: Dockerfile 최적화 (이미 존재)
현재 프로젝트에 Dockerfile이 있지만 최적화 버전을 제공:

```dockerfile
FROM python:3.9-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 데이터베이스 초기화
RUN python init_database.py

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🎯 Step 2: docker-compose.prod.yml
```yaml
version: '3.8'

services:
  airiss:
    build: .
    ports:
      - "80:8000"
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - airiss
    restart: unless-stopped
```

## 🎯 Step 3: EC2 인스턴스 생성
1. **AWS Console → EC2**
2. **Launch Instance**
   - AMI: Amazon Linux 2
   - Instance Type: t3.micro (프리 티어) 또는 t3.small
   - Security Group: HTTP(80), HTTPS(443), SSH(22) 허용
   - Key Pair: 새로 생성 또는 기존 사용

## 🎯 Step 4: EC2 서버 설정
```bash
# 1. EC2 연결
ssh -i your-key.pem ec2-user@your-instance-ip

# 2. Docker 설치
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 3. Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Git 설치 및 코드 다운로드
sudo yum install -y git
git clone https://github.com/YOUR_USERNAME/airiss_enterprise.git
cd airiss_enterprise
```

## 🎯 Step 5: 배포 실행
```bash
# 1. 프로덕션 빌드
docker-compose -f docker-compose.prod.yml build

# 2. 서비스 시작
docker-compose -f docker-compose.prod.yml up -d

# 3. 상태 확인
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs

# 4. 접속 테스트
curl http://localhost/health
```

## 🎯 Step 6: 도메인 및 SSL 설정
```bash
# Let's Encrypt SSL 인증서 설치
sudo yum install -y certbot
sudo certbot certonly --standalone -d yourdomain.com

# Nginx 설정에 SSL 인증서 경로 추가
```

## 🎯 Step 7: 자동 업데이트 스크립트
```bash
#!/bin/bash
# deploy.sh
echo "🚀 AIRISS 자동 배포 시작..."

cd /home/ec2-user/airiss_enterprise
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

echo "✅ 배포 완료!"
```

## 💰 비용 예상
- t3.micro (프리 티어): $0/월 (12개월)
- t3.small: 월 $16.80
- Elastic IP: 월 $3.60
- 총 예상 비용: 월 $0-20

## 🎯 장점
✅ 완전한 제어권
✅ 비용 효율적
✅ 사용자 정의 환경
✅ 도커 기반 이식성
✅ CI/CD 파이프라인 구축 가능
