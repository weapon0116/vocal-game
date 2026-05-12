import streamlit as st
import numpy as np
import librosa
import io
import random
import scipy.io.wavfile as wav

# --- [1. 기본 설정 및 디자인] ---
st.set_page_config(page_title="V-RAP: 주파수 챌린지", layout="centered")

st.markdown("""
    <style>
        .target-box { 
            background: linear-gradient(145deg, #121212, #252525); 
            padding: 30px; border-radius: 20px; border: 3px solid #FF4B4B; 
            text-align: center; margin-bottom: 20px;
        }
        .target-val { font-size: 4rem; font-weight: 900; color: #FF4B4B; }
        .my-val { font-size: 3.5rem; font-weight: 800; color: #00BFFF; }
        .report-box { 
            background-color: #1E1E1E; padding: 15px; border-radius: 12px; 
            border: 1px solid #444; text-align: center; margin-bottom: 10px;
        }
        .banner { font-size: 2.5rem !important; font-weight: 900; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 주파수 일치 게임")

# --- [2. 게임 로직] ---
if 'target_hz' not in st.session_state:
    st.session_state.target_hz = round(random.uniform(160.0, 300.0), 1)

st.markdown(f"""
    <div class='target-box'>
        <p style='color:#888;'>TARGET</p>
        <div class='target-val'>{st.session_state.target_hz} Hz</div>
    </div>
""", unsafe_allow_html=True)

if st.button("🔄 타겟 변경", use_container_width=True):
    st.session_state.target_hz = round(random.uniform(160.0, 300.0), 1)
    st.rerun()

game_audio = st.audio_input("목소리를 내주세요!", key="game_v3")

if game_audio:
    try:
        # 1. 초고속 로드
        audio_bytes = game_audio.read()
        sr, y = wav.read(io.BytesIO(audio_bytes))
        if len(y.shape) > 1: y = y[:, 0]
        
        # 2. 데이터 최적화 (32비트 변환)
        y = y.astype(np.float32) / 32768.0 
        
        # 3. 정밀 분석 (분석 모드와 동일 엔진 + 속도 튜닝)
        with st.spinner('🎯 정밀 매칭 중...'):
            # 분석 구간을 0.5초로 최적화
            y_segment = y[:int(sr * 0.5)]
            
            # hop_length를 1024로 높여서 연산 속도를 대폭 개선 (정밀도는 유지)
            f0 = librosa.yin(
                y_segment, 
                fmin=librosa.note_to_hz('C2'), 
                fmax=librosa.note_to_hz('C6'), 
                sr=sr,
                hop_length=1024
            )
            avg_f0 = np.nanmean(f0)

        # 4. 결과 출력
        if not np.isnan(avg_f0):
            diff = abs(avg_f0 - st.session_state.target_hz)
            st.markdown(f"<div class='report-box'><small>나의 기록</small><div class='my-val'>{avg_f0:.1f} Hz</div></div>", unsafe_allow_html=True)
            
            if diff <= 20:
                st.balloons()
                st.markdown("<div style='text-align:center; color:#00FF88;' class='banner'>🎉 SUCCESS!</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center; color:#FFD700;' class='banner'>오차: {diff:.1f} Hz</div>", unsafe_allow_html=True)
        else:
            st.warning("소리가 너무 작거나 감지되지 않았습니다.")

    except Exception as e:
        st.error(f"분석 중 오류가 발생했습니다. 다시 시도해주세요.")
