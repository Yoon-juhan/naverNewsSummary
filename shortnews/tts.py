"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""

from google.cloud import texttospeech

def tts(df):

    for i in range(len(df)):

        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=df['content'][i])

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR", 
            # ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            name="ko-KR-Neural2-A"
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1,  # 재생속도?
            pitch=0
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        with open(f"tts_mp3/{i}.mp3", "wb") as out:     # mp3 다운 경로
            # Write the response to the output file.
            out.write(response.audio_content)
            print(f'Audio content written to file "{i}.mp3"')