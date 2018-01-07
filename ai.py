import recorder
import re
from pynput.keyboard import Key, Listener


def printUser(text):
    print("User:", text)


def printComputer(text):
    print("Computer:", text)


def response(text):
    if "smokes" in text.lower():
        return "Fuck you Ricky!"


printComputer("Hello, my name is Bot!")

while True:
    with recorder.AudioRecorder() as rec:

        def on_press(key):
            if key == Key.ctrl_l:
                if rec.closed:
                    rec.start()


        def on_release(key):
            if key == Key.ctrl_l:
                rec.stop()
                return False


        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

        text = rec.transcribe()

        if text:
            printUser(text + "!")
        else:
            printUser(text)

        if text.endswith("let's go"):
            printComputer(response(re.sub("let's go", "", text)))
        elif not text:
            printComputer("You didn't say anything")
        else:
            printComputer("Please end your sentence with a command: 'let's go'")
