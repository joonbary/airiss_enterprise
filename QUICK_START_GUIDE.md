# 🚀 AIRISS v4.0 단계별 실행 가이드

## 현재 상황 해결 방법

### ✅ 즉시 실행 방법

#### 방법 1: PowerShell에서 올바른 실행
```powershell
# PowerShell에서 실행 (현재 위치에서)
.\start_dev_integrated.bat
```

#### 방법 2: PowerShell 스크립트 실행
```powershell
# PowerShell 실행 정책 설정 (처음 한 번만)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# PowerShell 스크립트 실행
.\start_dev_integrated.ps1
```

#### 방법 3: 명령 프롬프트에서 실행
```cmd
# Win + R → cmd 입력 → 엔터
# 프로젝트 디렉토리로 이동 후
start_dev_integrated.bat
```

#### 방법 4: 단계별 수동 실행 (가장 확실한 방법)

### 🔧 단계별 수동 실행

#### 1단계: 백엔드 서버 시작
```powershell
# 첫 번째 PowerShell 창에서
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

#### 2단계: React 개발 서버 시작
```powershell
# 두 번째 PowerShell 창에서
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\airiss-v4-frontend

# npm 설치 (처음 한 번만)
npm install

# React 개발 서버 시작
npm start
```

#### 3단계: 브라우저에서 확인
- 🌐 React 앱: http://localhost:3000
- 🔧 백엔드 API: http://localhost:8002
- 📖 API 문서: http://localhost:8002/docs
- 📊 개발 대시보드: http://localhost:8002/dashboard

### 🧪 시스템 테스트
```powershell
# 세 번째 PowerShell 창에서 (선택사항)
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
python test_integration.py
```

## 🔍 문제 해결

### PowerShell 실행 정책 오류 시
```powershell
# 현재 실행 정책 확인
Get-ExecutionPolicy

# 실행 정책 변경 (관리자 권한 필요할 수 있음)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 포트 충돌 오류 시
```powershell
# 포트 사용 확인
netstat -ano | findstr :8002
netstat -ano | findstr :3000

# 프로세스 종료
taskkill /PID [PID번호] /F
```

### Python 모듈 오류 시
```powershell
# 가상환경 활성화 (있는 경우)
.\venv\Scripts\Activate.ps1

# 패키지 설치
pip install -r requirements.txt
```

### Node.js 오류 시
```powershell
# Node.js 버전 확인
node --version
npm --version

# 캐시 정리
npm cache clean --force

# 의존성 재설치
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
npm install
```

## ✅ 성공 확인 방법

### 1. 백엔드 서버 확인
- PowerShell에서 "Application startup complete" 메시지 확인
- http://localhost:8002/health 접속하여 JSON 응답 확인

### 2. React 앱 확인  
- PowerShell에서 "webpack compiled with 0 errors" 메시지 확인
- http://localhost:3000 접속하여 AIRISS 앱 화면 확인

### 3. WebSocket 연결 확인
- React 앱에서 실시간 연결 상태 확인
- 개발자 도구(F12) → Console에서 WebSocket 연결 로그 확인

## 🎯 다음 단계

### 시스템이 정상 작동하면:
1. **테스트 데이터 업로드**: Excel/CSV 파일로 분석 테스트
2. **실시간 기능 확인**: 분석 진행률 실시간 업데이트 확인  
3. **결과 다운로드**: 분석 완료 후 결과 파일 다운로드
4. **WebSocket 테스트**: 실시간 알림 및 진행률 확인

### 문제가 지속되면:
1. **로그 확인**: PowerShell 창의 오류 메시지 확인
2. **브라우저 개발자 도구**: F12 → Console 탭에서 JavaScript 오류 확인
3. **방화벽/백신**: Windows Defender 또는 백신 프로그램의 차단 여부 확인
4. **관리자 권한**: PowerShell을 관리자 권한으로 실행 시도

---

**💡 팁: 가장 확실한 방법은 "단계별 수동 실행"입니다!**
