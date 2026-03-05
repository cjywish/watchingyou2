import streamlit as st
import pandas as pd
import cv2
import io
from datetime import datetime
from generator import generate_hbm_sample
from inference import VLMInspector
from database import init_db, save_inspection, get_all_inspections
from hbm_utils import extract_status

# github 연동 테스트

# 페이지 설정
st.set_page_config(page_title="HBM VLM AI Inspector", layout="wide")

# 데이터베이스 초기화 및 모델 로드
init_db()
@st.cache_resource
def load_inspector():
    return VLMInspector()

inspector = load_inspector()

# 세션 상태 초기화 (이미지 및 데이터 유지용)
if 'sample_img' not in st.session_state:
    st.session_state.sample_img = None
if 'telemetry' not in st.session_state:
    st.session_state.telemetry = None

# --- 사이드바: 공정 제어 및 대시보드 요약 ---
st.sidebar.title("🏭 HBM Control Center")

if st.sidebar.button("Generate New HBM Sample"):
    img, tele = generate_hbm_sample()
    st.session_state.sample_img = img
    st.session_state.telemetry = tele
    st.sidebar.success("새 공정 샘플 생성 완료")

# --- 메인 화면 구성 ---
st.title("🛡️ HBM Intelligent VLM Inspection System")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Real-time Process Image")
    if st.session_state.sample_img is not None:
        st.image(st.session_state.sample_img, channels="BGR", use_container_width=True)
        st.info(f"🌡️ Temperature: {st.session_state.telemetry['temp']}°C | ⚖️ Pressure: {st.session_state.telemetry['pressure']}N")
    else:
        st.warning("먼저 샘플 생성 버튼을 눌러주세요.")

with col2:
    st.subheader("🧠 AI VLM & PINN Analysis")
    if st.button("Run Hybrid Analysis", type="primary"):
        if st.session_state.sample_img is not None:
            with st.spinner("VLM과 PINN이 협력하여 분석 중입니다..."):
                # 수정된 통합 분석 함수 호출
                full_report, internal_temp = inspector.analyze_with_physics(
                    st.session_state.sample_img, st.session_state.telemetry
                )
                status = extract_status(full_report)
                
                # UI 출력
                st.metric("PINN 예측 내부 온도", f"{internal_temp:.1f} °C")
                st.write(full_report)
                
                # [기능 1] 실시간 알림 (Alert & Toast)
                if "불량" in status:
                    st.error(f"🚨 공정 이상 감지: {status} 판정!")
                    st.toast("🔥 긴급: 불량 데이터 감지됨!", icon="🔥")
                elif "주의" in status:
                    st.warning(f"⚠️ 모니터링 필요: {status} 판정")
                    st.toast("⚠️ 공정 드리프트 주의", icon="⚠️")
                else:
                    st.success("✅ 공정 정상 상태입니다.")
                    st.toast("✅ 정상 판정 완료", icon="✅")

                # 분석 결과 출력
                st.markdown(f"**[AI 판정 결과]**")
                st.write(full_report)
                
                # DB 저장
                #save_inspection(st.session_state.telemetry, analysis_result, status)
                save_inspection(st.session_state.telemetry, full_report, status)
        else:
            st.error("분석할 이미지가 없습니다.")

st.markdown("---")

# --- 하단부: 검사 이력 및 엑셀 다운로드 ---
st.subheader("📊 Inspection History & Reports")

# DB에서 데이터 불러오기
history_df = get_all_inspections()

if not history_df.empty:
    # 데이터 시각화 간단 요약
    c1, c2, c3 = st.columns(3)
    c1.metric("총 검사 수", len(history_df))
    c2.metric("불량 건수", len(history_df[history_df['status'] == '불량']))
    c3.metric("정상 건수", len(history_df[history_df['status'] == '정상']))

    # 데이터 테이블 표시
    st.dataframe(history_df.sort_values(by='timestamp', ascending=False), use_container_width=True)

    # [기능 2] 엑셀 다운로드 버튼
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        history_df.to_excel(writer, index=False, sheet_name='HBM_Inspection_Log')
    
    st.download_button(
        label="📥 전체 검사 리포트 엑셀 다운로드",
        data=buffer.getvalue(),
        file_name=f"HBM_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.ms-excel"
    )
else:
    st.info("아직 저장된 검사 이력이 없습니다.")
