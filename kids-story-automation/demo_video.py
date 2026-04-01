"""
DEMO: Kids Story Video Generator
Run this to see a sample video with:
- Opening intro animation
- Professional thumbnail
- Voice narration
- Moral story

Usage: python demo_video.py
"""

import os
import sys
import asyncio
import requests
from pathlib import Path
from datetime import datetime
import random
import subprocess

# Install dependencies
def install_deps():
    deps = ['edge-tts', 'moviepy', 'pillow', 'requests']
    for dep in deps:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)

print("Checking dependencies...")
install_deps()

import edge_tts
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips,
    CompositeVideoClip, ColorClip
)
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Configuration
OUTPUT_DIR = Path("./demo_output")
TEMP_DIR = Path("./temp")
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Voice configuration
VOICE = "en-US-AnaNeural"  # Cheerful kid-friendly voice


async def generate_voice(text, path):
    """Generate voice using Edge-TTS (FREE)"""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(path)


def download_image(prompt, path, retries=3):
    """Download AI image from Pollinations (FREE)"""
    safe_prompt = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1280&height=720&seed={random.randint(1, 9999)}"

    print(f"  Generating: {prompt[:50]}...")

    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=120)
            if resp.status_code == 200:
                img = Image.open(BytesIO(resp.content))
                img = img.convert('RGB').resize((1280, 720), Image.Resampling.LANCZOS)
                img.save(path)
                return True
        except Exception as e:
            print(f"  Retry {attempt + 1}: {e}")

    # Fallback gradient
    img = Image.new('RGB', (1280, 720), (135, 206, 250))
    img.save(path)
    return False


def create_opening_intro(title, moral, output_path):
    """Create beautiful opening intro image"""
    # Create gradient background (sky blue to pink)
    img = Image.new('RGB', (1280, 720), (135, 206, 250))
    draw = ImageDraw.Draw(img)

    # Add gradient effect
    for y in range(720):
        r = int(135 + (255 - 135) * y / 720)
        g = int(206 + (182 - 206) * y / 720)
        b = int(250 + (193 - 250) * y / 720)
        draw.line([(0, y), (1280, y)], fill=(r, g, b))

    # Add decorative elements (simple shapes)
    # Stars
    for _ in range(20):
        x, y = random.randint(50, 1230), random.randint(50, 300)
        size = random.randint(3, 8)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=(255, 255, 200))

    # Add text (centered)
    try:
        # Try to use a font, fallback to default
        title_y = 280
        draw.text((640, title_y), "✨ Story Time ✨", fill=(255, 255, 255), anchor="mm")
        draw.text((640, title_y + 80), title, fill=(70, 50, 120), anchor="mm")
        draw.text((640, title_y + 160), f"Moral: {moral}", fill=(100, 80, 150), anchor="mm")
        draw.text((640, 650), "For Kids 4+ Years", fill=(150, 100, 180), anchor="mm")
    except:
        pass

    img.save(output_path)
    print(f"  Created opening intro: {output_path}")
    return output_path


def create_thumbnail(title, moral, output_path):
    """Create eye-catching YouTube thumbnail"""
    # Download a cute background image
    bg_prompt = "colorful cartoon background with rainbow stars sparkles cute children illustration bright colors no text"
    bg_path = TEMP_DIR / "thumb_bg.jpg"
    download_image(bg_prompt, str(bg_path))

    # Open and enhance
    img = Image.open(bg_path)
    img = img.resize((1280, 720), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)

    # Add semi-transparent overlay for text readability
    overlay = Image.new('RGBA', (1280, 720), (0, 0, 0, 100))
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.convert('RGB')
    draw = ImageDraw.Draw(img)

    # Add eye-catching elements
    # Title banner
    draw.rectangle([40, 250, 1240, 470], fill=(255, 100, 100), outline=(255, 255, 255), width=5)

    # Text
    try:
        draw.text((640, 310), "NEW STORY!", fill=(255, 255, 0), anchor="mm")
        draw.text((640, 400), title[:30], fill=(255, 255, 255), anchor="mm")
        draw.text((640, 550), "4+ MORAL STORY", fill=(255, 220, 100), anchor="mm")
        draw.text((640, 650), "▶ WATCH NOW", fill=(0, 255, 0), anchor="mm")
    except:
        pass

    img.save(output_path)
    print(f"  Created thumbnail: {output_path}")
    return output_path


