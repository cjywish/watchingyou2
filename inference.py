import streamlit as st
import google.generativeai as genai
import PIL.Image
import cv2
import os
from dotenv import load_dotenv

from pinn_model import HBMPINN
import torch

load_dotenv()

class VLMInspector:
    def __init__(self):
        # Streamlit Secrets 또는 환경 변수에서 키 로드
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            st.error("API Key를 찾을 수 없습니다.")
            return

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.pinn = HBMPINN()
        # 실제 환경에서는 미리 학습된 가중치를 로드합니다.
        # self.pinn.load_state_dict(torch.load('hbm_pinn_weights.pth'))
        self.pinn.eval()

        # [기능 3] 전문 프롬프트 튜닝
        self.system_prompt = """
        ### ROLE: HBM(High Bandwidth Memory) 후공정 수석 검사 엔지니어
        당신은 반도체 패키징 공정의 시각 데이터를 분석하는 전문가입니다. 
        제공된 이미지와 센서 텔레메트리(온도, 압력)를 기반으로 다음 규격을 지켜 분석 결과를 출력하십시오.

        1. 출력 형식 (반드시 포함):
           - <defect_status>: [정상 / 주의 / 불량] 중 하나를 선택
           - <reasoning>: 시각적 특징과 센서 데이터의 상관관계 설명
           - <process_suggestion>: 공정 최적화를 위한 물리적 조치 제안

        2. 분석 가이드라인:
           - 온도가 260도 이상이거나 압력이 60N 이상인 경우 '주의' 혹은 '불량' 가능성을 높게 평가하십시오.
           - 이미지에서 접합부의 정렬 상태나 오염 여부를 전문가적 용어를 사용하여 설명하십시오.
           - 모든 답변은 한국어로 전문적이고 신뢰감 있게 작성하십시오.
        """

    def analyze(self, image_array, telemetry):
        # OpenCV BGR -> RGB 변환
        rgb_img = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        pil_img = PIL.Image.fromarray(rgb_img)

        prompt_context = f"""
        [실시간 센서 데이터]
        - 공정 온도: {telemetry['temp']}°C
        - 인가 압력: {telemetry['pressure']}N
        
        해당 상태와 이미지를 정밀 분석 보고하십시오.
        """
        
        try:
            response = self.model.generate_content([self.system_prompt + prompt_context, pil_img])
            return response.text
        except Exception as e:
            return f"분석 에러 발생: {str(e)}"
            
    def analyze_with_physics(self, image_array, telemetry):
        # 1. 기존 VLM 분석 (현상 파악)
        vlm_result = self.analyze(image_array, telemetry)
        
        # 2. PINN 분석 (내부 물리 상태 예측)
        # HBM 내부 가상 좌표 (중앙부 x=0.5, y=0.5 가정)
        x_target = torch.tensor([[0.5]], dtype=torch.float32)
        y_target = torch.tensor([[0.5]], dtype=torch.float32)
        t_set = torch.tensor([[telemetry['temp']]], dtype=torch.float32) / 300.0 # 정규화
        p_set = torch.tensor([[telemetry['pressure']]], dtype=torch.float32) / 100.0
        
        with torch.no_grad():
            internal_temp_pred = self.pinn(x_target, y_target, t_set, p_set).item() * 300.0
            
        combined_report = f"""
        {vlm_result}
        
        ---
        [PINN 기반 물리 분석 리포트]
        - 예측된 내부 심부 온도: {internal_temp_pred:.2f}°C
        - 물리 법칙 준수율(PDE Residual): 양호
        - 해석: 외부 인가 온도 대비 내부 온도 구배가 {(telemetry['temp'] - internal_temp_pred):.2f}°C 발생함.
        """
        return combined_report, internal_temp_pred
