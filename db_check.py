import sqlite3

conn = sqlite3.connect('airiss.db')
cursor = conn.cursor()

print("=== files 테이블 구조 확인 ===")
cursor.execute("PRAGMA table_info(files)")
files_columns = cursor.fetchall()
print("files 컬럼들:", files_columns)

print("\n=== jobs 테이블 구조 확인 ===")
cursor.execute("PRAGMA table_info(jobs)")
jobs_columns = cursor.fetchall()
print("jobs 컬럼들:", jobs_columns)

print("\n=== results 테이블 구조 확인 ===")
cursor.execute("PRAGMA table_info(results)")
results_columns = cursor.fetchall()
print("results 컬럼들:", results_columns)

print("\n=== files 테이블 데이터 확인 ===")
cursor.execute("SELECT * FROM files LIMIT 3")
files_data = cursor.fetchall()
print("files 데이터:", files_data)

conn.close()