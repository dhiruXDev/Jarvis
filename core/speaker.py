# import pyttsx3

# engine = pyttsx3.init()
# engine.setProperty('rate', 170)

# def speak(text):
#     print(f"Jarvis: {text}")
#     engine.say(text)
#     engine.runAndWait()

# import pyttsx3

# engine = pyttsx3.init()

# def speak(text):
#     try:
#         print("Jarvis:", text)
#         engine.say(text)
#         engine.runAndWait()
#     except:
#         print("Speech error")

import pyttsx3

def speak(text):
    print("Jarvis:", text)

    try:
        engine = pyttsx3.init('sapi5')   # re-init every time
        engine.setProperty('rate', 170)

        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("Speech error:", e)