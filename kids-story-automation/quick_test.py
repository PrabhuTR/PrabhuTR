"""
Quick Test Script - Generate a video without n8n
Just run: python quick_test.py
"""

import os
import asyncio
import requests
from pathlib import Path
from datetime import datetime
import subprocess
import sys

# Install dependencies if needed
def check_deps():
    try:
        import edge_tts
        from moviepy.editor import ImageClip
        from PIL import Image
    except ImportError:
        print("Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'edge-tts', 'moviepy', 'pillow', 'requests'])
        print("Dependencies installed! Please run this script again.")
        sys.exit(0)

check_deps()

import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image
from io import BytesIO

# Create directories
OUTPUT_DIR = Path("./output")
TEMP_DIR = Path("./temp")
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)


async def generate_voice(text, path):
    """Generate voice using free Microsoft Edge TTS"""
    voice = "en-US-AnaNeural"  # Cheerful young voice
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)


def download_image(prompt, path):
    """Download AI image from Pollinations (free)"""
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1280&height=720"
    print(f"Generating image: {prompt[:50]}...")

    for _ in range(3):
        try:
            resp = requests.get(url, timeout=60)
            if resp.status_code == 200:
                img = Image.open(BytesIO(resp.content))
                img = img.convert('RGB').resize((1280, 720))
                img.save(path)
                return True
        except Exception as e:
            print(f"Retry: {e}")

    # Fallback: create colored placeholder
    Image.new('RGB', (1280, 720), (135, 206, 235)).save(path)
    return False


def create_video():
    """Create a complete kids story video"""

    # Sample story - you can modify this!
    story = {
        "title": "The Friendly Cloud",
        "scenes": [
            {
                "text": "High up in the blue sky, there lived a fluffy white cloud named Cloudy.",
                "image": "cute cartoon white fluffy cloud with a happy smiling face in blue sky, children book illustration, bright and colorful"
            },
            {
                "text": "Cloudy loved to float around and watch the children play below.",
                "image": "cartoon happy cloud floating over a playground with children playing, sunny day, kids illustration style"
            },
            {
                "text": "One hot summer day, the flowers in the garden were very thirsty.",
                "image": "cartoon wilting sad flowers in a garden under hot sun, children book style, cute faces on flowers"
            },
            {
                "text": "Cloudy had an idea! He took a deep breath and made gentle rain fall down.",
                "image": "cartoon smiling cloud making colorful rain drops fall on happy flowers, rainbow appearing, kids illustration"
            },
            {
                "text": "The flowers were so happy! Remember, helping others makes everyone smile. The End!",
                "image": "happy cartoon cloud with blooming colorful flowers below, rainbow in sky, text The End, children book illustration"
            }
        ]
    }

    print(f"\n{'='*50}")
    print(f"Creating: {story['title']}")
    print(f"{'='*50}\n")

    clips = []

    for i, scene in enumerate(story['scenes']):
        print(f"\nScene {i+1}/{len(story['scenes'])}")

        # Generate image
        img_path = TEMP_DIR / f"scene_{i}.jpg"
        download_image(scene['image'], str(img_path))

        # Generate voiceover
        audio_path = TEMP_DIR / f"audio_{i}.mp3"
        print(f"Generating voiceover...")
        asyncio.run(generate_voice(scene['text'], str(audio_path)))

        # Create video clip
        audio = AudioFileClip(str(audio_path))
        duration = audio.duration + 1.5  # Pause after narration

        clip = ImageClip(str(img_path)).set_duration(duration)
        clip = clip.set_audio(audio)
        clips.append(clip)

    # Combine all clips
    print("\nCombining scenes...")
    final = concatenate_videoclips(clips, method="compose")

    # Output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"kids_story_{timestamp}.mp4"

    print(f"Rendering video...")
    final.write_videofile(
        str(output_path),
        fps=24,
        codec='libx264',
        audio_codec='aac',
        verbose=False,
        logger=None
    )

    # Cleanup
    for f in TEMP_DIR.glob("*"):
        f.unlink()

    print(f"\n{'='*50}")
    print(f"VIDEO CREATED!")
    print(f"Location: {output_path.absolute()}")
    print(f"{'='*50}\n")

    return str(output_path)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════╗
    ║   Kids Story Video Generator - Test    ║
    ║   100% FREE - No API keys needed!      ║
    ╚════════════════════════════════════════╝
    """)

    try:
        video_path = create_video()
        print(f"Open the video: {video_path}")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure FFmpeg is installed:")
        print("  Windows: winget install ffmpeg")
        print("  Mac: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
