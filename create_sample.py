import pandas as pd

print('📊 원본 파일 읽는 중...')
df = pd.read_csv('assessment_data_text_UTF8.csv')
print(f'✅ 총 {len(df)}개 행 발견')

print('🔄 처음 10개 추출 중...')
df_sample = df.head(10)
df_sample.to_csv('test_10.csv', index=False, encoding='utf-8-sig')

print('✅ test_10.csv 파일 생성 완료!')
print('📋 샘플 데이터 미리보기:')
for i, row in df_sample.iterrows():
    opinion = str(row['의견'])[:50] + '...' if len(str(row['의견'])) > 50 else str(row['의견'])
    print(f'{i+1}. {opinion}')