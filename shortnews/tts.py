from google.cloud import texttospeech
import re
from database import selectHour
from tqdm.notebook import tqdm

def tts():

    df = selectHour()

    # for i in tqdm(range(len(df)), desc="TTS"):
    for i in tqdm(range(2), desc="TTS"):  # 테스트용 2개
        try:
            text = df['CONTENT'][i]
            
            text = re.sub("다\.", "다,", text)
            text = re.sub('[‘’“”`"\']','',text)

            client = texttospeech.TextToSpeechClient()

            synthesis_input = texttospeech.SynthesisInput(text=text)

            # 여
            voice1 = texttospeech.VoiceSelectionParams(
                language_code="ko-KR", 
                # ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
                name="ko-KR-Neural2-B"
            )

            # 남
            voice2 = texttospeech.VoiceSelectionParams(
                language_code="ko-KR", 
                # ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
                name="ko-KR-Neural2-C"
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1,  # 재생속도?
                pitch=0
            )

            response1 = client.synthesize_speech(
                input=synthesis_input, voice=voice1, audio_config=audio_config
            )

            response2 = client.synthesize_speech(
                input=synthesis_input, voice=voice2, audio_config=audio_config
            )

            with open(f"tts_mp3/{df['NEWS_ID'][i]}_female.mp3", "wb") as out:     # mp3 다운 경로
                out.write(response1.audio_content)
            
            with open(f"tts_mp3/{df['NEWS_ID'][i]}_male.mp3", "wb") as out:     # mp3 다운 경로
                out.write(response2.audio_content)

        except Exception as e:
            print(f"{df['NEWS_ID'][i]} mp3 생성 실패", e)