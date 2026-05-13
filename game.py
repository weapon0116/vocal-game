import streamlit as st
import numpy as np
import scipy.io.wavfile as wav
import io
import random

# --- [1. 기본 설정] ---
st.set_page_config(page_title="V-RAP: 주파수 챌린지", layout="centered")

# --- [2. 화이트 모드 전용 CSS 디자인] ---
st.markdown("""
    <style>
        /* 메인 배경 및 컨테이너 */
        .block-container { background-color: #FFFFFF; }
        
        /* 결과 박스 (밝은 회색 계열) */
        .report-box { 
            background-color: #F8F9FA; padding: 15px; border-radius: 15px; 
            border: 1px solid #DEE2E6; text-align: center; margin-bottom: 10px;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
        }
        
        /* 미션 타겟 디스플레이 (강렬한 레드 포인트) */
        .game-display {
            background: linear-gradient(145deg, #FFFFFF, #F1F3F5);
            padding: 30px; border-radius: 25px;
            border: 2px solid #FF4B4B; text-align: center; margin: 15px 0px;
            box-shadow: 5px 5px 15px #EDF0F2, -5px -5px 15px #FFFFFF;
        }
        
        .target-val { font-size: 4rem !important; font-weight: 900; color: #FF4B4B; margin: 10px 0; }
        .my-val { font-size: 3.5rem !important; font-weight: 800; color: #007BFF; }
        .banner { font-size: 2.8rem !important; font-weight: 900; margin-top: 15px; }
        
        /* 텍스트 색상 보정 */
        h1 { color: #212529; font-weight: 800 !important; }
        p { color: #495057; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 주파수 맞추기 게임")

# --- [3. 게임 로직] ---
if 'target_hz' not in st.session_state:
    st.session_state.target_hz = round(random.uniform(200.0, 800.0), 1)

st.markdown(f"""
    <div class='game-display'>
        <p style='font-weight: 700; color: #FF4B4B; letter-spacing: 2px;'>MISSION TARGET</p>
        <div class='target-val'>{st.session_state.target_hz} Hz</div>
    </div>
""", unsafe_allow_html=True)

if st.button("🔄 타겟 변경", use_container_width=True):
    st.session_state.target_hz = round(random.uniform(200.0, 800.0), 1)
    st.rerun()

# 화이트 모드에서는 기본 audio_input UI가 아주 깔끔하게 보입니다.
game_audio = st.audio_input("지금 바로 소리내보세요!", key="game_white_input")

if game_audio:
    try:
        audio_bytes = game_audio.read()
        sr, y = wav.read(io.BytesIO(audio_bytes))
        if len(y.shape) > 1: y = y[:, 0]
        
        y = y[:int(sr * 0.5)].astype(float)
        y -= np.mean(y) 
        
        # 자기상관 함수로 주파수 검출
        corr = np.correlate(y, y, mode='full')[len(y)-1:]
        d = np.diff(corr)
        start_indices = np.where(d > 0)[0]
        start = start_indices[0] if len(start_indices) > 0 else 0
        peak = np.argmax(corr[start:]) + start
        
        if peak > 0:
            raw_f0 = sr / peak
            
            # 🔥 [파워 가변 보정 로직 유지]
            if raw_f0 < 150:
                weight = 1.8
            elif raw_f0 < 250:
                weight = 2.4
            else:
                weight = 3.0
            
            avg_f0 = raw_f0 * weight
            
            # 최종 판정 및 출력
            if 10 <= avg_f0 <= 1500:
                diff = abs(avg_f0 - st.session_state.target_hz)
                
                # 나의 결과 출력 박스
                st.markdown(f"""
                    <div class='report-box'>
                        <small style='color:#6C757D;'>나의 기록</small>
                        <div class='my-val'>{avg_f0:.1f} Hz</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if diff <= 40:
                    st.balloons()
                    st.markdown("<div style='text-align:center; color:#28A745;' class='banner'>🎉 PERFECT!</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:center; color:#FFC107;' class='banner'>오차: {diff:.1f} Hz</div>", unsafe_allow_html=True)
            else:
                st.warning("목소리 주파수가 범위를 벗어났습니다.")
        else:
            st.warning("소리가 너무 작습니다.")
            
    except Exception as e:
        st.error("처리 중 오류가 발생했습니다. 다시 시도해 주세요.")
