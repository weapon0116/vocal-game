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

st.title("🎯 파워 주파수 챌린지")

# --- [2. 게임 로직] ---
if 'target_hz' not in st.session_state:
    st.session_state.target_hz = round(random.uniform(200.0, 800.0), 1)

st.markdown(f"""
    <div class='game-display'>
        <p style='color:#888; margin-bottom:0;'>MISSION TARGET</p>
        <div class='target-val'>{st.session_state.target_hz} Hz</div>
    </div>
""", unsafe_allow_html=True)

if st.button("🔄 타겟 변경", use_container_width=True):
    # 보정치에 맞춰 타겟 범위도 시원하게 올렸습니다.
    st.session_state.target_hz = round(random.uniform(200.0, 800.0), 1)
    st.rerun()

game_audio = st.audio_input("지금 바로 소리내보세요!", key="game_input")

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
            
            # 🔥 [파워 가변 보정 로직]
            # 전체적으로 보정 배수를 확 끌어올렸습니다.
            if raw_f0 < 150:
                weight = 1.8  # 저음도 이제 꽤 높게 나옵니다.
            elif raw_f0 < 250:
                weight = 2.4  # 중음은 확실하게 뻥튀기!
            else:
                weight = 3.0  # 고음은 3배까지 미친듯이 올라갑니다.
            
            avg_f0 = raw_f0 * weight
            
            # 최종 판정
            if 80 < avg_f0 < 1500: # 범위 제한도 1500까지 넉넉하게!
                diff = abs(avg_f0 - st.session_state.target_hz)
                
                # 결과값만 깔끔하게 표시 (뭘 곱했는지는 비밀!)
                st.markdown(f"<div class='report-box'><small>분석 결과</small><div class='my-val'>{avg_f0:.1f} Hz</div></div>", unsafe_allow_html=True)
                
                if diff <= 40: # 수치가 커진 만큼 성공 범위도 40으로 넉넉하게 조절
                    st.balloons()
                    st.markdown("<div style='text-align:center; color:#00FF88;' class='banner'>🎉 PERFECT!</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:center; color:#FFD700;' class='banner'>오차: {diff:.1f} Hz</div>", unsafe_allow_html=True)
            else:
                st.warning("목소리 주파수가 범위를 벗어났습니다.")
        else:
            st.warning("소리가 너무 작습니다.")
            
    except Exception:
        st.error("처리 중 오류가 발생했습니다. 다시 시도해 주세요.")
