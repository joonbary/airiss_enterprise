#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWS Elastic Beanstalk PID 오류 즉시 해결 스크립트 (Unicode 안전 버전)
"""

import os
import shutil
import subprocess
from datetime import datetime

def backup_current_files():
    """현재 파일들 백업"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 현재 Procfile 백업
    if os.path.exists("Procfile"):
        shutil.copy("Procfile", f"Procfile_backup_{timestamp}")
        print(f"✅ 기존 Procfile 백업: Procfile_backup_{timestamp}")
    
    return timestamp

def create_fixed_procfile():
    """AWS EB 최적화된 Procfile 생성"""
    
    # 3가지 옵션 제공
    procfile_options = {
        "simple": "web: uvicorn application:application --host 0.0.0.0 --port $PORT --log-level info",
        
        "stable": "web: gunicorn application:application --workers=1 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:$PORT --timeout=180 --keep-alive=2 --max-requests=1000 --preload --access-logfile=- --error-logfile=- --log-level=info",
        
        "robust": "web: gunicorn application:application --workers=2 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:$PORT --timeout=300 --keep-alive=5 --max-requests=500 --max-requests-jitter=50 --preload --access-logfile=- --error-logfile=- --log-level=info"
    }
    
    # stable 버전 사용 (가장 안정적)
    with open("Procfile", "w", encoding="utf-8") as f:
        f.write(procfile_options["stable"])
    
    print("✅ AWS EB 최적화 Procfile 생성 완료")
    print("   - PID 파일 제거")
    print("   - Daemon 옵션 제거") 
    print("   - AWS EB 환경 최적화")
    
    # 백업용 옵션들도 생성
    for name, content in procfile_options.items():
        with open(f"Procfile_{name}_fixed", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   📁 백업: Procfile_{name}_fixed")

def create_ebextensions():
    """AWS EB 확장 설정 (선택사항)"""
    
    if not os.path.exists(".ebextensions"):
        os.makedirs(".ebextensions")
    
    # 01_python.config
    python_config = """option_settings:
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
    PYTHONUNBUFFERED: "1"
  aws:elasticbeanstalk:container:python:
    WSGIPath: "application.py"
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: static
"""
    
    with open(".ebextensions/01_python.config", "w", encoding="utf-8") as f:
        f.write(python_config)
    
    print("✅ .ebextensions 설정 생성")

def verify_application_py():
    """application.py 호환성 확인"""
    
    if not os.path.exists("application.py"):
        print("❌ application.py 파일이 없습니다!")
        return False
    
    with open("application.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 필수 요소 확인
    checks = [
        ("application = app", "AWS EB 호환성 변수"),
        ("FastAPI", "FastAPI 임포트"),
        ("@app.get", "엔드포인트 정의")
    ]
    
    all_good = True
    for check, desc in checks:
        if check in content:
            print(f"✅ {desc}: 확인됨")
        else:
            print(f"❌ {desc}: 누락")
            all_good = False
    
    return all_good

def create_deployment_script():
    """배포 스크립트 생성"""
    
    # 이모지 제거한 안전한 버전
    script_content = """#!/bin/bash
# AWS EB 배포 스크립트

echo "AIRISS v4 AWS EB 배포 시작..."

# 1. EB CLI 확인
if ! command -v eb &> /dev/null; then
    echo "EB CLI가 설치되지 않았습니다."
    echo "pip install awsebcli 로 설치하세요."
    exit 1
fi

# 2. 현재 상태 확인
echo "현재 EB 환경 상태 확인..."
eb status

# 3. 배포 실행
echo "배포 실행 중..."
eb deploy

# 4. 상태 확인
echo "배포 완료 - 상태 확인..."
eb status
eb health

echo "배포 완료! 애플리케이션 URL:"
eb open
"""
    
    with open("deploy_fixed.sh", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # Windows 배치 파일도 생성
    batch_content = """@echo off
echo AIRISS v4 AWS EB 배포 시작...

REM 1. EB CLI 확인
where eb >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo EB CLI가 설치되지 않았습니다.
    echo pip install awsebcli 로 설치하세요.
    exit /b 1
)

REM 2. 현재 상태 확인
echo 현재 EB 환경 상태 확인...
eb status

REM 3. 배포 실행
echo 배포 실행 중...
eb deploy

REM 4. 상태 확인
echo 배포 완료 - 상태 확인...
eb status
eb health

echo 배포 완료! 
eb open
"""
    
    with open("deploy_fixed.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print("✅ 배포 스크립트 생성: deploy_fixed.sh, deploy_fixed.bat")

def create_troubleshooting_guide():
    """트러블슈팅 가이드 생성"""
    
    guide_content = """# AWS Elastic Beanstalk PID 오류 해결 가이드

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
"""
    
    with open("AWS_PID_FIX_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print("✅ 트러블슈팅 가이드 생성: AWS_PID_FIX_GUIDE.md")

def main():
    """메인 실행"""
    print("AWS Elastic Beanstalk PID 오류 해결 스크립트")
    print("=" * 60)
    
    # 1. 백업
    timestamp = backup_current_files()
    
    # 2. 고정된 Procfile 생성
    create_fixed_procfile()
    
    # 3. application.py 검증
    if not verify_application_py():
        print("⚠️ application.py 파일을 수정해야 할 수 있습니다.")
    
    # 4. EB 확장 설정
    create_ebextensions()
    
    # 5. 배포 스크립트
    create_deployment_script()
    
    # 6. 가이드 생성
    create_troubleshooting_guide()
    
    print("\n해결 완료!")
    print("=" * 60)
    print("다음 단계:")
    print("1. deploy_fixed.bat 실행하여 배포")
    print("2. eb health 로 상태 확인")
    print("3. 문제 지속시 AWS_PID_FIX_GUIDE.md 참조")
    print("\n생성된 파일들:")
    print("   - Procfile (수정됨)")
    print("   - .ebextensions/01_python.config")
    print("   - deploy_fixed.bat / deploy_fixed.sh")
    print("   - AWS_PID_FIX_GUIDE.md")
    print("   - Procfile_backup_" + timestamp)

if __name__ == "__main__":
    main()
