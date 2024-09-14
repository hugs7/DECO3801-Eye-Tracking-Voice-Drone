"""
Module for audio processing.
"""

from logger_helper import init_logger
import speech_recognition as sr
import numpy as np

import constants as c
import file_handler
import date

logger = init_logger()


class AudioRecogniser:
    def __init__(self):
        self.recogniser = sr.Recognizer()

    def save_audio(self, audio: sr.AudioData):
        """
        Saves audio to external .wav file

        Args:
            audio: audio data

        Returns:
            None
        """
        recording_folder = file_handler.get_recordings_folder()
        file_handler.create_folder_if_not_exists(recording_folder)

        timestamp = date.timestamp_filename_safe()
        recording_name = f"recording_{timestamp}.wav"
        recording_save_path = recording_folder / recording_name

        logger.info(f"Saving audio to {recording_save_path}")
        with open(recording_save_path, c.WRITE_BINARY_MODE) as f:
            f.write(audio.get_wav_data())

        logger.info(f"Audio saved to {recording_save_path}")

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
        volume_norm = np.linalg.norm(indata) * c.MAX_VOLUME_THRESHOLD
        logger.info(f"Microphone Volume: {volume_norm:.2f}")

    def capture_voice_input(self) -> sr.AudioData:
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
            logger.debug(f"Listening on source", source.list_microphone_names(
            ), "\n\n", source.list_working_microphones())
            logger.info("Listening...")

            audio = self.recogniser.listen(
                source, phrase_time_limit=c.AUDIO_PHRASE_TIME_LIMIT)
            self.save_audio(audio)
        return audio

    def load_audio(self) -> sr.AudioData:
        """
        Loads most recent audio file from recordings folder if available.

        Args:
            None

        Returns:
            AudioData: An AudioData object containing the recorded audio input.
        """
        logger.info("Loading audio...")

        recordings_folder = file_handler.get_recordings_folder()
        audio_files = file_handler.list_files_in_folder(
            recordings_folder, c.AUDIO_FILE_EXTENSIONS)

        if not audio_files:
            logger.info("No audio files found. Listening for new audio...")
            return self.capture_voice_input()

        most_recent_audio_file = sorted(
            audio_files, key=lambda x: x.stat().st_ctime, reverse=True)[0]

        logger.info(f"Loading audio from {most_recent_audio_file}")
        with open(most_recent_audio_file, c.READ_BINARY_MODE) as f:
            audio = sr.AudioData(f.read(), c.MAX_VOLUME_THRESHOLD, 1)
        return audio

    def convert_voice_to_text(self, audio: sr.AudioData):
        """
        Takes in the recorded audio and converts it into text.
        """
        logger.info("Converting audio to text...")

        try:
            text = self.recogniser.recognize_google(audio)
            logger.info(f"You said: '{text}'")
        except sr.UnknownValueError:
            text = ""
            logger.warning("Not understood")
            # return
        except sr.RequestError as e:
            text = ""
            logger.error(e)
        return text
