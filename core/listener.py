import speech_recognition as sr

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8


def listen():

    try:

        # with sr.Microphone() as source:

        #     print("Listening...")

        #     recognizer.adjust_for_ambient_noise(
        #         source,
        #         duration=1
        #     )

        #     audio = recognizer.listen(
        #         source,
        #         timeout=10,
        #         phrase_time_limit=8
        #     )

        # print("Recognizing...")

        # command = recognizer.recognize_google(audio)
        command = input("You: ")
        # print("You:", command)

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