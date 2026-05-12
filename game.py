import streamlit as st
import numpy as np
import librosa
import io
import random
import scipy.io.wavfile as wav

# --- [기본 설정 및 디자인 생략 - 기존과 동일] ---

# ... (상단 CSS 및 디자인 부분은 그대로 유지) ...

if game_audio:
    try:
        # 1. 초고속 로드 (sr=16000 고정으로 연산량 감소)
        audio_bytes = game_audio.read()
        sr, y = wav.read(io.BytesIO(audio_bytes))
        if len(y.shape) > 1: y = y[:, 0]
        
        # 2. [최적화 핵심 1] 데이터 형 변환 및 정규화 간소화
        y = y.astype(np.float32) / 32768.0 
        
        # 3. [최적화 핵심 2] 분석 구간을 0.4초로 더 줄임 (게임용으론 충분)
        # 그리고 hop_length를 키워서 연산 횟수를 절반으로 줄임
        with st.spinner('🎯 매칭 중...'):
            y_segment = y[:int(sr * 0.4)]
            
            # librosa.yin의 속도를 결정하는 파라미터 튜닝
            f0 = librosa.yin(
                y_segment, 
                fmin=librosa.note_to_hz('C2'), 
                fmax=librosa.note_to_hz('C6'), 
                sr=sr,
                hop_length=1024  # 이 값이 커질수록 속도가 비약적으로 빨라집니다!
            )
            avg_f0 = np.nanmean(f0)

        if not np.isnan(avg_f0):
            # 결과 출력 로직 (기존과 동일)
            # ...
