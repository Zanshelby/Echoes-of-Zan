import librosa
import numpy as np

def detect_beats(audio_path):
    """
    Detect beats in audio file using librosa.
    Returns list of beat timestamps in seconds.
    """
    y, sr = librosa.load(audio_path, sr=None)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    return beat_times.tolist()
