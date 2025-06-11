import pandas as pd
import chardet
import os

print("📊 AIRISS 데이터 인코딩 변환 시작")
print("=" * 50)

# 현재 파일 확인
if os.path.exists('AIRISS_Assessment_rawdata.csv'):
    print("✅ 원본 파일 발견")
    
    # 인코딩 감지
    with open('AIRISS_Assessment_rawdata.csv', 'rb') as f:
        raw_data = f.read(10000)  # 처음 10KB만 읽어서 감지
        result = chardet.detect(raw_data)
        print(f"🔍 감지된 인코딩: {result['encoding']} (신뢰도: {result['confidence']:.2%})")
    
    # 다양한 인코딩으로 시도
    encodings = ['cp949', 'euc-kr', 'iso-8859-1', 'utf-8', 'utf-16']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv('AIRISS_Assessment_rawdata.csv', encoding=encoding)
            print(f"✅ {encoding} 인코딩 성공!")
            print(f"📊 총 데이터: {len(df)}개")
            print(f"📑 컬럼: {list(df.columns)}")
            break
        except Exception as e:
            print(f"❌ {encoding} 실패: {str(e)[:50]}...")
            continue
    
    if df is not None:
        # UTF-8로 재저장
        df.to_csv('AIRISS_fixed.csv', index=False, encoding='utf-8-sig')
        print("✅ AIRISS_fixed.csv 생성 완료 (UTF-8)")
        
        # 100개 테스트용 생성
        df_100 = df.head(100)
        df_100.to_csv('test_100_fixed.csv', index=False, encoding='utf-8-sig')
        print("✅ test_100_fixed.csv 생성 완료")
        
        # 데이터 미리보기
        print("\n📋 데이터 미리보기:")
        print("-" * 40)
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            uid = row.iloc[0]
            opinion = str(row.iloc[1])
            opinion_preview = opinion[:100] + "..." if len(opinion) > 100 else opinion
            print(f"ID {uid}: {opinion_preview}")
        
        print(f"\n🎯 다음 단계:")
        print(f"1. test_100_fixed.csv를 웹에 업로드")
        print(f"2. AI 분석 시작 (예상 비용: $0.09)")
        print(f"3. 품질 검증 후 전체 {len(df)}개 진행")
        
    else:
        print("❌ 모든 인코딩 시도 실패")
        print("📁 파일을 Excel로 열어서 다시 CSV로 저장해보세요")
        
else:
    print("❌ AIRISS_Assessment_rawdata.csv 파일이 없습니다")
    print("📁 현재 폴더의 파일 목록:")
    for file in os.listdir('.'):
        if file.endswith('.csv'):
            print(f"   📄 {file}")