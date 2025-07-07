# 🚨 AIRISS AWS 배포 연결 문제 긴급 해결 가이드

## 현재 상황
- URL: https://airiss-v4.ap-northeast-2.elasticbeanstalk.com
- 오류: ERR_CONNECTION_TIMED_OUT
- 배포 방식: AWS Elastic Beanstalk

## 🚀 즉시 시도해볼 해결책 (우선순위순)

### 1️⃣ 가장 먼저 시도 (재배포)
```bash
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
eb deploy
```
- 현재 코드를 다시 배포
- 임시 네트워크 문제일 가능성

### 2️⃣ 상태 확인
```bash
eb status
eb health
eb logs --all
```
- 현재 환경 상태 파악
- 오류 로그 확인

### 3️⃣ 새 환경 생성 (위 방법 실패 시)
```bash
eb create production-v2
```
- 완전히 새로운 환경 생성
- 기존 환경에 문제가 있는 경우

### 4️⃣ 최소 버전으로 테스트
```bash
# application.py만 사용하여 배포
eb deploy
```

## 🔍 문제 원인 분석

### 가능한 원인들:
1. **Elastic Beanstalk 환경 문제**
   - 인스턴스가 시작되지 않음
   - 헬스체크 실패

2. **보안 그룹 설정**
   - HTTP/HTTPS 포트 막힘
   - 인바운드 규칙 누락

3. **코드 오류**
   - application.py 실행 오류
   - 의존성 문제

4. **리소스 한계**
   - t3.micro 메모리 부족
   - 할당량 초과

## 🛠️ 단계별 해결 프로세스

### Step 1: 스크립트 실행
```bash
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
python aws_deployment_troubleshoot.py
```

### Step 2: 자동 수정 시도
```bash
fix_aws_deployment.bat
```

### Step 3: AWS Console 확인
1. AWS Console → Elastic Beanstalk
2. airiss-v4 환경 선택
3. Health 탭에서 상태 확인
4. Events 탭에서 오류 확인

### Step 4: 보안 그룹 확인
1. EC2 → Security Groups
2. EB 관련 보안 그룹 선택
3. Inbound rules에 HTTP(80) 추가

### Step 5: 최후 수단 (전체 재구축)
```bash
eb terminate
eb create production
eb deploy
```

## 📞 즉시 연락 필요한 경우

### 다음 중 하나라도 해당되면 즉시 연락:
- [ ] AWS 계정 문제 (권한, 결제)
- [ ] 1-2시간 내 해결 필요
- [ ] 중요 데모/발표 예정

### 연락처:
- 기술팀: [연락처]
- AWS 지원: [계정별 지원]

## ⚡ 빠른 체크리스트

### 지금 당장 확인할 것들:
- [ ] eb status 실행
- [ ] eb health 실행  
- [ ] eb logs --all 실행
- [ ] AWS Console에서 환경 상태 확인
- [ ] application.py 로컬 실행 테스트

### 30분 내 시도할 것들:
- [ ] eb deploy (재배포)
- [ ] eb create production-v2 (새 환경)
- [ ] 보안 그룹 확인
- [ ] 인스턴스 타입 변경 (t3.small)

## 🎯 성공 기준
✅ https://airiss-v4.ap-northeast-2.elasticbeanstalk.com 접속 가능
✅ /health 엔드포인트 정상 응답
✅ JSON 형태 응답 확인

## 💡 예방책 (향후)
1. **모니터링 설정**
   - CloudWatch 알람
   - 헬스체크 자동화

2. **백업 배포 환경**
   - Staging 환경 운영
   - Blue-Green 배포

3. **로컬 개발 환경**
   - Docker 컨테이너
   - 로컬 테스트 자동화

---
**⏰ 긴급도: 높음 | 예상 해결 시간: 30분-2시간**
