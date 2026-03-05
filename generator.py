import cv2
import numpy as np
import random

def generate_hbm_sample():
    # 1. 가상의 HBM 단면 이미지 생성 (640x480)
    img = np.full((480, 640, 3), 40, dtype=np.uint8) # 어두운 배경
    
    # 센서 데이터 시뮬레이션
    # 정상 범위: Temp 230~250, Pressure 40~55
    temp = round(random.uniform(220, 270), 1)
    pressure = round(random.uniform(35, 65), 1)
    
    status = "정상"
    if temp > 260 or pressure > 60:
        status = "불량"
        color = (0, 0, 255) # Red (불량일 때 이미지에 붉은 점 생성)
    else:
        color = (200, 200, 200) # Gray
        
    # 가상의 반도체 칩 범프(Bump) 패턴 그리기
    for i in range(100, 500, 60):
        for j in range(100, 400, 60):
            cv2.circle(img, (i, j), 15, color, -1)
            
    # 노이즈 추가
    noise = np.random.normal(0, 5, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)
    
    telemetry = {
        "temp": temp,
        "pressure": pressure,
        "true_status": status
    }
    
    return img, telemetry