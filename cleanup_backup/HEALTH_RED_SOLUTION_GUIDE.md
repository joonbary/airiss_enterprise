# AIRISS Health Red 원인 분석 및 해결 가이드

## 🔍 Health Red 발생 원인 TOP 5

### 1️⃣ 애플리케이션 시작 실패 (60% 확률)
**증상:** 
- eb logs에서 ImportError, ModuleNotFoundError
- "Application failed to start"
- Port binding 실패

**해결방법:**
```bash
# 로그 확인
eb logs --all | grep -i "error\|exception"

# requirements.txt 검증
pip check

# 로컬 테스트
python application.py
```

### 2️⃣ 헬스체크 엔드포인트 응답 실패 (25% 확률)
**증상:**
- / 또는 /health 엔드포인트 500 오류
- 응답 시간 초과 (30초+)
- JSON 형식 오류

**해결방법:**
- 강화된 application_health_enhanced.py 사용
- 다중 헬스체크 엔드포인트 구성
- 시스템 리소스 모니터링 추가

### 3️⃣ 메모리/CPU 리소스 부족 (10% 확률)
**증상:**
- "Memory usage too high"
- CPU 100% 사용률
- OOMKilled 에러

**해결방법:**
```bash
# 인스턴스 타입 업그레이드
eb config

# 메모리 사용량 최적화
- 불필요한 라이브러리 제거
- gunicorn worker 수 조정
```

### 4️⃣ 네트워크/보안그룹 문제 (3% 확률)
**증상:**
- Connection timeout
- Port 접근 불가
- Security group 오류

**해결방법:**
- AWS Console에서 보안그룹 확인
- Port 80/443 인바운드 규칙 점검

### 5️⃣ EB 플랫폼 버전 호환성 (2% 확률)
**증상:**
- Python 버전 불일치
- 플랫폼 업데이트 실패

**해결방법:**
```bash
# 플랫폼 버전 확인
eb platform list-versions

# 호환성 확인
eb config save --cfg=current
```

## 🎯 단계별 진단 체크리스트

### Phase 1: 기본 진단 (5분)
- [ ] `eb status` - 전체 상태 확인
- [ ] `eb health --refresh` - 헬스체크 상태
- [ ] `eb logs --all | tail -50` - 최근 로그 50줄

### Phase 2: 심화 진단 (10분)  
- [ ] `eb logs --all | grep -i error` - 에러만 필터링
- [ ] 로컬에서 `python application.py` 테스트
- [ ] `curl http://localhost:8000/` 로컬 헬스체크

### Phase 3: 해결 시도 (15분)
- [ ] `eb restart` - 재시작 시도
- [ ] 강화된 application.py 적용
- [ ] 새 버전 배포 `eb deploy`

### Phase 4: 검증 (5분)
- [ ] `eb health --refresh` - 최종 상태 확인
- [ ] 엔드포인트 직접 테스트
- [ ] 모니터링 설정

## ⚡ 긴급 복구 명령어

```bash
# 1. 즉시 재시작
eb restart

# 2. 이전 버전으로 롤백
eb deploy --version-label=app-37af-250703_140210732480

# 3. 환경 재구축 (최후 수단)
eb terminate
eb create production --platform "Python 3.11"

# 4. 로그 실시간 모니터링
eb logs --all --follow
```

## 🔮 예방 조치

### 모니터링 설정
- CloudWatch 알람 설정
- 헬스체크 주기 단축 (30초)
- 자동 스케일링 활성화

### 코드 품질
- 로컬 테스트 자동화
- CI/CD 파이프라인 구축
- 스테이징 환경 운영

### 인프라 강화
- 멀티 AZ 배포
- 로드밸런서 설정 최적화
- 백업 및 복구 계획

## 📞 에스컬레이션 경로

1. **자동 해결 시도** (COMPLETE_HEALTH_FIX.bat)
2. **수동 진단** (이 가이드 활용)
3. **AWS 지원 티켓** (Business+ 플랜)
4. **외부 DevOps 전문가** (긴급시)

---

✅ **성공 기준**: Health가 Green으로 변경되고 모든 엔드포인트가 200 응답
⚠️ **실패시**: AWS Support 또는 DevOps 전문가 에스컬레이션
