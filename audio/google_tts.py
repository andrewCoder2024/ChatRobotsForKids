import google.cloud.texttospeech as tts
import os

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/ChatRobotsForKids/audio/key.json"
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/andrewlustig/Documents/GitHub/ChatRobotsForKids/key.json"


def text_to_wav(voice_name: str, text: str):
    language_code = "-".join(voice_name.split("-")[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input, voice=voice_params, audio_config=audio_config
    )

    filename = f"{language_code}.wav"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
        print(f'Generated speech saved to "{filename}"')

    return filename


os.system("play -q " + text_to_wav("cmn-CN-Wavenet-A", "纽约的天气怎么样？"))
os.system("play -q " + text_to_wav("en-US-Wavenet-F", "What is the temperature in New York?"))
