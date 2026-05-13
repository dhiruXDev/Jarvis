# pyrefly: ignore [missing-import]
import speech_recognition as sr
# pyrefly: ignore [missing-import]
import pyttsx3
# pyrefly: ignore [missing-import]
from langdetect import detect
# pyrefly: ignore [missing-import]
from deep_translator import GoogleTranslator

# =========================
# TTS ENGINE
# =========================

_engine = pyttsx3.init("sapi5")

_engine.setProperty("rate", 165)
_engine.setProperty("volume", 1.0)

voices = _engine.getProperty("voices")

# English voice
_engine.setProperty("voice", voices[0].id)

# =========================
# SPEECH RECOGNITION
# =========================

_recognizer = sr.Recognizer()

# =========================
# HINGLISH NORMALIZATION
# =========================

HINGLISH_MAP = {

    # OPEN
    "kholo": "open",
    "kholna": "open",
    "khol": "open",
    "open karo": "open",
    "kholo na": "open",

    # CLOSE
    "band karo": "close",
    "band": "close",

    # PLAY
    "chalao": "play",
    "bajao": "play",

    # STOP
    "rok do": "stop",
    "band kar do": "stop",

    # SCREENSHOT
    "screenshot lo": "take screenshot",
    "photo lo": "take screenshot",

    # VOLUME
    "awaz": "volume",
    "awaaz": "volume",

    # MUSIC
    "gaana": "song",
    "gana": "song",

    # COMMON APPS
    "youtube": "youtube",
    "chrome": "chrome",
    "whatsapp": "whatsapp",
    "settings": "settings",

    # increase 
    "badhana": "increase",
    "badhao": "increase",
    "badhaiyo": "increase",

    # decrease
    "kam karna": "decrease",
    "kam": "decrease",
    "kam kar do": "decrease",

    # tell
    "btana": "tell",
    "batao": "tell",
    "batao na": "tell",

    # what is
    "kya hai": "what is",
    
}

# =========================
# LANGUAGE DETECTION
# =========================

def detect_lang(text):

    try:

        detected = detect(text)

        print(f"[LANG DETECTED] {detected}")

        return detected

    except:

        return "en"

# =========================
# NORMALIZATION
# =========================

def normalize_hinglish(text):

    text = text.lower().strip()

    for hindi, english in HINGLISH_MAP.items():

        if hindi in text:

            text = text.replace(hindi, english)

    # chrome open -> open chrome
    words = text.split()

    if len(words) >= 2:

        if words[-1] == "open":

            app = " ".join(words[:-1])

            text = f"open {app}"

        elif words[-1] == "close":

            app = " ".join(words[:-1])

            text = f"close {app}"

        elif words[-1] == "play":

            media = " ".join(words[:-1])

            text = f"play {media}"

    print(f"[NORMALIZED] {text}")

    return text

# =========================
# TO ENGLISH
# =========================

def to_english(text):

    text = normalize_hinglish(text)

    lang = detect_lang(text)

    # Already English/Hinglish normalized
    if lang == "en":
        return text

    try:

        translated = GoogleTranslator(
            source="auto",
            target="en"
        ).translate(text)

        print(f"[TRANSLATED] {translated}")

        return translated

    except Exception as e:

        print("Translation Error:", e)

        return text

# =========================
# FROM ENGLISH
# =========================

def from_english(text, lang):

    if lang == "en":
        return text

    try:

        translated = GoogleTranslator(
            source="en",
            target="hi"
        ).translate(text)

        return translated

    except:

        return text

# =========================
# LISTEN
# =========================

def listen():

    with sr.Microphone() as source:

        print("🎤 Listening...")

        _recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )

        try:

            audio = _recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=5
            )

            text = _recognizer.recognize_google(
                audio,
                language="hi-IN"
            )

            print(f"🧑 User: {text}")

            return text

        except sr.WaitTimeoutError:

            return ""

        except sr.UnknownValueError:

            return ""

        except Exception as e:

            print("Mic Error:", e)

            return ""

# =========================
# SPEAK
# =========================

def speak(text, lang="en"):

    try:

        final_text = from_english(text, lang)

        print(f"🤖 Jarvis: {final_text}")

        _engine.stop()

        _engine.say(final_text)

        _engine.runAndWait()

    except Exception as e:

        print("Speak Error:", e)