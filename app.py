from flask import Flask, render_template, request, session, redirect, url_for
from main import predict_voice
from moviepy.editor import VideoFileClip
import os
import uuid
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this-123456"  # Change this!

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store analysis history (in production use database)
HISTORY_FILE = "analysis_history.json"

def save_to_history(filename, result, confidence, file_type, file_size):
    """Save analysis to history"""
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    
    history.append({
        'id': str(uuid.uuid4()),
        'filename': filename,
        'result': result,
        'confidence': confidence,
        'file_type': file_type,
        'file_size': file_size,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Keep last 50 records
    history = history[-50:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return redirect(url_for("index"))
    
    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index"))
    
    # Save file
    original_filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{file.filename}")
    file.save(file_path)
    
    # Get file size
    file_size = os.path.getsize(file_path) / 1024  # KB
    
    # Video support
    file_type = "audio"
    if file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        file_type = "video"
        video = VideoFileClip(file_path)
        audio_path = file_path.rsplit('.', 1)[0] + ".wav"
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        file_path = audio_path
    
    # Prediction
    prediction, confidence = predict_voice(file_path)
    confidence_percent = max(confidence[0]) * 100
    confidence_score = round(confidence_percent, 2)
    
    # Determine result class
    result_class = "real" if prediction == "REAL VOICE" else "fake"
    
    # Save to history
    save_to_history(original_filename, prediction, confidence_score, file_type, round(file_size, 2))
    
    # Store in session for result page
    session['analysis_result'] = {
        'filename': original_filename,
        'result': prediction,
        'confidence': confidence_score,
        'result_class': result_class,
        'file_type': file_type,
        'file_size': round(file_size, 2),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Clean up files
    try:
        os.remove(file_path)
        if file_type == "video" and os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass
    
    return redirect(url_for("result"))

@app.route("/result")
def result():
    if 'analysis_result' not in session:
        return redirect(url_for("index"))
    
    result_data = session.pop('analysis_result')
    return render_template("result.html", result=result_data)

@app.route("/history")
def history():
    history_data = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history_data = json.load(f)
    
    # Reverse for latest first
    history_data.reverse()
    return render_template("history.html", history=history_data)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)