import whisper
import tempfile
import os

def transcribe_audio(video_path):
    """
    Transcribe dialogue from video using OpenAI Whisper model.
    Returns list of (start_time, end_time, text) tuples.
    """
    model = whisper.load_model("base")  # or "small" / "medium" for better accuracy but slower

    # Extract audio from video to temp WAV
    temp_audio_path = tempfile.mktemp(suffix=".wav")
    os.system(f'ffmpeg -y -i "{video_path}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{temp_audio_path}"')

    result = model.transcribe(temp_audio_path)
    os.remove(temp_audio_path)

    segments = result.get("segments", [])
    dialogue = [(seg['start'], seg['end'], seg['text']) for seg in segments]

    return dialogue
