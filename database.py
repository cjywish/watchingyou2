import sqlite3
import pandas as pd
from datetime import datetime

# 데이터베이스 연결 및 테이블 초기화
def init_db():
    conn = sqlite3.connect('hbm_factory.db')
    cursor = conn.cursor()
    # 테이블 생성 (기존에 없으면 생성)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temp REAL,
            pressure REAL,
            analysis_text TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 검사 결과 저장 함수
def save_inspection(telemetry, analysis_text, status):
    conn = sqlite3.connect('hbm_factory.db')
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO inspections (timestamp, temp, pressure, analysis_text, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (now, telemetry['temp'], telemetry['pressure'], analysis_text, status))
    
    conn.commit()
    conn.close()

# 전체 검사 이력 조회 함수 (Pandas DataFrame 반환)
def get_all_inspections():
    conn = sqlite3.connect('hbm_factory.db')
    query = "SELECT * FROM inspections ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
