# import speech_recognition as sr

# recognizer = sr.Recognizer()

# def listen():
#     with sr.Microphone() as source:
#         print("Listening...")
#         recognizer.adjust_for_ambient_noise(source)

#         try:
#             audio = recognizer.listen(source, timeout=5)
#             command = recognizer.recognize_google(audio)
#             print("You:", command)
#             return command.lower()
#         except:
#             return ""
import speech_recognition as sr

recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("Listening...")

        recognizer.energy_threshold = 300
        recognizer.pause_threshold = 1

        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            command = recognizer.recognize_google(audio)

            print("You:", command)
            return command.lower()

        except sr.WaitTimeoutError:
            print("Listening timeout")
            return ""

        except sr.UnknownValueError:
            print("Didn't understand")
            return ""

        except Exception as e:
            print("Error:", e)
            return ""