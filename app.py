import os
from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
from utils.reel_editor import generate_reel

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "static/outputs"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    reel_url = None

    if request.method == "POST":
        video = request.files.get("video")
        music = request.files.get("music")
        style = request.form.get("style")           # e.g. "heroic", "glitch", etc.
        mood = request.form.get("mood")             # color grading category
        resolution = request.form.get("resolution") # "720p", "1080p", "1440p", "4k"

        if not video or not music:
            message = "Please upload both video and music files."
            return render_template("index.html", message=message)

        vid_fn = secure_filename(video.filename)
        mus_fn = secure_filename(music.filename)

        video_path = os.path.join(app.config['UPLOAD_FOLDER'], vid_fn)
        music_path = os.path.join(app.config['UPLOAD_FOLDER'], mus_fn)

        video.save(video_path)
        music.save(music_path)

        output_name = f"reel_{os.path.splitext(vid_fn)[0]}_{style}_{resolution}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_name)

        try:
            generate_reel(video_path, music_path, output_path, style, mood, resolution)
            message = "Reel created successfully!"
            reel_url = url_for('static', filename=f"outputs/{output_name}")
        except Exception as e:
            message = f"Error during reel generation: {e}"

    return render_template("index.html", message=message, reel=reel_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
