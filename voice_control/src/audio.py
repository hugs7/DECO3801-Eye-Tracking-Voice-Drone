"""
Module for audio processing.
"""

from typing import Optional, Dict
import pathlib

import numpy as np
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
from omegaconf import OmegaConf

from common.logger_helper import init_logger
from common.file_handler import get_file_extension
from common import network

from . import constants as c
from . import file_handler
from . import date

logger = init_logger()


class AudioRecogniser:
    """
    Class to handle voice recognition and audio processing.
    """

    def __init__(self, audio_config: OmegaConf):
        """
        Initialises the AudioRecogniser.

        Args:
            audio_config (OmegaConf): The audio configuration settings.
        """

        self.recogniser = sr.Recognizer()
        self.config = audio_config

        # Assume microphone is available by default
        self.microphone_available = True
        self.check_network_connection()

        self.wake_command = self.config.wake_command
        self.enable_sound_effects = self.config.sound_effects.enable
        self.sound_effects: Dict[str, AudioSegment] = {}

        self.__load_sounds()

    def check_network_connection(self) -> bool:
        """
        Checks if an internet connection is available.

        Args:
            None

        Returns:
            bool: True if an internet connection is available, False otherwise.
        """
        self.network_available = network.check_internet_connection()

    def __load_sounds(self):
        """
        Load sound files for wake word detection and other audio processing.

        Args:
            None

        Returns:
            None
        """
        assets_folder = file_handler.get_assets_folder()
        sound_effects_map = self.config.sound_effects.files

        for sound_name, sound_file in sound_effects_map.items():
            sound_file_path: pathlib.Path = assets_folder / sound_file
            segment = self.load_audio_segment(sound_file_path)
            self.sound_effects[sound_name] = segment

    def _detect_wake_word(self, audio: Optional[sr.AudioData]) -> bool:
        """
        Detects the wake word (defined in config) in the audio data.

        Args:
            audio (Optional[sr.AudioData]): The audio data to check for the wake word or None if no audio is provided.

        Returns:
            bool: True if the wake word is detected, False otherwise.
        """

        if not audio:
            return False

        command = self.convert_voice_to_text(audio)
        if not command:
            return False

        wake_word_detected = self.wake_command.lower() in command.lower()

        if wake_word_detected:
            logger.info("Wake word detected: '%s'", self.wake_command)
            self.play_sound_effect("wake")
        else:
            logger.info("Not the wake word: '%s'", command)

        return wake_word_detected

    def _listen_until_silence(self, source: sr.Microphone):
        """
        Listens to the user's voice until they stop speaking.
        Uses a combination of timeouts and silence detection to end listening.

        Args:
            source (sr.Microphone): The microphone input source.

        Returns:
            AudioData: The recorded audio input.
        """
        logger.info("Listening for user input...")

        try:
            audio = self.listen_for_audio(
                source, True, self.config.listen_timeout)
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out.")
            self.play_sound_effect("reject")
            return None

        if audio is not None:
            self.play_sound_effect("accept")

        return audio

    def listen_for_audio(self, source: Optional[sr.Microphone] = None, save: bool = False, timeout: Optional[int] = None) -> sr.AudioData:
        """
        Listens for audio input from the microphone.

        Args:
            source (sr.Microphone): The microphone input source. If None, a new microphone source is created.
            save (bool): Whether to save the recorded audio to a file.
            timeout (int): The maximum time to listen for audio input.

        Returns:
            AudioData: The recorded audio input.
        """

        if timeout is None:
            logger.debug("No timeout set. Listening indefinitely.")

        def listen_callback(source: sr.Microphone) -> sr.AudioData:
            logger.info("    >>> Listening for audio...")
            # Adjust for ambient noise to improve speech detection
            self.recogniser.adjust_for_ambient_noise(
                source, self.config.ambient_noise_duration)
            audio = self.recogniser.listen(
                source, timeout, phrase_time_limit=self.config.phrase_time_limit)

            if audio is not None:
                logger.info("    <<< Finished listening.")

            return audio

        if source:
            audio = listen_callback(source)
        else:
            try:
                with sr.Microphone() as source:
                    audio = listen_callback(source)
            except OSError as e:
                self.__handle_microphone_error(e)
                return None

        if save:
            self.save_audio(audio)

        return audio

    def capture_voice_input(self) -> Optional[sr.AudioData]:
        """
        Listens continuously for the wake word defined in config.
        Once the wake word is detected, it listens continuously until the user stops speaking.

        Args:
            None

        Returns:
            Optional[AudioData]: AudioData object containing the recorded audio after wake
                                 word is detected. None if the microphone is not available
                                 or an error occurs.
        """

        if not self.microphone_available:
            logger.debug("Microphone not available.")
            return None

        try:
            with sr.Microphone() as source:
                logger.info("Listening for wake word...")

                audio = self.listen_for_audio(source, False, None)
                if self._detect_wake_word(audio):
                    logger.info(
                        "Wake word detected, listening for commands...")
                    return self._listen_until_silence(source)
        except OSError as e:
            self.__handle_microphone_error(e)

    def convert_voice_to_text(self, audio: sr.AudioData) -> Optional[str]:
        """
        Takes in the recorded audio and converts it into text.

        Args:
            audio (AudioData): The recorded audio input.

        Returns:
            str: The text output from the audio input.
        """

        if not self.network_available:
            logger.warning(
                "No internet connection. Cannot convert audio to text.")
            return None

        text = None
        logger.info("Converting audio to text...")

        try:
            text = self.recogniser.recognize_google(audio)
            logger.info("You said: '%s'", text)
        except sr.UnknownValueError:
            logger.debug("No speech detected.")
        except sr.RequestError as e:
            logger.error("Error converting voice to command. Details: %s", e)

        return text

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

        logger.info("Saving audio to %s", recording_save_path)
        with open(recording_save_path, c.WRITE_BINARY_MODE) as f:
            f.write(audio.get_wav_data())

        logger.info("Audio saved to %s", recording_save_path)

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

        audio = self.load_audio_file(str(most_recent_audio_file))
        return audio

    def load_audio_file(self, file_path: str) -> sr.AudioData:
        """
        Loads audio file from specified path.

        Args:
            file_path: path to audio file as string

        Returns:
            AudioData: An AudioData object containing the recorded audio input.
        """
        logger.info("Loading audio from %s", file_path)
        with sr.AudioFile(file_path) as source:
            audio = self.recogniser.record(source)

        logger.debug("Audio loaded.")
        return audio

    def load_audio_segment(self, file_path: pathlib.Path) -> AudioSegment:
        """
        Loads audio file from specified path.

        Args:
            file_path: path to audio file as pathlib.Path

        Returns:
            AudioSegment: An AudioSegment object containing the recorded audio input.
        """

        if not file_path.exists():
            logger.error("Sound file not found: %s", file_path)
            return None

        str_file_path = str(file_path)
        logger.debug("Loading sound file: %s", file_path)
        try:
            extension = get_file_extension(file_path, True)
            logger.debug("Audio format: %s", extension)
            segment = AudioSegment.from_file(str_file_path, format=extension)
        except Exception as e:
            logger.error(
                "Error loading sound file: %s. Check you have ffmpeg installed and on $PATH.", str_file_path)
            logger.error(
                "In CMD: 'where ffmpeg' should return the path to ffmpeg.exe")
            logger.error(e)
            segment = None

        return segment

    def play_sound_effect(self, sound_name: str):
        """
        Plays a sound effect from the sound_effects folder.

        Args:
            sound_name (str): The name of the sound effect to play.

        Returns:
            None
        """
        if not self.enable_sound_effects:
            logger.debug("Sound effects disabled.")
            return

        sound = self.sound_effects.get(sound_name)
        if sound:
            logger.info("Playing sound effect: %s", sound_name)
            play(sound)
        else:
            logger.error("Sound effect not found: %s",  sound_name)

    def __handle_microphone_error(self, e: Exception):
        """
        Handles microphone errors by logging the error and playing a sound effect.

        Args:
            e (Exception): The exception raised by the microphone.

        Returns:
            None
        """
        logger.error("Error accessing microphone. Details: %s", e)
        self.microphone_available = False

    def log_volume(self, indata: np.ndarray, frames: int, time: any, status: any):
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
        logger.info("Microphone Volume: %d", volume_norm)
