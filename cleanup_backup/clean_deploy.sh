#!/bin/bash
# 완전한 클린 배포 스크립트

echo "=== AIRISS v4.0 클린 배포 시작 ==="

# 1. 기존 배포 파일 정리
echo "1. 기존 배포 파일 정리..."
rm -rf .elasticbeanstalk/app_versions/*
rm -rf .elasticbeanstalk/logs/*

# 2. 강제 배포 (새로운 버전 번호로)
echo "2. 강제 배포 시작..."
eb deploy --label "airiss-simple-$(date +%Y%m%d%H%M%S)" --timeout 10

# 3. 상태 확인
echo "3. 배포 상태 확인..."
eb status

# 4. Health check
echo "4. Health check..."
eb health

# 5. 로그 확인
echo "5. 최신 로그 확인..."
eb logs --all

echo "=== 배포 완료 ==="