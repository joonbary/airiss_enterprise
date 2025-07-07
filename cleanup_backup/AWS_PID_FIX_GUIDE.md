# AWS Elastic Beanstalk PID 오류 해결 가이드

## 문제 상황
- `failed to read file /var/pids/web.pid` 오류
- AWS EB healthd가 web 프로세스 추적 실패

## 해결 방법

### 1. Procfile 최적화
기존 Procfile에서 문제가 되는 옵션들 제거:
- `--pid=/var/pids/web.pid` (PID 파일 불필요)
- `--daemon-off` (AWS EB와 충돌)
- `mkdir -p /var/pids` (권한 문제)

### 2. 권장 Procfile 설정
```
web: gunicorn application:application --workers=1 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:$PORT --timeout=180 --keep-alive=2 --max-requests=1000 --preload --access-logfile=- --error-logfile=- --log-level=info
```

### 3. 배포 단계
1. `python fix_aws_pid_error_fixed.py` 실행
2. `deploy_fixed.bat` 실행
3. `eb health` 로 상태 확인

### 4. 모니터링
```bash
# 배포 상태 확인
eb status

# 헬스 체크
eb health

# 로그 확인
eb logs
```

### 5. 응급 복구
문제 발생시:
```bash
# 이전 버전으로 롤백
eb deploy --version-label=<이전버전>

# 환경 재시작
eb restart
```

## 추가 최적화

### requirements.txt 확인
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pydantic==2.7.0
```

### .ebextensions 설정
AWS EB 환경 최적화를 위한 추가 설정이 자동 생성됩니다.

## 지원
문제 지속시:
1. `eb logs` 로 상세 로그 확인
2. AWS EB 콘솔에서 환경 상태 점검
3. 이 스크립트 재실행
