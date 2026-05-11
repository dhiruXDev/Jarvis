
import threading
import speech_recognition as sr
from langdetect import detect
from deep_translator import GoogleTranslator
import pyttsx3

# ---------------------------
# 🔊 FAST LOCAL ENGINE (English)
# ---------------------------
_engine = pyttsx3.init('sapi5')
_engine.setProperty('rate', 165)
_engine.setProperty('volume', 1.0)
try:
    voices = _engine.getProperty('voices')
    _engine.setProperty('voice', voices[1].id)  # 0=male, 1=female (try both)
except:
    pass

def _speak_local(text):
    try:
        _engine.stop()
        _engine.say(text)
        _engine.runAndWait()
    except Exception as e:
        print("Local TTS error:", e)

# ---------------------------
# 🎙 Listen
# ---------------------------
_recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        _recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = _recognizer.listen(source, timeout=8, phrase_time_limit=5)
            text = _recognizer.recognize_google(audio)
            print("🧑 You:", text)
            return text
        except sr.WaitTimeoutError:
            print("⏱️ Timeout")
            return ""
        except sr.UnknownValueError:
            print("❌ Couldn't understand")
            return ""
        except Exception as e:
            print("Mic error:", e)
            return ""

# ---------------------------
# 🌍 Language detect + translate
# ---------------------------
def detect_lang(text):
    try:
        return detect(text)
    except:
        return "en"

def to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text  # fallback

def from_english(text, lang):
    if lang == "en":
        return text
    try:
        return GoogleTranslator(source='en', target=lang).translate(text)
    except:
        return text  # fallback

# ---------------------------
# 🔊 HYBRID SPEAK
# en → pyttsx3 (fast)
# others → gTTS (multilang)
# ---------------------------
def speak(text, lang="en"):

    print("🤖 Jarvis:", text)

    try:

        _engine.stop()

        voices = _engine.getProperty("voices")

        # English voice
        if lang == "en":
            _engine.setProperty(
                "voice",
                voices[1].id
            )

        _engine.say(text)

        _engine.runAndWait()

    except Exception as e:

        print("Speak Error:", e)