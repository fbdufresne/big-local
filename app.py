import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import tempfile
from video_generator import VideoGenerator
import logging

VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1080"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1920"))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "30"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
TTS_VOICE = os.getenv("TTS_VOICE", "en")

logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))



app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Create necessary directories
OUTPUT_DIR = Path("/app/output")
OUTPUT_DIR.mkdir(exist_ok=True)

TEMP_DIR = Path("/app/temp")
TEMP_DIR.mkdir(exist_ok=True)
app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


video_gen = VideoGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """Generate a video based on user input"""
    try:
        data = request.json
        topic = data.get('topic', '')
        duration = int(data.get('duration', 60))
        voice = data.get('voice', 'default')
        music_style = data.get('music_style', 'upbeat')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Generate the video
        video_path = video_gen.create_video(
            topic=topic,
            duration=duration,
            voice=voice,
            music_style=music_style
        )
        
        return jsonify({
            'success': True,
            'video_id': Path(video_path).name,
            'message': 'Video generated successfully!'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<video_id>')
def get_video(video_id):
    """Serve a generated video"""
    video_path = OUTPUT_DIR / video_id
    
    if not video_path.exists():
        return jsonify({'error': 'Video not found'}), 404
    
    return send_file(video_path, mimetype='video/mp4')

@app.route('/api/videos')
def list_videos():
    """List all generated videos"""
    videos = []
    for video_file in OUTPUT_DIR.glob('*.mp4'):
        videos.append({
            'id': video_file.name,
            'created': video_file.stat().st_mtime
        })
    
    videos.sort(key=lambda x: x['created'], reverse=True)
    return jsonify({'videos': videos})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
