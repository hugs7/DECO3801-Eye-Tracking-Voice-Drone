import speech_recognition as sr
import sounddevice as sd
import numpy as np
import time
from scipy.io.wavfile import write


recognizer = sr.Recognizer()

def save_audio(audio):
    with open("recorded_audio.wav", "wb") as f:
        f.write(audio.get_wav_data())

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
        
        audio = recognizer.listen(source, phrase_time_limit=5)
        save_audio(audio)
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
    commands = {
        "left": "Left",
        "right": "Right",
        "up": "Up",
        "down": "Down",
        "forward": "Forward",
        "back" : "Back"
    }
    command = text.lower()
    # Use the get method to provide a default value if the command is not found
    result = commands.get(command, "Command Not understood. Try again.")
    print(result)
    return False


def main():
    end_program = False
    while not end_program:
        audio = capture_voice_input()
        text = convert_voice_to_text(audio)
        end_program = process_voice_command(text)
        time.sleep(1)


if __name__ == "__main__":
    main()
