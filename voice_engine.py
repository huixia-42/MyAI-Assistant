import os
import re
import json
import requests
import pygame

# 初始化 pygame 音频引擎
pygame.mixer.init()

def play_audio(filepath):
    try:
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"[Audio Play Error] {e}")

def speak_japanese(text, emotion_id=61):
    try:
        query_url = "http://127.0.0.1:50021/audio_query"
        params = {"text": text, "speaker": emotion_id} 
        query_response = requests.post(query_url, params=params)
        query_response.raise_for_status() 
        audio_query = query_response.json()

        # 根据情绪微调音频参数
        if emotion_id == 62: 
            audio_query["speedScale"] = 1.2
            audio_query["pitchScale"] = 0.05
            audio_query["intonationScale"] = 1.3
        elif emotion_id == 63: 
            audio_query["speedScale"] = 0.9
            audio_query["pitchScale"] = -0.05
            audio_query["intonationScale"] = 1.2
        elif emotion_id == 64: 
            audio_query["speedScale"] = 0.8
            audio_query["pitchScale"] = -0.1
            audio_query["intonationScale"] = 0.8

        synthesis_url = "http://127.0.0.1:50021/synthesis"
        synth_params = {"speaker": emotion_id}
        synth_response = requests.post(
            synthesis_url, params=synth_params,
            data=json.dumps(audio_query),
            headers={"Content-Type": "application/json"}
        )
        synth_response.raise_for_status()

        # 强制使用绝对路径保存音频
        script_dir = os.path.dirname(os.path.abspath(__file__))
        wav_file = os.path.join(script_dir, "temp_jp.wav")
        with open(wav_file, "wb") as f:
            f.write(synth_response.content)

        play_audio(wav_file)
        
        # 播放完毕，清理文件
        if os.path.exists(wav_file):
            os.remove(wav_file)
            
    except Exception as e:
        print(f"[VOICEVOX Engine Error] {e}")

def speak_bilingual(reply_text, emotion_id):
    jp_match = re.search(r'\[JP\](.*?)\[/JP\]', reply_text, re.DOTALL)
    if jp_match:
        jp_text = jp_match.group(1).strip()
        speak_japanese(jp_text, emotion_id)