# 🚀 AIRISS GitHub 동기화 가이드

## 📋 현재 상황
- ✅ **GitHub 리포지토리**: 정상 생성됨 (`https://github.com/joonbary/airiss_enterprise`)
- ⚠️ **버전 차이**: 로컬 v4.1 ↔ GitHub v3.0
- 🔄 **동기화 필요**: 최신 코드를 GitHub에 업로드 필요

---

## 🛠️ 해결 방법 (3가지 옵션)

### 🥇 **옵션 1: 원클릭 자동화 (권장)**

#### **Step 1: 상태 진단**
```bash
# 프로젝트 폴더에서 더블클릭
github_sync_manager.bat
```
- 메뉴에서 `1. 현재 상태 진단하기` 선택
- 진단 결과를 확인하고 문제점 파악

#### **Step 2: 안전 업데이트**
```bash
# 같은 배치 파일에서
메뉴 > 2. GitHub에 안전하게 업데이트하기
```
- 자동으로 백업 생성
- 기존 기능 100% 보존
- GitHub에 v4.1 업로드

---

### 🥈 **옵션 2: 개별 스크립트 실행**

#### **Step 1: 진단**
```bash
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
python github_sync_checker.py
```

#### **Step 2: 업데이트**
```bash
python github_sync_updater.py
```

---

### 🥉 **옵션 3: 수동 Git 명령어**

#### **고급 사용자용 (IT 전문가)**
```bash
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

# 1. 상태 확인
git status

# 2. 변경사항 스테이징
git add .

# 3. 커밋 생성
git commit -m "Update to AIRISS v4.1 Enhanced"

# 4. GitHub 업로드
git push origin main
```

---

## ✅ 성공 확인 방법

### 1. **GitHub 페이지 확인**
- 브라우저에서 `https://github.com/joonbary/airiss_enterprise` 접속
- README에 "v4.1" 표시 확인
- 최신 커밋 시간 확인

### 2. **로컬 동기화 확인**
```bash
# 프로젝트 폴더에서
git status
# "Your branch is up to date with 'origin/main'" 메시지 확인
```

### 3. **파일 수 비교**
- GitHub에서 파일 목록 확인
- 로컬과 동일한 파일들이 모두 있는지 확인

---

## 🔒 안전 장치

### **자동 백업**
- 업데이트 전 전체 프로젝트 자동 백업
- 위치: `C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4_backup_[날짜시간]`
- 문제 발생 시 백업으로 즉시 복구 가능

### **기능 보존 보장**
- ✅ 모든 기존 기능 100% 유지
- ✅ 데이터베이스 파일 보존
- ✅ 설정 파일 보존
- ✅ 사용자 데이터 보존

### **롤백 방법**
문제 발생 시:
1. 백업 폴더의 내용을 원본 폴더로 복사
2. 또는 `git reset --hard HEAD~1` 사용

---

## 🆘 문제 해결

### **문제 1: "Permission denied" 오류**
```bash
# 해결: Git 사용자 정보 설정
git config user.name "AIRISS Developer"
git config user.email "airiss@okfinancialgroup.co.kr"
```

### **문제 2: "Connection refused" 오류**
- 인터넷 연결 확인
- GitHub 접속 가능 여부 확인
- 방화벽 설정 확인

### **문제 3: "Repository not found" 오류**
```bash
# 해결: 원격 저장소 재설정
git remote set-url origin https://github.com/joonbary/airiss_enterprise.git
```

### **문제 4: 파일이 너무 큰 경우**
```bash
# .gitignore에 추가할 패턴
*.db
*.log
logs/
temp_data/
```

---

## 📊 업데이트 후 확인사항

### **필수 체크리스트**
- [ ] GitHub 페이지에서 v4.1 버전 확인
- [ ] README.md 최신 내용 확인
- [ ] 주요 파일들 업로드 확인
- [ ] 로컬과 원격 동기화 확인

### **선택 체크리스트**
- [ ] 팀원들에게 업데이트 공지
- [ ] 개발 문서 업데이트
- [ ] 다음 버전 계획 수립

---

## 🎯 추천 실행 순서

1. **🔍 먼저 진단**: `github_sync_manager.bat` → 메뉴 1
2. **📦 백업 확인**: 자동 생성되는 백업 폴더 위치 확인
3. **🚀 업데이트**: `github_sync_manager.bat` → 메뉴 2
4. **✅ 확인**: GitHub 페이지 접속하여 업데이트 확인
5. **🎉 완료**: 팀원들에게 최신 버전 공지

---

## 💡 팁

### **정기 동기화**
- 매주 금요일 오후에 변경사항 동기화 권장
- 큰 변경사항이 있을 때마다 즉시 업로드

### **협업 시 주의사항**
- 여러 명이 동시에 작업할 경우 충돌 가능
- 작업 전 항상 `git pull` 먼저 실행

### **버전 관리**
- 주요 기능 추가 시 버전 번호 업데이트
- 변경 내역을 CHANGELOG.md에 기록

---

**🎉 이제 AIRISS v4.1이 GitHub에 완벽하게 동기화됩니다!**
