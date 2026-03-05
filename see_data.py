import sqlite3
import random
from datetime import datetime, timedelta

def seed_hbm_data(db_path='hbm_factory.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 1. 기존 데이터 삭제 (초기화)
    c.execute("DELETE FROM logs")
    
    # 2. 시나리오 데이터 정의
    scenarios = [
        {
            "status": "정상",
            "defect_choice": "Normal",
            "temp_range": (255, 265),
            "press_range": (110, 130),
            "analysis": "<defect_status>: [정상]\n<reasoning>: 범프 정렬 상태 양호 및 TSV 단면 균일함. 공정 파라미터가 가이드라인 내에 있음."
        },
        {
            "status": "주의",
            "defect_choice": "TSV Void",
            "temp_range": (268, 275),
            "press_range": (100, 115),
            "analysis": "<defect_status>: [주의]\n<reasoning>: 고온 공정으로 인해 TSV 내부 미세 기포 발생 가능성 포착. 전기적 특성 전수 검사 권고."
        },
        {
            "status": "불량",
            "defect_choice": "Microbump Bridge",
            "temp_range": (250, 260),
            "press_range": (155, 180),
            "analysis": "<defect_status>: [불량]\n<reasoning>: 과도한 본딩 압력(150N 초과)으로 인해 인접 범프 간 솔더 브릿지 형성됨. 즉시 장비 정지 필요."
        }
    ]

    # 3. 20개의 가상 데이터 생성
    print(f"[{datetime.now()}] 초기 데이터 적재 시작...")
    
    for i in range(20):
        # 시나리오 랜덤 선택 (정상 60%, 주의 20%, 불량 20% 비중)
        scenario = random.choices(scenarios, weights=[60, 20, 20])[0]
        
        timestamp = (datetime.now() - timedelta(hours=random.randint(1, 100))).strftime("%Y-%m-%d %H:%M:%S")
        temp = round(random.uniform(*scenario["temp_range"]), 1)
        pressure = round(random.uniform(*scenario["press_range"]), 1)
        
        c.execute("""INSERT INTO logs (timestamp, status, user_label, temp, pressure, analysis, is_corrected) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (timestamp, scenario["status"], scenario["status"], temp, pressure, scenario["analysis"], 0))

    conn.commit()
    conn.close()
    print(f"✅ 적재 완료: 20건의 검사 이력이 '{db_path}'에 저장되었습니다.")

if __name__ == "__main__":
    seed_hbm_data()