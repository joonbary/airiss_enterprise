#!/bin/bash
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
