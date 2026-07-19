from speech import speak, listen
from command import execute_command

def start_assistant():

    speak("Hello, I am Nova. How can I help you")

    while True:

        command = listen()

        print("Assistant received:", command)


        if command:
            execute_command(command)