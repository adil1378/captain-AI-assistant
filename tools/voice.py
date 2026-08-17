import subprocess
import io
from typing import Optional
from loguru import logger


def speak_text(text: str):
    """
    Direct in-memory Text-to-Speech audio output using professional English voice.
    Synthesizes and speaks text directly through the sound card.
    CREATES ZERO FILES ON DISK.
    """
    if not text:
        return

    # Clean markdown and symbols for clear speech
    clean = (
        text.replace("#", "")
        .replace("*", "")
        .replace("`", "")
        .replace("###", "")
        .replace("- ", "")
        .replace("• ", "")
        .strip()
    )
    if not clean:
        return

    clean_speech = clean[:400]

    # Method 1: Professional English pyttsx3 SAPI5 voice engine
    try:
        import pyttsx3
        engine = pyttsx3.init('sapi5')
        engine.setProperty('rate', 165)
        engine.setProperty('volume', 1.0)
        
        voices = engine.getProperty('voices')
        friendly_voice_names = ["david", "guy", "mark", "george", "christopher", "eric", "liam", "alex", "daniel"]
        selected_voice = None
        for name in friendly_voice_names:
            for v in voices:
                if name in v.name.lower():
                    selected_voice = v.id
                    break
            if selected_voice:
                break
        if selected_voice:
            engine.setProperty('voice', selected_voice)

        engine.say(clean_speech)
        engine.runAndWait()
        return
    except Exception as e:
        logger.warning(f"pyttsx3 speech failed: {e}")

    # Method 2: Professional In-memory PowerShell SAPI5 Synthesizer
    try:
        escaped_text = clean_speech.replace("'", " ").replace('"', ' ').replace("\n", " ")
        ps_cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Rate = 0; $synth.Speak(\'{escaped_text}\')"'
        subprocess.run(ps_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"In-memory PowerShell speech error: {e}")


def listen_to_speech(duration: int = 5) -> Optional[str]:
    """
    Record microphone audio directly in RAM and convert speech to text (STT).
    Understands Hindi (hi-IN), Urdu (ur-PK), and English (en-IN/en-US).
    CREATES ZERO FILES ON DISK.
    """
    try:
        import sounddevice as sd
        import speech_recognition as sr
        import wave

        sample_rate = 16000
        logger.info(f"Listening for microphone audio ({duration}s)...")
        
        # Record microphone audio directly into RAM buffer
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()

        # In-memory WAV buffer (RAM only, zero files on disk)
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())

        wav_io.seek(0)

        # Transcribe directly from in-memory BytesIO WAV buffer
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            recorded_audio = recognizer.record(source)

        text = None
        for language in ["en-IN", "hi-IN", "ur-PK", "en-US"]:
            try:
                text = recognizer.recognize_google(recorded_audio, language=language)
                if text:
                    break
            except Exception:
                continue

        if text:
            logger.info(f"Speech Recognized: '{text}'")
            return text
        else:
            logger.warning("No speech transcribed.")
            return None

    except Exception as e:
        logger.error(f"Speech recognition error: {e}")
        return None
