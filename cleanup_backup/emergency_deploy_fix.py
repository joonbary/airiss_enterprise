#!/usr/bin/env python3
"""
AIRISS v4.1 긴급 배포 수정 스크립트
AWS Elastic Beanstalk 플랫폼 비활성화 문제 해결
"""

import os
import shutil
import subprocess
import zipfile
from datetime import datetime

def create_emergency_deployment_package():
    """긴급 배포 패키지 생성"""
    
    print("🚨 AIRISS v4.1 긴급 배포 패키지 생성 중...")
    
    # 타임스탬프
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 새로운 배포 패키지명
    package_name = f"airiss_v4_emergency_fix_{timestamp}.zip"
    
    # 포함할 파일들 (필수만)
    files_to_include = [
        "app/",
        "static/",
        ".ebextensions/",
        "application.py",
        "requirements.txt",
        "runtime.txt",
        "Procfile",
        "init_database.py",
        "create_db_files.py",
        ".env.example"
    ]
    
    # 수정된 runtime.txt (Python 3.11 고정)
    runtime_content = "python-3.11"
    with open("runtime.txt", "w") as f:
        f.write(runtime_content)
    print("✅ runtime.txt updated to Python 3.11")
    
    # 수정된 Procfile (타임아웃 증가)
    procfile_content = "web: gunicorn application:application -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 600 --keep-alive 5 --max-requests 500"
    with open("Procfile", "w") as f:
        f.write(procfile_content)
    print("✅ Procfile updated with increased timeout")
    
    # ZIP 파일 생성
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in files_to_include:
            if os.path.exists(item):
                if os.path.isfile(item):
                    zipf.write(item)
                    print(f"✅ Added file: {item}")
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        # __pycache__ 제외
                        dirs[:] = [d for d in dirs if not d.startswith('__pycache__')]
                        for file in files:
                            if not file.endswith('.pyc'):
                                file_path = os.path.join(root, file)
                                zipf.write(file_path)
                    print(f"✅ Added directory: {item}")
            else:
                print(f"⚠️ Not found: {item}")
    
    print(f"🎉 긴급 배포 패키지 생성 완료: {package_name}")
    return package_name

def create_new_environment_guide():
    """새 환경 생성 가이드"""
    
    guide_content = """
# 🚨 AIRISS v4.1 긴급 배포 가이드

## 즉시 실행 단계

### 1️⃣ 새 Elastic Beanstalk 환경 생성 (권장)

```
환경명: AIRISS-v41-Production
플랫폼: Python 3.11 running on 64bit Amazon Linux 2
애플리케이션 코드: 새로 생성된 ZIP 파일 업로드
```

### 2️⃣ 환경 설정

```
인스턴스 타입: t3.large (필수 - AI 모델용)
Auto Scaling: 최소 1, 최대 2
로드 밸런서: Application Load Balancer
헬스체크: /health
```

### 3️⃣ 모니터링 설정

```
CloudWatch 로그 활성화
Enhanced 헬스 리포팅 활성화
알림: 에러율 5% 이상 시 알림
```

## 예상 비용
- t3.large: 약 $60/월
- CloudWatch + S3: 약 $10/월
- 총 예상 비용: $70/월

## 배포 후 확인사항
1. http://[your-env-url]/health - 헬스체크
2. http://[your-env-url]/ - 메인 화면
3. http://[your-env-url]/docs - API 문서

## 성공 기준
✅ 헬스체크 통과
✅ 메인 화면 로딩
✅ 파일 업로드 테스트
✅ 분석 기능 동작

## 문제 발생 시
1. CloudWatch 로그 확인
2. /var/log/eb-hooks.log 확인
3. Python 버전 및 의존성 검증
"""
    
    with open("EMERGENCY_DEPLOY_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print("📝 긴급 배포 가이드 생성: EMERGENCY_DEPLOY_GUIDE.md")

def main():
    """메인 실행"""
    print("🚨 AIRISS v4.1 긴급 배포 수정 스크립트 시작")
    print("=" * 60)
    
    # 현재 디렉토리 확인
    if not os.path.exists("app/main.py"):
        print("❌ AIRISS 프로젝트 루트 디렉토리에서 실행해주세요")
        return
    
    # 1. 긴급 배포 패키지 생성
    package_name = create_emergency_deployment_package()
    
    # 2. 배포 가이드 생성
    create_new_environment_guide()
    
    print("\n" + "=" * 60)
    print("🎯 다음 단계:")
    print(f"1. AWS Console > Elastic Beanstalk")
    print(f"2. 새 환경 생성")
    print(f"3. {package_name} 업로드")
    print(f"4. EMERGENCY_DEPLOY_GUIDE.md 참조")
    print("\n💡 예상 배포 시간: 10-15분")
    print("💰 예상 월 비용: $70 (t3.large)")

if __name__ == "__main__":
    main()
