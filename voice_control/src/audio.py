"""
Module for audio processing.
"""

from typing import Optional
import speech_recognition as sr
import numpy as np
from omegaconf import OmegaConf

from common.logger_helper import init_logger

from . import constants as c
from . import file_handler
from . import date

logger = init_logger()


class AudioRecogniser:
    def __init__(self, audio_config: OmegaConf):
        self.recogniser = sr.Recognizer()
        self.config = audio_config

        self.wake_command = self.config.wake_command

    def detect_wake_word(self, audio: sr.AudioData) -> bool:
        """
        Detects the wake word (defined in config) in the audio data.

        Args:
            audio (sr.AudioData): The audio data to check for the wake word.

        Returns:
            bool: True if the wake word is detected, False otherwise.
        """

        command = self.convert_voice_to_text(audio)

        wake_word_detected = self.wake_command.lower() in command.lower()

        if wake_word_detected:
            logger.info(f"Wake word detected: '{self.wake_command}'")

        return wake_word_detected

    def listen_for_wake_word(self):
        """
        Listens continuously for the wake word defined in config.
        Once the wake word is detected, it listens continuously until the user stops speaking.

        Args:
            None

        Returns:
            AudioData: AudioData object containing the recorded audio after wake word is detected.
        """

        with sr.Microphone() as source:
            logger.info("Listening for wake word...")

            while True:
                audio = self.listen_for_audio(source, False)
                if self.detect_wake_word(audio):
                    logger.info("Wake word detected, listening for commands...")
                    return self.listen_until_silence(source)

    def listen_until_silence(self, source: sr.Microphone):
        """
        Listens to the user's voice until they stop speaking.
        Uses a combination of timeouts and silence detection to end listening.

        Args:
            source (sr.Microphone): The microphone input source.

        Returns:
            AudioData: The recorded audio input.
        """
        logger.info("Listening for user input...")

        # Adjust for ambient noise to improve speech detection
        self.recogniser.adjust_for_ambient_noise(source)
        try:
            audio = self.listen_for_audio(source, True)
            self.save_audio(audio)
            return audio
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out.")
            return None

    def listen_for_audio(self, source: Optional[sr.Microphone] = None, save: bool = False) -> sr.AudioData:
        """
        Listens for audio input from the microphone.

        Args:
            source (sr.Microphone): The microphone input source. If None, a new microphone source is created.

        Returns:
            AudioData: The recorded audio input.
        """

        def listen_callback(source: sr.Microphone) -> sr.AudioData:
            logger.info("    >>> Listening for audio...")
            audio = self.recogniser.listen(source, timeout=self.config.listen_timeout, phrase_time_limit=self.config.phrase_time_limit)
            logger.info("    <<< Finished listening.")
            return audio

        if source:
            audio = listen_callback(source)
        else:
            with sr.Microphone() as source:
                audio = listen_callback(source)

        if save:
            self.save_audio(audio)
        return audio

    def capture_voice_input(self):
        """
        Captures voice input after detecting the wake word.
        Listens for "Hey Drone" and then records the user's input.

        Returns:
            AudioData: The recorded audio input.
        """
        return self.listen_for_wake_word()

    def log_volume(indata: np.ndarray, frames: int, time: any, status: any):
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

    def save_audio(self, audio: sr.AudioData) -> None:
        """
        Saves audio to external .wav file

        Args:
            audio: audio data

        Returns:
            None
        """
        if not self.config.save_recordings:
            logger.debug("Saving audio disabled.")
            return

        recording_folder = file_handler.get_recordings_folder()
        file_handler.create_folder_if_not_exists(recording_folder)

        timestamp = date.timestamp_filename_safe()
        recording_name = f"recording_{timestamp}.wav"
        recording_save_path = recording_folder / recording_name

        logger.info(f"Saving audio to {recording_save_path}")
        with open(recording_save_path, c.WRITE_BINARY_MODE) as f:
            f.write(audio.get_wav_data())

        logger.info(f"Audio saved to {recording_save_path}")

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
        audio_files = file_handler.list_files_in_folder(recordings_folder, c.AUDIO_FILE_EXTENSIONS)

        if not audio_files:
            logger.info("No audio files found. Listening for new audio...")
            return self.capture_voice_input()

        most_recent_audio_file = sorted(audio_files, key=lambda x: x.stat().st_ctime, reverse=True)[0]

        logger.debug(f"Loading audio from {file_handler.relative_path(most_recent_audio_file)}")
        most_recent_audio_file = str(most_recent_audio_file)
        with sr.AudioFile(most_recent_audio_file) as source:
            audio = self.recogniser.record(source)

        logger.debug(f"Audio loaded.")
        return audio

    def convert_voice_to_text(self, audio: sr.AudioData):
        """
        Takes in the recorded audio and converts it into text.
        """
        logger.info("Converting audio to text...")

        text = None
        try:
            text = self.recogniser.recognize_google(audio)
            logger.info(f"You said: '{text}'")
        except sr.UnknownValueError:
            logger.warning("Not understood")
        except sr.RequestError as e:
            logger.error(e)

        return text
