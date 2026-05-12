import streamlit as st
import numpy as np
import librosa  # 분석 모드와 동일한 엔진 사용
import io
import random
import scipy.io.wavfile as wav

# --- [1. 기본 설정] ---
st.set_page_config(page_title="V-RAP: 주파수 챌린지", layout="centered")

# --- [2. CSS 디자인] ---
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
    </style>
""", unsafe_allow_html=True)

st.title("🎯 주파수 일치 게임")

# --- [3. 게임 로직] ---
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

game_audio = st.audio_input("목소리를 내주세요! (분석 모드와 동일 엔진)", key="game_v2")

if game_audio:
    try:
        # 1. 오디오 로드 (scipy로 빠르게 읽기)
        sr, y = wav.read(io.BytesIO(game_audio.read()))
        if len(y.shape) > 1: y = y[:, 0]
        
        # 2. 데이터 정규화 및 부동소수점 변환 (librosa 호환용)
        y = y.astype(float) / np.max(np.abs(y)) if np.max(np.abs(y)) > 0 else y.astype(float)
        
        # 3. [핵심] 분석 모드와 동일한 YIN 알고리즘 적용
        # 렉 방지를 위해 데이터는 짧게(0.7초) 쓰지만, 계산 방식은 동일하게 가져갑니다.
        with st.spinner('🎯 정확하게 측정 중...'):
            # 분석 모드와 동일한 최소(C2)/최대(C6) 범위 설정
            fmin = librosa.note_to_hz('C2')
            fmax = librosa.note_to_hz('C6')
            
            # 0.7초 분량만 추출해서 계산 속도 보완
            y_segment = y[:int(sr * 0.7)]
            f0 = librosa.yin(y_segment, fmin=fmin, fmax=fmax, sr=sr)
            avg_f0 = np.nanmean(f0)

        if not np.isnan(avg_f0):
            diff = abs(avg_f0 - st.session_state.target_hz)
            st.markdown(f"<div class='report-box'><small>나의 기록</small><div class='my-val'>{avg_f0:.1f} Hz</div></div>", unsafe_allow_html=True)
            
            if diff <= 20:
                st.balloons()
                st.success("🎉 PERFECT! 분석 결과와 동일한 엔진으로 성공하셨습니다!")
            else:
                st.warning(f"오차: {diff:.1f} Hz (조금만 더 조절해보세요!)")
        else:
            st.warning("소리가 감지되지 않았습니다.")

    except Exception as e:
        st.error(f"오류 발생: {e}")
