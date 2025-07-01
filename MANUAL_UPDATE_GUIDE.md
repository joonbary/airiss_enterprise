# 🛠️ AIRISS GitHub 수동 업데이트 방법

## ❌ 배치 파일이 안 될 때 사용하세요!

### 🥇 **방법 1: 명령 프롬프트 사용 (가장 확실함)**

1. **Win + R** 키를 누르세요
2. **`cmd`** 입력하고 **엔터**
3. 다음 명령어들을 **하나씩** 복사해서 붙여넣으세요:

```cmd
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
```

```cmd
git status
```

```cmd
git add .
```

```cmd
git commit -m "Update AIRISS to v4.1 Enhanced"
```

```cmd
git push origin main
```

### 🥈 **방법 2: Git Bash 사용 (Git 설치된 경우)**

1. 파일 탐색기에서 `C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4` 폴더 열기
2. 빈 공간에서 **우클릭**
3. **"Git Bash Here"** 선택
4. 다음 명령어 입력:

```bash
git add .
git commit -m "Update AIRISS to v4.1 Enhanced"
git push origin main
```

### 🥉 **방법 3: Visual Studio Code 사용**

1. **VS Code** 열기
2. **Ctrl + K, Ctrl + O** 누르고 프로젝트 폴더 선택
3. **Source Control** 탭 (Ctrl + Shift + G)
4. **"+"** 버튼으로 모든 변경사항 스테이징
5. 커밋 메시지 입력: "Update AIRISS to v4.1 Enhanced"
6. **"Commit"** 클릭
7. **"Push"** 클릭

---

## 🔍 **문제 진단**

### **배치 파일이 꺼지는 이유들:**

1. **Python 경로 문제**
   - Python이 환경변수 PATH에 없음
   - 해결: 아래 Python 재설정 방법 사용

2. **권한 문제**
   - 관리자 권한 필요
   - 해결: 배치 파일 우클릭 → "관리자로 실행"

3. **파일 경로 문제**
   - 프로젝트 폴더 경로가 다름
   - 해결: 실제 폴더 경로 확인

### **Python 경로 확인 방법:**

1. **Win + R** → `cmd` → 엔터
2. `python --version` 입력
3. 오류가 나면 Python 재설치 필요

---

## ✅ **성공 확인 방법**

1. **GitHub 페이지 접속**: https://github.com/joonbary/airiss_enterprise
2. **최신 커밋 시간** 확인 (방금 시간이어야 함)
3. **README 내용** 확인 (v4.1 내용이 있어야 함)

---

## 🆘 **여전히 안 되면**

다음 정보를 확인해주세요:

1. **Python 설치 여부**:
   ```cmd
   python --version
   ```

2. **Git 설치 여부**:
   ```cmd
   git --version
   ```

3. **현재 위치**:
   ```cmd
   dir
   ```

4. **Git 상태**:
   ```cmd
   git status
   ```

이 정보들을 알려주시면 더 정확한 해결책을 제공할 수 있습니다!
