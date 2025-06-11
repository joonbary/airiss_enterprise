"""
AIRISS Excel 업로드 시스템
AI 기반 직원 평가 의견 분석
"""

from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import openai
import os
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
import io
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(title="AIRISS - AI 기반 평가 분석 시스템", version="1.0.0")

# 정적 파일 및 템플릿 설정
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass  # static 폴더가 비어있어도 괜찮음

templates = Jinja2Templates(directory="templates")

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 전역 변수
processing_status = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지 - 파일 업로드 인터페이스"""
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    """Excel 파일 업로드 및 분석 시작"""
    
    # 파일 확장자 검증
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Excel 또는 CSV 파일만 업로드 가능합니다")
    
    # 파일 크기 검증 (10MB 제한)
    content = await file.read()
    if len(content) > int(os.getenv("MAX_FILE_SIZE", 10485760)):
        raise HTTPException(status_code=400, detail="파일 크기가 10MB를 초과합니다")
    
    # 고유 태스크 ID 생성
    task_id = str(uuid.uuid4())[:8]
    
    # 파일 저장
    upload_path = f"uploads/{task_id}_{file.filename}"
    with open(upload_path, "wb") as f:
        f.write(content)
    
    # 처리 상태 초기화
    processing_status[task_id] = {
        "status": "processing",
        "filename": file.filename,
        "start_time": datetime.now(),
        "progress": 0,
        "total_rows": 0,
        "completed_rows": 0,
        "result_file": None
    }
    
    # 백그라운드에서 분석 시작
    asyncio.create_task(process_excel_file(task_id, upload_path))
    
    return {
        "task_id": task_id,
        "message": "파일 업로드 완료. 분석을 시작합니다.",
        "filename": file.filename
    }

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """분석 진행 상태 조회"""
    if task_id not in processing_status:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    return processing_status[task_id]

@app.get("/download/{task_id}")
async def download_result(task_id: str):
    """분석 결과 다운로드"""
    if task_id not in processing_status:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    status = processing_status[task_id]
    if status["status"] != "completed" or not status["result_file"]:
        raise HTTPException(status_code=400, detail="분석이 완료되지 않았습니다")
    
    result_path = status["result_file"]
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="결과 파일을 찾을 수 없습니다")
    
    filename = f"AIRISS_분석결과_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return FileResponse(result_path, filename=filename)

async def process_excel_file(task_id: str, file_path: str):
    """Excel 파일 분석 처리"""
    try:
        print(f"📊 {task_id}: 파일 분석 시작 - {file_path}")
        
        # 파일 읽기
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        else:
            df = pd.read_excel(file_path)
        
        processing_status[task_id]["total_rows"] = len(df)
        print(f"📋 {task_id}: 총 {len(df)}개 행 발견")
        
        # 의견 컬럼 찾기
        opinion_column = None
        for col in df.columns:
            if any(keyword in col for keyword in ['의견', 'opinion', '평가', 'feedback', '코멘트']):
                opinion_column = col
                break
        
        if not opinion_column:
            processing_status[task_id]["status"] = "error"
            processing_status[task_id]["error"] = "의견 컬럼을 찾을 수 없습니다"
            print(f"❌ {task_id}: 의견 컬럼 없음")
            return
        
        print(f"✅ {task_id}: 의견 컬럼 발견 - {opinion_column}")
        
        # 결과 컬럼 추가
        df['AI_장점'] = ''
        df['AI_단점'] = ''
        df['AI_피드백'] = ''
        df['분석_시간'] = ''
        
        # 각 행 분석
        for index, row in df.iterrows():
            opinion_text = str(row[opinion_column])
            
            print(f"🔄 {task_id}: {index+1}/{len(df)} 처리 중...")
            
            if len(opinion_text.strip()) < 10:
                df.at[index, 'AI_장점'] = '분석할 내용이 부족합니다'
                df.at[index, 'AI_단점'] = ''
                df.at[index, 'AI_피드백'] = ''
            else:
                # AI 분석 실행
                analysis_result = await analyze_opinion(opinion_text)
                
                # 결과 저장
                df.at[index, 'AI_장점'] = analysis_result.get('장점', '')
                df.at[index, 'AI_단점'] = analysis_result.get('단점', '')
                df.at[index, 'AI_피드백'] = analysis_result.get('피드백', '')
            
            df.at[index, '분석_시간'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 진행률 업데이트
            processing_status[task_id]["completed_rows"] = index + 1
            processing_status[task_id]["progress"] = int(((index + 1) / len(df)) * 100)
            
            # API 제한을 고려한 딜레이
            await asyncio.sleep(1)
        
        # 결과 파일 저장
        result_path = f"results/AIRISS_결과_{task_id}.xlsx"
        df.to_excel(result_path, index=False)
        
        # 완료 상태 업데이트
        processing_status[task_id]["status"] = "completed"
        processing_status[task_id]["result_file"] = result_path
        processing_status[task_id]["end_time"] = datetime.now()
        
        print(f"🎉 {task_id}: 분석 완료! 결과 파일: {result_path}")
        
    except Exception as e:
        processing_status[task_id]["status"] = "error"
        processing_status[task_id]["error"] = str(e)
        print(f"❌ {task_id}: 오류 발생 - {e}")

async def analyze_opinion(opinion_text: str) -> dict:
    """단일 평가 의견 AI 분석"""
    prompt = f"""
다음 직원 평가 의견을 분석해 주세요:

{opinion_text}

다음 형식으로 정확히 응답해 주세요:
장점: (핵심 강점 2-3가지를 간결하게)
단점: (개선 필요 영역 2-3가지를 간결하게)
AI 피드백: (구체적이고 실행 가능한 조언)
"""
    
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 HR 전문가입니다. 직원 평가를 객관적이고 건설적으로 분석합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=400
        )
        
        ai_text = response.choices[0].message.content.strip()
        return parse_ai_response(ai_text)
        
    except Exception as e:
        print(f"⚠️ AI 분석 오류: {e}")
        return {
            "장점": "",
            "단점": "",
            "피드백": f"분석 중 오류 발생: {str(e)}"
        }

def parse_ai_response(ai_text: str) -> dict:
    """AI 응답 파싱"""
    result = {"장점": "", "단점": "", "피드백": ""}
    
    lines = ai_text.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if '장점' in line:
            current_section = "장점"
            content = line.split(':', 1)[-1].strip()
            if content:
                result["장점"] = content
        elif '단점' in line:
            current_section = "단점"
            content = line.split(':', 1)[-1].strip()
            if content:
                result["단점"] = content
        elif '피드백' in line or '조언' in line:
            current_section = "피드백"
            content = line.split(':', 1)[-1].strip()
            if content:
                result["피드백"] = content
        elif current_section and line:
            if result[current_section]:
                result[current_section] += " " + line
            else:
                result[current_section] = line
    
    return result

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/test")
async def test_openai():
    """OpenAI 연결 테스트"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "안녕하세요! 연결 테스트입니다."}],
            max_tokens=50
        )
        return {
            "status": "success",
            "message": "OpenAI API 연결 성공",
            "response": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"OpenAI API 연결 실패: {e}"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 AIRISS 시스템 시작 중...")
    print("📡 서버 주소: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)