import speech_recognition as sr
import sounddevice as sd
import numpy as np
import time
from scipy.io.wavfile import write
from LLM import run_terminal_agent
from constants import AUDIO_PHRASE_TIME_LIMIT, MAX_VOLUME_THRESHOLD

recogniser = sr.Recognizer()

def save_audio(audio: sr.AudioData):
    """
    Saves audio to external .wav file

    Args:
        audio: audio data

    Returns:
        None
    """
    with open("voice_control\\recordings\\recorded_audio.wav", "wb") as f:
        f.write(audio.get_wav_data())

def print_volume(indata: np.ndarray, frames: int, time: any, status: any):
    """
    Outputs the normalized microphone volume to the console.

    This function calculates the volume by computing the Euclidean norm (L2 norm) of the input audio data 
    and multiplies it by 10 for scaling. The resulting value is printed in a formatted string with two decimal places.

    Args:
        indata (numpy.ndarray): The input audio data captured from the microphone.
        frames (int): The number of audio frames in the data (unused in this function but typically required by audio libraries).
        time (object): The time information related to the audio stream (unused in this function).
        status (object): The status information of the audio input stream (unused in this function).

    Returns:
        None
    """
    volume_norm = np.linalg.norm(indata) * MAX_VOLUME_THRESHOLD
    print(f"Microphone Volume: {volume_norm:.2f}")


def capture_voice_input() -> sr.AudioData:
    """
    Captures and returns voice input from the microphone for 5 seconds.

    This function uses the `speech_recognition` library to capture audio from the microphone. 
    It listens to the input for a maximum of 5 seconds and returns the recorded audio data.

    Args:
        None

    Returns:
        AudioData: An AudioData object containing the recorded audio input.
    """
    with sr.Microphone() as source:
        #print(f"Listening on source", source.list_microphone_names(), "\n\n", source.list_working_microphones())
        print("Listening...")
        
        audio = recogniser.listen(source, phrase_time_limit=AUDIO_PHRASE_TIME_LIMIT)
        save_audio(audio)
    return audio


def convert_voice_to_text(audio: sr.AudioData):
    """
    Takes in the recorded audio and converts it into text.
    """
    try:
        text = recogniser.recognize_google(audio)
        print(text)
    except sr.UnknownValueError:
        text = ""
        print("Not understood")
        #return
    except sr.RequestError as e:
        text = ""
        print("Error; {0}".format(e))
    return text


def process_voice_command(text: str):
    """
    Takes in the voice in text form and sends it to LLM and returns the converted drone command.
    """
    commands = {
        "left": "Left",
        "right": "Right",
        "up": "Up",
        "down": "Down",
        "forward": "Forward",
        "back" : "Back"
    }
    command = text.lower()
    # Call the LLM to convert text
    result = run_terminal_agent(text)
    print(result)
    


def main():
    #end_program = False
    #while not end_program:
    audio = capture_voice_input()
    text = convert_voice_to_text(audio)
    end_program = process_voice_command(text)
    print(end_program)
    #time.sleep(1)

if __name__ == "__main__":
    main()
