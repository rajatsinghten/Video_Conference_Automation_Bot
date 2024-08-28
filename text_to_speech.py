# from gtts import gTTS
# import os


# def text_to_speech(text, lang='en'):
#     tts = gTTS(text=text, lang=lang)
#     tts.save("output.wav")
#     os.system("start output.wav")

import pyttsx3
text_speech = pyttsx3.init()

def text_to_speech(text):
    text_speech.say(text)
    text_speech.runAndWait()