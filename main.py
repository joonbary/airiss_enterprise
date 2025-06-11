import pandas as pd
import openai
import time
import json
from datetime import datetime
import os
import re

# OpenAI API 설정
openai.api_key = "***REMOVED***"  # 실제 API 키로 교체

def analyze_and_regenerate_feedback():
    """
    AIRISS 잘린 피드백 문제 완전 해결
    - 원인 분석: API 응답 길이 제한, 프롬프트 최적화 부족
    - 해결책: 충분한 토큰, 최적화된 프롬프트, 완전성 검증
    """
    
    print("🚀 AIRISS 완전한 피드백 재생성 시작")
    print("=" * 60)
    
    # 1. 기존 데이터 로드 및 분석
    try:
        df = pd.read_excel('AIRISS_분석결과_aaef5f17_20250529_171458.xlsx')
        print(f"✅ 기존 데이터 로드: {len(df)}개")
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        return
    
    # 2. 잘린 피드백 정밀 분석
    def is_feedback_truncated(feedback_text):
        """피드백 잘림 여부 정밀 판단"""
        if not feedback_text or pd.isna(feedback_text):
            return True
            
        text = str(feedback_text).strip()
        
        # 잘림 판정 기준 (여러 조건)
        truncation_indicators = [
            len(text) < 300,  # 너무 짧음
            not text.endswith(('.', '!', '?', '다', '요', '니다', '습니다')),  # 문장이 끝나지 않음
            text.endswith(('하고', '및', '을', '를', '이', '가', '에', '의', '로', '으로')),  # 조사로 끝남
            '...' in text[-10:],  # 말줄임표
            len(text.split()) < 30,  # 너무 적은 단어 수
        ]
        
        return any(truncation_indicators)
    
    # 3. 잘린 데이터 식별
    df['is_truncated'] = df['AI_피드백'].apply(is_feedback_truncated)
    truncated_rows = df[df['is_truncated']].copy()
    
    print(f"🔍 분석 결과:")
    print(f"   전체 데이터: {len(df)}개")
    print(f"   잘린 피드백: {len(truncated_rows)}개 ({len(truncated_rows)/len(df)*100:.1f}%)")
    print(f"   완전한 피드백: {len(df) - len(truncated_rows)}개")
    
    # 4. 개선된 프롬프트 템플릿
    def create_optimized_prompt(opinion_text, uid):
        """최적화된 프롬프트 생성 - 완전한 응답 보장"""
        return f"""
다음 직원 평가 의견을 종합적으로 분석하여 완전하고 구체적인 피드백을 작성해주세요.

【직원 ID】: {uid}
【평가 의견】: {opinion_text[:2000]}

【요구사항】:
1. 반드시 완전한 문장으로 끝내기
2. 총 500-800자 분량으로 작성
3. 다음 구조를 반드시 포함:
   - 장점 강화 방안 (2-3개)
   - 개선 필요 영역 (2-3개)  
   - 구체적 실행 계획 (3-5개)
   - 향후 발전 방향 제시

【작성 형식】:
✅ 장점 강화 방안:
1. [구체적 방안]
2. [구체적 방안]

🔧 개선 필요 영역:
1. [구체적 개선점]
2. [구체적 개선점]

🎯 실행 계획:
1. [즉시 실행 가능한 방안]
2. [단기 목표 (1-3개월)]
3. [중기 목표 (6개월)]

💡 발전 방향:
[미래 성장 가능성과 구체적 방향]

**중요: 반드시 마지막 문장을 완전히 끝내고, 최소 500자 이상 작성하세요.**
"""

    # 5. API 호출 함수 (최적화)
    def generate_complete_feedback(opinion, uid, max_retries=3):
        """완전한 피드백 생성 - 재시도 및 검증 포함"""
        
        for attempt in range(max_retries):
            try:
                print(f"   🤖 UID {uid} 분석 시도 {attempt + 1}/{max_retries}")
                
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",  # 최신 모델 사용
                    messages=[
                        {"role": "system", "content": "당신은 전문적인 HR 분석가입니다. 항상 완전하고 구체적인 피드백을 제공합니다."},
                        {"role": "user", "content": create_optimized_prompt(opinion, uid)}
                    ],
                    max_tokens=1500,  # 충분한 토큰 할당
                    temperature=0.7,
                    top_p=0.9,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                
                feedback = response.choices[0].message.content.strip()
                
                # 응답 품질 검증
                if len(feedback) >= 400 and feedback.endswith(('.', '다', '요', '니다', '습니다')):
                    print(f"   ✅ 성공: {len(feedback)}자 생성")
                    return feedback
                else:
                    print(f"   ⚠️ 품질 미달: {len(feedback)}자, 재시도...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"   ❌ API 오류: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # 오류 시 대기
                    
        print(f"   🔴 실패: UID {uid}")
        return None
    
    # 6. 배치 처리 실행
    print(f"\n🔄 {len(truncated_rows)}개 피드백 재생성 시작")
    print(f"⏱️ 예상 시간: {len(truncated_rows) * 3 / 60:.1f}분")
    print(f"💰 예상 비용: ${len(truncated_rows) * 0.003:.3f}")
    
    results = []
    start_time = time.time()
    
    for idx, row in truncated_rows.iterrows():
        uid = row['UID']
        opinion = row['의견']
        
        print(f"\n[{len(results)+1}/{len(truncated_rows)}] UID: {uid}")
        
        # 완전한 피드백 생성
        new_feedback = generate_complete_feedback(opinion, uid)
        
        if new_feedback:
            results.append({
                'UID': uid,
                'original_feedback': row['AI_피드백'],
                'new_feedback': new_feedback,
                'original_length': len(str(row['AI_피드백'])) if pd.notna(row['AI_피드백']) else 0,
                'new_length': len(new_feedback),
                'improvement': len(new_feedback) - (len(str(row['AI_피드백'])) if pd.notna(row['AI_피드백']) else 0)
            })
        
        # API 제한 준수
        time.sleep(2)
        
        # 진행상황 출력
        if (len(results)) % 10 == 0:
            elapsed = time.time() - start_time
            remaining = (len(truncated_rows) - len(results)) * (elapsed / len(results))
            print(f"📊 진행률: {len(results)}/{len(truncated_rows)} ({len(results)/len(truncated_rows)*100:.1f}%)")
            print(f"⏱️ 남은 시간: {remaining/60:.1f}분")
    
    # 7. 결과 분석 및 업데이트
    print(f"\n📊 재생성 완료!")
    print(f"   성공: {len(results)}개")
    print(f"   실패: {len(truncated_rows) - len(results)}개")
    
    if results:
        results_df = pd.DataFrame(results)
        print(f"   평균 길이 개선: {results_df['original_length'].mean():.0f}자 → {results_df['new_length'].mean():.0f}자")
        print(f"   총 개선량: +{results_df['improvement'].sum():,}자")
        
        # 8. 원본 데이터프레임 업데이트
        for result in results:
            mask = df['UID'] == result['UID']
            df.loc[mask, 'AI_피드백'] = result['new_feedback']
            df.loc[mask, '분석_시간'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 9. 새 파일 저장 (여러 형식)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Excel 저장
        excel_filename = f'AIRISS_완전판_{timestamp}.xlsx'
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        print(f"✅ Excel 저장: {excel_filename}")
        
        # CSV 저장 (백업)
        csv_filename = f'AIRISS_완전판_{timestamp}.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"✅ CSV 저장: {csv_filename}")
        
        # 개선 리포트 저장
        report_filename = f'AIRISS_개선리포트_{timestamp}.json'
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_processed': len(results),
                    'success_rate': len(results) / len(truncated_rows) * 100,
                    'avg_original_length': results_df['original_length'].mean(),
                    'avg_new_length': results_df['new_length'].mean(),
                    'total_improvement': results_df['improvement'].sum()
                },
                'details': results
            }, f, ensure_ascii=False, indent=2)
        print(f"✅ 리포트 저장: {report_filename}")
        
        # 10. 최종 품질 검증
        print(f"\n🔍 최종 품질 검증:")
        final_truncated = df['AI_피드백'].apply(is_feedback_truncated).sum()
        print(f"   남은 잘린 피드백: {final_truncated}개")
        print(f"   완전한 피드백: {len(df) - final_truncated}개 ({(len(df) - final_truncated)/len(df)*100:.1f}%)")
        
        avg_length = df['AI_피드백'].apply(lambda x: len(str(x)) if pd.notna(x) else 0).mean()
        print(f"   평균 피드백 길이: {avg_length:.0f}자")
        
        print(f"\n🎉 AIRISS 완전한 피드백 생성 완료!")
        print(f"📁 파일: {excel_filename}")
        print(f"💪 품질: {(len(df) - final_truncated)/len(df)*100:.1f}% 완전")
        
        return excel_filename
    
    else:
        print("❌ 재생성 실패")
        return None

# 실행
if __name__ == "__main__":
    print("🚀 AIRISS 피드백 완전 재생성 프로그램")
    print("⚠️ OpenAI API 키를 설정해주세요!")
    
    # API 키 확인
    if openai.api_key == "YOUR_API_KEY_HERE":
        print("❌ OpenAI API 키를 실제 키로 교체해주세요")
        print("   openai.api_key = 'sk-...'")
    else:
        result_file = analyze_and_regenerate_feedback()
        if result_file:
            print(f"\n✅ 성공! 파일: {result_file}")
        else:
            print(f"\n❌ 실패! 로그를 확인해주세요")