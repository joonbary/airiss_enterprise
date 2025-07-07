# 🚀 AIRISS GitHub 업로드 가이드

## 1단계: GitHub Repository 준비
1. https://github.com/joonbary/airiss_enterprise 접속
2. Repository가 비어있는지 확인

## 2단계: 로컬 Git 설정 확인
```bash
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
git status
git remote -v
```

## 3단계: 파일 정리 및 추가
```bash
# 중요 파일들을 staging area에 추가
git add README.md
git add requirements.txt
git add app/
git add static/
git add templates/
git add *.py
git add .gitignore
git add docs/
git add scripts/

# 민감한 파일 제외 확인
git status
```

## 4단계: 초기 커밋
```bash
git commit -m "🎉 Initial commit: AIRISS v4.1 Enhanced - AI-powered Resource Intelligence Scoring System

✨ Features:
- 8차원 하이브리드 AI 분석 (텍스트 60% + 정량 40%)
- 실시간 편향 탐지 및 공정성 모니터링
- Chart.js 기반 고급 시각화 대시보드
- WebSocket 실시간 분석 진행률 추적
- SQLite 기반 경량 데이터베이스
- FastAPI + uvicorn 고성능 백엔드

🏆 Impact:
- OK금융그룹 1,800명 대상 실무 검증
- HR 의사결정 시간 50% 단축
- 평가 객관성 40% 향상
- B2B 시장 진출 잠재력 확보

🛠 Tech Stack:
- Backend: FastAPI, Python 3.9+
- Frontend: HTML5, Chart.js, WebSocket
- Database: SQLite
- AI/ML: NLP, 편향 탐지, 통계 분석"
```

## 5단계: GitHub Remote 설정 및 Push
```bash
# Remote repository 설정 (이미 설정되어 있다면 스킵)
git remote add origin https://github.com/joonbary/airiss_enterprise.git

# 또는 기존 origin 확인/변경
git remote set-url origin https://github.com/joonbary/airiss_enterprise.git

# Push to GitHub
git push -u origin main
```

## 6단계: GitHub에서 확인
1. https://github.com/joonbary/airiss_enterprise 접속
2. 파일 업로드 확인
3. README.md 내용 확인

## 추가 설정 (선택사항)

### GitHub Actions 설정
```yaml
# .github/workflows/ci.yml
name: AIRISS CI/CD
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest tests/
```

### GitHub Pages 설정 (문서화)
1. Repository Settings > Pages
2. Source: Deploy from a branch
3. Branch: main / docs

## 🔐 보안 주의사항
- `.env` 파일은 절대 업로드하지 않기
- API 키, 비밀번호 등 민감정보 제외
- `.gitignore`로 민감 파일 보호

## 📞 문제 해결
문제 발생 시:
1. `git status`로 현재 상태 확인
2. `git log --oneline`으로 커밋 히스토리 확인
3. GitHub Desktop 사용 고려 (GUI 방식)
