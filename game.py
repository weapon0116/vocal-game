import streamlit as st
import numpy as np
import scipy.io.wavfile as wav
import io
import random

# --- [1. 기본 설정] ---
st.set_page_config(page_title="V-RAP: 주파수 챌린지", layout="centered")

# --- [2. CSS 디자인 (보내주신 스타일 유지)] ---
st.markdown("""
    <style>
        .report-box { 
            background-color: #1E1E1E; padding: 15px; border-radius: 12px; 
            border: 1px solid #444; text-align: center; margin-bottom: 10px;
        }
        .game-display {
            background: linear-gradient(145deg, #121212, #252525);
            padding: 20px; border-radius: 20px;
            border: 2px solid #FF4B4B; text-align: center; margin: 10px 0px;
        }
        .target-val { font-size: 3.5rem !important; font-weight: 900; color: #FF4B4B; }
        .my-val { font-size: 3rem !important; font-weight: 800; color: #00BFFF; }
        .banner { font-size: 2.5rem !important; font-weight: 900; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 주파수 맞추기 게임")

# --- [3. 게임 로직] ---
if 'target_hz' not in st.session_state:
    st.session_state.target_hz = round(random.uniform(160.0, 300.0), 1)

st.markdown(f"""
    <div class='game-display'>
        <p style='color:#888; margin-bottom:0;'>MISSION TARGET</p>
        <div class='target-val'>{st.session_state.target_hz} Hz</div>
    </div>
""", unsafe_allow_html=True)

if st.button("🔄 주파수 변경", use_container_width=True):
    st.session_state.target_hz = round(random.uniform(160.0, 300.0), 1)
    st.rerun()

game_audio = st.audio_input("지금 바로 소리내고 체크하세요!", key="game_input")

if game_audio:
    try:
        # [초고속 로드] 메모리에서 직접 읽기
        audio_bytes = game_audio.read()
        sr, y = wav.read(io.BytesIO(audio_bytes))
        
        if len(y.shape) > 1: y = y[:, 0]
        
        # [초고속 분석] 0.5초만 사용하여 연산량 최소화
        y = y[:int(sr * 0.5)].astype(float)
        y -= np.mean(y) 
        
        corr = np.correlate(y, y, mode='full')[len(y)-1:]
        d = np.diff(corr)
        start = np.where(d > 0)[0][0] if len(np.where(d > 0)[0]) > 0 else 0
        peak = np.argmax(corr[start:]) + start
        
        if peak > 0:
            avg_f0 = sr / peak
            if 80 < avg_f0 < 500:
                diff = abs(avg_f0 - st.session_state.target_hz)
                st.markdown(f"<div class='report-box'><small>나의 기록</small><div class='my-val'>{avg_f0:.1f} Hz</div></div>", unsafe_allow_html=True)
                
                if diff <= 20:
                    st.balloons()
                    st.markdown("<div style='text-align:center; color:#00FF88;' class='banner'>🎉 SUCCESS!</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:center; color:#FFD700;' class='banner'>오차: {diff:.1f} Hz</div>", unsafe_allow_html=True)
            else:
                st.warning("목소리가 범위를 벗어났습니다. 다시 시도해 주세요!")
        else:
            st.warning("소리가 너무 작습니다.")
            
    except Exception:
        st.error("처리 중 렉이 발생했습니다. 다시 시도해 주세요.")