def create_ending_card(moral, output_path):
    """Create ending card with moral"""
    img = Image.new('RGB', (1280, 720), (70, 50, 120))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(720):
        r = int(70 + (100 - 70) * y / 720)
        g = int(50 + (80 - 50) * y / 720)
        b = int(120 + (180 - 120) * y / 720)
        draw.line([(0, y), (1280, y)], fill=(r, g, b))

    # Add stars
    for _ in range(30):
        x, y = random.randint(50, 1230), random.randint(50, 670)
        size = random.randint(2, 6)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=(255, 255, 200))

    try:
        draw.text((640, 200), "🌟 THE END 🌟", fill=(255, 215, 0), anchor="mm")
        draw.text((640, 350), "Today's Moral:", fill=(200, 200, 255), anchor="mm")
        draw.text((640, 450), moral, fill=(255, 255, 255), anchor="mm")
        draw.text((640, 600), "👍 Like & Subscribe for more stories!", fill=(100, 255, 100), anchor="mm")
    except:
        pass

    img.save(output_path)
    return output_path


def create_demo_video():
    """Create a complete demo video"""

    # Demo story with moral
    story = {
        "title": "The Kind Little Elephant",
        "moral": "Kindness makes everyone happy!",
        "scenes": [
            {
                "narration": "Once upon a time, in a sunny jungle, there lived a little elephant named Ellie. She had big floppy ears and a very kind heart.",
                "image_prompt": "cute cartoon baby elephant with big ears smiling in sunny jungle, bright colors, children book illustration style"
            },
            {
                "narration": "One day, Ellie saw a tiny bird who had fallen from its nest. The little bird was crying and looking very sad.",
                "image_prompt": "cartoon baby elephant looking at small sad bird on ground, jungle background, cute children illustration"
            },
            {
                "narration": "Don't worry little friend! said Ellie. I will help you! She gently lifted the bird with her trunk.",
                "image_prompt": "friendly cartoon elephant carefully lifting small bird with trunk, gentle caring scene, kids cartoon style"
            },
            {
                "narration": "Ellie carefully placed the bird back in its cozy nest high up in the tree. The bird's family was so happy!",
                "image_prompt": "cartoon elephant putting bird in nest in tree, happy bird family, colorful jungle scene, children illustration"
            },
            {
                "narration": "The birds sang a beautiful thank you song for Ellie. All the jungle animals cheered for her kindness!",
                "image_prompt": "happy cartoon elephant surrounded by singing birds and cheering animals, celebration scene, bright colorful kids art"
            },
            {
                "narration": "From that day on, Ellie made many friends in the jungle. Remember children, being kind to others makes everyone happy! The End!",
                "image_prompt": "cartoon elephant with many animal friends smiling together, rainbow background, happy ending scene, THE END text"
            }
        ]
    }

    title = story["title"]
    moral = story["moral"]
    scenes = story["scenes"]

    print(f"\n{'='*60}")
    print(f"DEMO: Creating Kids Story Video")
    print(f"Title: {title}")
    print(f"Moral: {moral}")
    print(f"Scenes: {len(scenes)}")
    print(f"{'='*60}\n")

    clips = []

    # 1. Create Opening Intro (3 seconds)
    print("\n[1/4] Creating opening intro...")
    intro_img_path = TEMP_DIR / "intro.jpg"
    create_opening_intro(title, moral, str(intro_img_path))

    intro_audio_path = TEMP_DIR / "intro_audio.mp3"
    intro_text = f"Welcome to Story Time! Today's story is: {title}. A beautiful moral story for children!"
    asyncio.run(generate_voice(intro_text, str(intro_audio_path)))

    intro_audio = AudioFileClip(str(intro_audio_path))
    intro_clip = ImageClip(str(intro_img_path)).set_duration(intro_audio.duration + 1).set_audio(intro_audio)
    clips.append(intro_clip)

    # 2. Create Thumbnail (save separately)
    print("\n[2/4] Creating thumbnail...")
    thumbnail_path = OUTPUT_DIR / "thumbnail.jpg"
    create_thumbnail(title, moral, str(thumbnail_path))

    # 3. Process story scenes
    print(f"\n[3/4] Creating {len(scenes)} story scenes...")
    for i, scene in enumerate(scenes):
        print(f"\n  Scene {i+1}/{len(scenes)}")

        # Download image
        img_path = TEMP_DIR / f"scene_{i}.jpg"
        download_image(scene['image_prompt'], str(img_path))

        # Generate voice
        audio_path = TEMP_DIR / f"audio_{i}.mp3"
        asyncio.run(generate_voice(scene['narration'], str(audio_path)))

        # Create clip
        audio = AudioFileClip(str(audio_path))
        duration = audio.duration + 1.5

        clip = ImageClip(str(img_path)).set_duration(duration).set_audio(audio)
        clips.append(clip)

    # 4. Create ending card
    print("\n[4/4] Creating ending card...")
    ending_img_path = TEMP_DIR / "ending.jpg"
    create_ending_card(moral, str(ending_img_path))

    ending_audio_path = TEMP_DIR / "ending_audio.mp3"
    ending_text = f"And that's the end of our story! Remember children: {moral} Please like and subscribe for more wonderful stories. See you next time!"
    asyncio.run(generate_voice(ending_text, str(ending_audio_path)))

    ending_audio = AudioFileClip(str(ending_audio_path))
    ending_clip = ImageClip(str(ending_img_path)).set_duration(ending_audio.duration + 2).set_audio(ending_audio)
    clips.append(ending_clip)

    # Combine all clips
    print("\n Combining all clips...")
    final = concatenate_videoclips(clips, method="compose")

    # Output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = OUTPUT_DIR / f"demo_story_{timestamp}.mp4"

    print(f"\n Rendering video...")
    final.write_videofile(
        str(video_path),
        fps=24,
        codec='libx264',
        audio_codec='aac',
        verbose=False,
        logger=None
    )

    # Get duration
    duration_mins = final.duration / 60

    # Cleanup temp
    for f in TEMP_DIR.glob("*"):
        try:
            f.unlink()
        except:
            pass

    print(f"\n{'='*60}")
    print(f"✅ DEMO VIDEO CREATED!")
    print(f"{'='*60}")
    print(f"\n📹 Video: {video_path.absolute()}")
    print(f"🖼️  Thumbnail: {thumbnail_path.absolute()}")
    print(f"⏱️  Duration: {duration_mins:.1f} minutes")
    print(f"\n🎬 Open the video to watch your demo!")
    print(f"{'='*60}\n")

    # Try to open the video
    try:
        if sys.platform == 'win32':
            os.startfile(str(video_path))
        elif sys.platform == 'darwin':
            subprocess.run(['open', str(video_path)])
        else:
            subprocess.run(['xdg-open', str(video_path)])
    except:
        print("Could not auto-open. Please open the video manually.")

    return str(video_path), str(thumbnail_path)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║     🎬 KIDS STORY VIDEO DEMO GENERATOR 🎬              ║
    ║                                                        ║
    ║  This will create a sample video with:                 ║
    ║  ✨ Beautiful opening intro                            ║
    ║  🖼️  Eye-catching YouTube thumbnail                    ║
    ║  🎤 Voice narration                                    ║
    ║  📖 Moral story for kids 4+                           ║
    ║  🌟 Professional ending card                           ║
    ╚════════════════════════════════════════════════════════╝
    """)

    try:
        video_path, thumb_path = create_demo_video()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure FFmpeg is installed:")
        print("  Windows: winget install ffmpeg")
        print("  Mac: brew install ffmpeg")
