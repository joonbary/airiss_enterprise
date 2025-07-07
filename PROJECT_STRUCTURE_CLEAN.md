# AIRISS v4 정리된 프로젝트 구조
정리 일시: 2025-07-07 12:27:15
## 핵심 디렉토리
### app/
- analytics/
- api/
- core/
- db/
- main.py
- middleware/
- models/
- schemas/
- services/
- static/
- ... (3개 더)

### airiss-v4-frontend/
- README.md
- debug_websocket.js
- node_modules/
- package-lock.json
- package.json
- public/
- src/
- theme/
- tsconfig.json

### alembic/
- README
- env.py
- script.py.mako
- versions/

### static/
- fonts/

### docs/

### scripts/
- init_db.py

### tests/
- e2e/
- integration/
- unit/

## 핵심 파일
- ❌ main.py (없음)
- ✅ application.py
- ✅ requirements.txt
- ✅ README.md
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ .env.example

## 정리 결과
- 정리된 파일들은 `cleanup_backup/` 폴더에 보관
- 보호된 폴더들: uploads, tests, docs, static, airiss-v4-frontend, app, alembic, env, .venv, .env_folder, venv, .git, scripts, node_modules
- 권한 문제로 건너뛴 파일들은 그대로 유지
