import os
import uuid
import json
from pathlib import Path
from datetime import datetime
import requests
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, 
    TextClip, concatenate_videoclips, CompositeAudioClip
)
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class VideoGenerator:
    def __init__(self):
        self.output_dir = Path("/app/output")
        self.temp_dir = Path("/app/temp")
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://ollama:11434')
        
    def create_video(self, topic, duration=60, voice='default', music_style='upbeat'):
        """Main method to create a video"""
        print(f"Starting video generation for topic: {topic}")
        
        # Generate script using Ollama
        script = self._generate_script(topic, duration)
        print(f"Generated script: {script[:100]}...")
        
        # Break script into scenes
        scenes = self._break_into_scenes(script, duration)
        print(f"Created {len(scenes)} scenes")
        
        # Generate voiceover
        audio_path = self._generate_voiceover(script)
        print(f"Generated voiceover: {audio_path}")
        
        # Generate images for each scene
        video_clips = []
        for i, scene in enumerate(scenes):
            print(f"Creating scene {i+1}/{len(scenes)}")
            image_path = self._generate_scene_image(scene, i)
            clip = self._create_scene_clip(image_path, scene, duration / len(scenes))
            video_clips.append(clip)
        
        # Combine everything
        final_video = self._compose_final_video(video_clips, audio_path, script)
        
        # Export
        video_id = f"{uuid.uuid4()}.mp4"
        output_path = self.output_dir / video_id
        
        print(f"Exporting final video to {output_path}")
        final_video.write_videofile(
            str(output_path),
            fps=24,
            codec='libx264',
            audio_codec='aac',
            preset='medium'
        )
        
        # Cleanup
        final_video.close()
        
        return str(output_path)
    
    def _generate_script(self, topic, duration):
        """Generate a script using Ollama"""
        try:
            prompt = f"""Create a {duration}-second video script about: {topic}

Requirements:
- Write an engaging, viral-worthy script
- Make it perfect for social media (TikTok, YouTube Shorts, Instagram Reels)
- Include hooks in the first 3 seconds
- Keep sentences short and punchy
- End with a call to action
- Word count should match approximately {duration * 2.5} words (2.5 words per second)

Write ONLY the script text, no labels or formatting."""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['response'].strip()
            else:
                return f"Did you know that {topic} is absolutely fascinating? Let me tell you why this matters and why you should care about it today."
                
        except Exception as e:
            print(f"Error generating script with Ollama: {e}")
            return f"Did you know that {topic} is absolutely fascinating? Let me tell you why this matters and why you should care about it today."
    
    def _break_into_scenes(self, script, duration):
        """Break script into scenes"""
        sentences = script.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Aim for 3-5 second scenes
        target_scenes = max(3, int(duration / 4))
        scenes_per_sentence = max(1, len(sentences) // target_scenes)
        
        scenes = []
        for i in range(0, len(sentences), scenes_per_sentence):
            scene_text = ' '.join(sentences[i:i+scenes_per_sentence])
            if scene_text:
                scenes.append(scene_text)
        
        return scenes[:target_scenes] if len(scenes) > target_scenes else scenes
    
    def _generate_voiceover(self, text):
        """Generate voiceover using gTTS"""
        audio_path = self.temp_dir / f"audio_{uuid.uuid4()}.mp3"
        
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(str(audio_path))
        
        return audio_path
    
    def _generate_scene_image(self, scene_text, scene_num):
        """Generate a simple gradient image with text overlay"""
        # Create gradient background
        width, height = 1080, 1920  # Vertical video format
        
        # Generate color based on scene number
        colors = [
            [(255, 107, 107), (255, 193, 7)],   # Red to Yellow
            [(74, 144, 226), (80, 227, 194)],   # Blue to Teal
            [(167, 112, 239), (247, 187, 151)], # Purple to Peach
            [(52, 211, 153), (88, 80, 236)],    # Green to Blue
            [(251, 146, 60), (239, 68, 68)]     # Orange to Red
        ]
        
        color_pair = colors[scene_num % len(colors)]
        
        # Create gradient
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        for y in range(height):
            ratio = y / height
            r = int(color_pair[0][0] * (1 - ratio) + color_pair[1][0] * ratio)
            g = int(color_pair[0][1] * (1 - ratio) + color_pair[1][1] * ratio)
            b = int(color_pair[0][2] * (1 - ratio) + color_pair[1][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add decorative shapes
        for _ in range(5):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            size = np.random.randint(50, 200)
            opacity = np.random.randint(20, 60)
            
            circle = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            circle_draw = ImageDraw.Draw(circle)
            circle_draw.ellipse(
                [x - size, y - size, x + size, y + size],
                fill=(255, 255, 255, opacity)
            )
            image = Image.alpha_composite(image.convert('RGBA'), circle).convert('RGB')
        
        # Save image
        image_path = self.temp_dir / f"scene_{scene_num}_{uuid.uuid4()}.png"
        image.save(image_path)
        
        return image_path
    
    def _create_scene_clip(self, image_path, scene_text, duration):
        """Create a video clip from an image with text overlay"""
        # Load image
        img_clip = ImageClip(str(image_path)).set_duration(duration)
        
        # Create text overlay with word wrapping
        words = scene_text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 30:  # Wrap at ~30 chars
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        text = '\n'.join(lines)
        
        # Create text clip
        try:
            txt_clip = TextClip(
                text,
                fontsize=70,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=3,
                method='caption',
                size=(900, None),
                align='center'
            ).set_duration(duration).set_position('center')
            
            # Composite
            video = CompositeVideoClip([img_clip, txt_clip])
        except Exception as e:
            print(f"Error creating text clip: {e}, using image only")
            video = img_clip
        
        return video
    
    def _compose_final_video(self, video_clips, audio_path, script):
        """Compose final video with all scenes and audio"""
        # Concatenate all scene clips
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Add audio
        audio = AudioFileClip(str(audio_path))
        
        # Trim video to audio length or vice versa
        if final_video.duration > audio.duration:
            final_video = final_video.subclip(0, audio.duration)
        else:
            audio = audio.subclip(0, final_video.duration)
        
        final_video = final_video.set_audio(audio)
        
        return final_video


if __name__ == "__main__":
    # Test the video generator
    gen = VideoGenerator()
    video_path = gen.create_video(
        topic="The surprising history of pizza",
        duration=30
    )
    print(f"Video created: {video_path}")
