#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import google.cloud.texttospeech as gtts
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/momoe/Documents/GitHub/ChatRobotsForKids/audio/key.json"


class Speaker:
    def __init__(self, lang='cn') -> None:
        self.lang = lang
        self.voice_params = gtts.VoiceSelectionParams(
            language_code='en-US', name="en-US-Wavenet-F"
        )
        self.audio_config = gtts.AudioConfig(audio_encoding=gtts.AudioEncoding.LINEAR16)
        self.client = gtts.TextToSpeechClient()

    def text_to_wav(self, text: str):
        text_input = gtts.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=text_input, voice=self.voice_params, audio_config=self.audio_config
        )

        filename = f"audio-{self.lang}.wav"
        with open(filename, "wb") as out:
            out.write(response.audio_content)
            # print(f'Generated speech saved to "{filename}"')

    def change_lang(self, lang):
        self.lang = lang
        if self.lang == 'en':
            voice_name = "en-US-Wavenet-F"
        elif self.lang == 'cn':
            voice_name = "cmn-CN-Wavenet-A"
        language_code = "-".join(voice_name.split("-")[:2])
        self.voice_params = gtts.VoiceSelectionParams(
            language_code=language_code, name=voice_name
        )

    def speak(self, text, speed = 1):
        if self.lang == 'en':
            self.text_to_wav(text)
            os.system("afplay audio-en.wav")
            #os.system("play -q audio-en.wav speed " + str(speed))
        elif self.lang == 'cn':
            self.text_to_wav(text)
            os.system("afplay audio-cn.wav")
            #os.system("play -q audio-cn.wav speed " + str(speed))
        else:
            return "Unsupported language"


if __name__ == "__main__":
    pi = Speaker()
    pi.speak("I am happy", 1.4)
    pi.change_lang('cn')
    pi.speak("我不开心", 0.85)
