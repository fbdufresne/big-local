# Local BigMotion - AI Video Generator

A self-hosted, Docker-based alternative to BigMotion.ai that generates faceless short-form videos using AI. Perfect for creating content for TikTok, YouTube Shorts, and Instagram Reels.

## Features

- 🎬 **Automated Video Generation**: Create complete videos from just a topic
- 🤖 **AI Script Writing**: Uses Ollama (Llama 3.2) to generate engaging scripts
- 🎙️ **Text-to-Speech**: Automatic voiceover generation using gTTS
- 🎨 **Dynamic Visuals**: Generates gradient backgrounds with text overlays
- 📱 **Vertical Video Format**: Optimized for social media (1080x1920)
- 🌐 **Web Interface**: Easy-to-use browser-based UI
- 🐳 **Fully Dockerized**: Easy deployment with docker-compose

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB of free disk space
- 4GB RAM minimum (8GB recommended)

## Quick Start

1. **Clone or create the project directory**:
```bash
mkdir bigmotion-local
cd bigmotion-local
```

2. **Copy all the project files** (Dockerfile, docker-compose.yml, app.py, video_generator.py, etc.)

3. **Start the application**:
```bash
docker-compose up -d
```

This will:
- Build the video generation application
- Pull and start Ollama with Llama 3.2 model
- Start the web interface

4. **Wait for Ollama to download the model** (first time only, ~2-3 minutes):
```bash
docker-compose logs -f ollama
```

Wait until you see "successfully loaded model llama3.2"

5. **Access the web interface**:
Open your browser and go to: http://localhost:5000

## Usage

### Web Interface

1. Enter a topic (e.g., "5 surprising facts about the ocean")
2. Choose duration (15-90 seconds)
3. Select voice style and music preference
4. Click "Generate Video"
5. Wait 1-2 minutes for generation
6. Download your video!

### API Usage

You can also use the API directly:

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The history of pizza",
    "duration": 60,
    "voice": "default",
    "music_style": "upbeat"
  }'
```

List all generated videos:
```bash
curl http://localhost:5000/api/videos
```

Download a specific video:
```bash
curl http://localhost:5000/api/videos/<video_id> -o video.mp4
```

## Directory Structure

```
bigmotion-local/
├── docker-compose.yml      # Container orchestration
├── Dockerfile              # App container definition
├── requirements.txt        # Python dependencies
├── app.py                  # Flask web server
├── video_generator.py      # Video generation logic
├── templates/
│   └── index.html         # Web UI
├── output/                 # Generated videos (auto-created)
└── temp/                   # Temporary files (auto-created)
```

## Configuration

### Environment Variables

You can customize the application by setting environment variables in `docker-compose.yml`:

```yaml
environment:
  - OLLAMA_URL=http://ollama:11434  # Ollama API endpoint
```

### Video Settings

Default settings in the UI:
- **Duration**: 60 seconds (adjustable 15-90s)
- **Resolution**: 1080x1920 (vertical)
- **FPS**: 24
- **Format**: MP4 (H.264 video, AAC audio)

## Tips for Best Results

### Topic Ideas
- "5 mind-blowing facts about [subject]"
- "The surprising history of [topic]"
- "Why [something] is actually [opposite]"
- "Things you didn't know about [topic]"
- "The truth about [controversial topic]"

### Best Practices
- Keep videos 30-60 seconds for maximum engagement
- Use specific, curiosity-provoking topics
- Think about what would make you stop scrolling
- Front-load interesting information (first 3 seconds matter!)

## Troubleshooting

### Video generation is slow
- First generation takes longer (model loading)
- Ensure you have enough RAM (4GB minimum)
- Check CPU usage with `docker stats`

### "Connection to Ollama failed"
- Wait for Ollama to fully start: `docker-compose logs -f ollama`
- Restart services: `docker-compose restart`

### Text not appearing in videos
- This is a known limitation of MoviePy with some fonts
- The video will still generate, just without text overlays
- Audio narration still works

### Out of disk space
- Clean old videos: `rm output/*.mp4`
- Clean Docker cache: `docker system prune -a`

## Upgrading

To upgrade to the latest version:

```bash
docker-compose down
docker-compose pull
docker-compose up -d --build
```

## Stopping the Application

```bash
docker-compose down
```

To also remove generated videos and data:
```bash
docker-compose down -v
rm -rf output/* temp/*
```

## System Requirements

**Minimum**:
- 2 CPU cores
- 4GB RAM
- 10GB disk space

**Recommended**:
- 4 CPU cores
- 8GB RAM
- 20GB disk space
- SSD storage

## Limitations

This is a basic implementation compared to commercial services like BigMotion.ai:

- **No image generation**: Uses gradient backgrounds instead of AI-generated images
- **Basic TTS**: Uses Google Text-to-Speech (free but less natural than ElevenLabs)
- **No music**: Background music generation not included
- **Simple visuals**: Text overlays on gradients instead of complex animations
- **No social media integration**: Manual upload required
- **Single video at a time**: No batch processing

## Future Enhancements

Potential improvements you could add:

1. **Better visuals**: Integrate Stable Diffusion for image generation
2. **Better TTS**: Add support for Coqui TTS or other local models
3. **Background music**: Add music library or generation
4. **Social media posting**: Integrate with TikTok/YouTube APIs
5. **Batch processing**: Generate multiple videos in series
6. **Templates**: Pre-built templates for different content types
7. **Advanced editing**: Timeline editor for fine-tuning

## License

This is a personal/educational project. For commercial use, ensure compliance with all dependencies' licenses.

## Contributing

This is a basic implementation. Feel free to fork and improve it!

## Credits

Built with:
- [Ollama](https://ollama.ai/) - Local LLM inference
- [MoviePy](https://zulko.github.io/moviepy/) - Video editing
- [gTTS](https://github.com/pndurette/gTTS) - Text-to-speech
- [Flask](https://flask.palletsprojects.com/) - Web framework

---

**Disclaimer**: This is an educational project and not affiliated with BigMotion.ai. Use responsibly and respect content creation guidelines on social media platforms.
