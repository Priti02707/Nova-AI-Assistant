import datetime
import webbrowser
import wikipedia
import pyjokes
import pywhatkit

wikipedia.set_lang("en")

from speech import speak


def execute_command(command):

    print("Command received:", command)

    command = command.lower()


    if "time" in command:

        current_time = datetime.datetime.now().strftime("%I:%M %p")

        speak("The current time is " + current_time)


    elif "date" in command:

        today = datetime.datetime.now().strftime("%d %B %Y")

        speak("Today's date is " + today)


    elif "open google" in command:

        webbrowser.open("https://www.google.com")

        speak("Opening Google")


    elif "open youtube" in command:

        webbrowser.open("https://www.youtube.com")

        speak("Opening YouTube")


    elif "play" in command:

        song = command.replace("play", "")

        speak("Playing " + song)

        pywhatkit.playonyt(song)

    
    elif "wikipedia" in command or "search" in command or "who is" in command or "what is" in command:

        try:

            topic = command.replace("wikipedia", "")
            topic = topic.replace("search", "")
            topic = topic.replace("who is", "")
            topic = topic.replace("what is", "")
            topic = topic.strip()

            print("Searching Wikipedia:", topic)

            speak("Searching Wikipedia")

            result = wikipedia.summary(topic, sentences=1)

            print("Result:", result)

            speak("I found the information")

            speak(result)


        except Exception as e:

           print("Wikipedia Error:", e)

           speak("Sorry, I could not find information")
    
        

    elif "joke" in command:

        joke = pyjokes.get_joke()

        print(joke)

        speak(joke)


    elif "exit" in command or "goodbye" in command or "stop" in command:

        speak("Goodbye")

        exit()


    else:

        speak("Sorry, I don't understand this command")