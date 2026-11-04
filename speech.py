import pyttsx3
import speech_recognition as sr
import sounddevice as sd


def speak(text):

    print("Speaking:", text)

    try:
        engine = pyttsx3.init()

        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)

        voices = engine.getProperty("voices")

        # Default voice set
        if voices:
            engine.setProperty("voice", voices[0].id)

        engine.say(str(text))

        engine.runAndWait()

        engine.stop()

    except Exception as e:
        print("Speech Error:", e)



def listen():

    recognizer = sr.Recognizer()

    print("Listening...")

    duration = 5
    sample_rate = 16000


    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )

    sd.wait()


    audio_data = sr.AudioData(
        recording.tobytes(),
        sample_rate,
        2
    )


    try:

        command = recognizer.recognize_google(audio_data)

        print("You said:", command)

        return command.lower()


    except Exception:

        print("Sorry, I did not understand")

        return ""