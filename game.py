import streamlit as st
import numpy as np
import scipy.io.wavfile as wav
import io
import random

# --- [1. 기본 설정 및 디자인은 기존과 동일] ---
st.set_page_config(page_title="V-RAP: 주파수 챌린지", layout="centered")

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

st.title("🎯 스마트 주파수 챌린지")

# --- [2. 게임 로직] ---
if 'target_hz' not in st.session_state:
    st.session_state.target_hz = round(random.uniform(150.0, 600.0), 1)

st.markdown(f"""
    <div class='game-display'>
        <p style='color:#888; margin-bottom:0;'>MISSION TARGET</p>
        <div class='target-val'>{st.session_state.target_hz} Hz</div>
    </div>
""", unsafe_allow_html=True)

if st.button("🔄 타겟 변경", use_container_width=True):
    st.session_state.target_hz = round(random.uniform(150.0, 600.0), 1)
    st.rerun()

game_audio = st.audio_input("목소리를 내주세요!", key="game_input")

if game_audio:
    try:
        audio_bytes = game_audio.read()
        sr, y = wav.read(io.BytesIO(audio_bytes))
        if len(y.shape) > 1: y = y[:, 0]
        
        y = y[:int(sr * 0.5)].astype(float)
        y -= np.mean(y) 
        
        corr = np.correlate(y, y, mode='full')[len(y)-1:]
        d = np.diff(corr)
        start = np.where(d > 0)[0][0] if len(np.where(d > 0)[0]) > 0 else 0
        peak = np.argmax(corr[start:]) + start
        
        if peak > 0:
            raw_f0 = sr / peak
            
            # 🔥 [스마트 가변 보정 로직]
            # 낮은 음(100Hz 근처)은 약 1.3배, 높은 음(300Hz 근처)은 2.0배 이상 보정
            # 주파수가 높을수록 더 큰 가중치를 곱해줍니다.
            if raw_f0 < 150:
                weight = 1.3
            elif raw_f0 < 250:
                weight = 1.7
            else:
                weight = 2.1
            
            avg_f0 = raw_f0 * weight
            
            # 최종 판정
            if 80 < avg_f0 < 1200:
                diff = abs(avg_f0 - st.session_state.target_hz)
                st.markdown(f"<div class='report-box'><small>스마트 분석 결과</small><div class='my-val'>{avg_f0:.1f} Hz</div><p style='color:#666; font-size:0.8rem;'>보정 가중치: x{weight}</p></div>", unsafe_allow_html=True)
                
                if diff <= 30: # 난이도를 고려해 오차 범위를 30으로 살짝 늘렸습니다.
                    st.balloons()
                    st.markdown("<div style='text-align:center; color:#00FF88;' class='banner'>🎉 PERFECT!</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f" <div style='text-align:center; color:#FFD700;' class='banner'>오차: {diff:.1f} Hz</div>", unsafe_allow_html=True)
            else:
                st.warning("목소리 주파수가 너무 낮거나 높습니다.")
        else:
            st.warning("소리가 너무 작습니다.")
            
    except Exception:
        st.error("처리 중 렉이 발생했습니다. 다시 시도해 주세요.")
