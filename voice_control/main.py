import speech_recognition as sr
import sounddevice as sd
import numpy as np

recognizer = sr.Recognizer()


def print_volume(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    print(f"Microphone Volume: {volume_norm:.2f}")


def capture_voice_input():
    """ with sd.InputStream(callback=print_volume):
        sd.sleep(10000)

    return"""
    with sr.Microphone() as source:
        #print(f"Listening on source", source.list_microphone_names(), "\n\n", source.list_working_microphones())
        print("Listening...")
        audio = recognizer.listen(source)
    return audio


def convert_voice_to_text(audio):
    try:
        text = recognizer.recognize_google(audio)
        print(text)
    except sr.UnknownValueError:
        text = ""
        print("Not understood")
    except sr.RequestError as e:
        text = ""
        print("Error; {0}".format(e))
    return text


def process_voice_command(text):
    if "left" in text.lower():
        print("Left")
    elif "right" in text.lower():
        print("Right")
    elif "up" in text.lower():
        print("Up")
    elif "down" in text.lower():
        print("Down")  
    else:
        print("Command Not understood. Try again.")
    return False


def main():
    end_program = False
    while not end_program:
        audio = capture_voice_input()
        text = convert_voice_to_text(audio)
        end_program = process_voice_command(text)


if __name__ == "__main__":
    main()
