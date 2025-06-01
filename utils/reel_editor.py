import os
import subprocess
from .audio_transcriber import transcribe_audio
from .beat_sync import detect_beats
from .color_grading import get_color_filter

RESOLUTIONS = {
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4k": (3840, 2160),
}

def generate_reel(video_path, music_path, output_path, style, mood, resolution):
    """
    Core reel generator function.
    1. Transcribes dialogue from video.
    2. Detects beat timestamps from music.
    3. Applies glow captions with timing.
    4. Applies beat-synced zoom/shake/glitch effects based on style.
    5. Applies color grading.
    6. Resizes video to selected resolution & formats to vertical 9:16.
    7. Mixes music and video audio.
    8. Saves output file.
    """

    width, height = RESOLUTIONS.get(resolution, (1920, 1080))

    # Step 1: Transcribe dialogue
    print("[*] Transcribing dialogue...")
    captions = transcribe_audio(video_path)  # list of (start, end, text)

    # Step 2: Beat detection
    print("[*] Detecting beats...")
    beats = detect_beats(music_path)  # list of beat timestamps

    # Step 3: Prepare subtitles file for glow captions
    subtitle_path = output_path.replace(".mp4", ".ass")
    generate_ass_subtitles(subtitle_path, captions)

    # Step 4: Compose FFmpeg filter complex

    glow_filter = "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:" \
                  "text='%{eif\\:n\\:d}':" \
                  "fontsize=48:fontcolor=white:shadowcolor=magenta:shadowx=2:shadowy=2:" \
                  "x=(w-text_w)/2:y=h-150:enable='between(t,0,20)',"

    color_filter = get_color_filter(mood)

    # Zoom & shake effect synced with beats, sample example for "glitch" style:
    if style == "glitch":
        # Zoom + shake around beat timestamps
        zoom_shake_filter = generate_beat_synced_filter(beats, width, height)
    else:
        zoom_shake_filter = ""

    # Base scale + pad to 9:16 (vertical)
    scale_pad_filter = f"scale={width}:-2,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"

    # Compose full filter
    filters = []
    if color_filter:
        filters.append(color_filter)
    if zoom_shake_filter:
        filters.append(zoom_shake_filter)
    filters.append(scale_pad_filter)

    filter_complex = ",".join(filters)

    # Step 5: Run FFmpeg command

    # Command: overlay subtitles + apply filters + add audio music mix

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", music_path,
        "-vf", f"ass={subtitle_path},{filter_complex}",
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    print("[*] Running FFmpeg...")
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr.decode()}")
    print("[*] Reel generated:", output_path)


def generate_ass_subtitles(ass_path, captions):
    """
    Generate .ass subtitle file with glow/fade slide effect for captions.
    """
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("""[Script Info]
Title: Echoes of Zan Captions
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,48,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,1,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
        for start, end, text in captions:
            start_ass = seconds_to_ass_time(start)
            end_ass = seconds_to_ass_time(end)
            glow_text = text.replace("{", "\\{").replace("}", "\\}")
            f.write(f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{glow_text}\n")


def seconds_to_ass_time(sec):
    """
    Convert seconds to ASS subtitle time format: H:MM:SS.cs
    """
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec - int(sec)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def generate_beat_synced_filter(beats, width, height):
    """
    Create a zoom & shake FFmpeg filter synced to beat timestamps.

    This is a simplified example: zoom in slightly at beat times.
    """

    # For demonstration, create a zoom expression that zooms on beat
    # (You can expand this logic to add glitch and shake effects)

    zoom_expr = "if(between(t,0,5),1+0.05*sin(2*PI*t*10),1)"
    # This dummy example does simple periodic zoom effect in first 5 seconds

    # Full filter example:
    return f"zoompan=z='{zoom_expr}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
