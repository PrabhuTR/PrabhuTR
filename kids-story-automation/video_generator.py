"""
Kids Story Video Generator
Generates animated story videos using free tools:
- Edge-TTS for voiceover (free Microsoft voices)
- Pollinations.ai for images (free)
- MoviePy/FFmpeg for video creation (free)
- YouTube API for upload

Run: python video_generator.py
"""

import os
import json
import asyncio
import requests
from pathlib import Path
from datetime import datetime
import subprocess

# Check and install dependencies
def install_dependencies():
    deps = ['edge-tts', 'moviepy', 'pillow', 'flask', 'google-auth-oauthlib', 'google-api-python-client']
    for dep in deps:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            print(f"Installing {dep}...")
            subprocess.run(['pip', 'install', dep], check=True)

install_dependencies()

import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
from PIL import Image
from io import BytesIO
from flask import Flask, request, jsonify

# Configuration
OUTPUT_DIR = Path("./output")
TEMP_DIR = Path("./temp")
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Kid-friendly voice options (Edge-TTS - FREE)
VOICES = [
    "en-US-AnaNeural",      # Young female, cheerful
    "en-US-JennyNeural",    # Female, friendly
    "en-GB-SoniaNeural",    # British female
]

app = Flask(__name__)


async def generate_voiceover(text: str, output_path: str, voice: str = "en-US-AnaNeural"):
    """Generate voiceover using Edge-TTS (free Microsoft voices)"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path


def download_image(url: str, output_path: str, max_retries: int = 3) -> str:
    """Download image from Pollinations.ai"""
    for attempt in range(max_retries):
        try:
            print(f"Downloading image (attempt {attempt + 1}): {url[:80]}...")
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img = img.convert('RGB')
                img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                img.save(output_path)
                print(f"Saved: {output_path}")
                return output_path
        except Exception as e:
            print(f"Retry {attempt + 1}: {e}")

    # Create placeholder if download fails
    img = Image.new('RGB', (1280, 720), color=(135, 206, 235))  # Sky blue
    img.save(output_path)
    return output_path


def create_video(story_data: dict) -> str:
    """Create video from story scenes"""
    title = story_data.get('title', 'Kids Story')
    scenes = story_data.get('scenes', [])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_name = f"story_{timestamp}.mp4"
    output_path = OUTPUT_DIR / video_name

    clips = []
    voice = VOICES[0]  # Use cheerful voice

    print(f"\nCreating video: {title}")
    print(f"Total scenes: {len(scenes)}")

    for i, scene in enumerate(scenes):
        print(f"\nProcessing scene {i + 1}/{len(scenes)}...")

        # Download image
        image_path = TEMP_DIR / f"scene_{i}.jpg"
        download_image(scene['imageUrl'], str(image_path))

        # Generate voiceover
        audio_path = TEMP_DIR / f"audio_{i}.mp3"
        asyncio.run(generate_voiceover(scene['narration'], str(audio_path), voice))

        # Create clip
        audio = AudioFileClip(str(audio_path))
        duration = audio.duration + 1  # Add 1 second padding

        image_clip = ImageClip(str(image_path)).set_duration(duration)
        image_clip = image_clip.set_audio(audio)

        clips.append(image_clip)

    # Add title card at beginning
    print("\nAdding title card...")
    try:
        title_clip = TextClip(
            title,
            fontsize=70,
            color='white',
            bg_color='darkblue',
            size=(1280, 720),
            method='caption'
        ).set_duration(3)
        clips.insert(0, title_clip)
    except Exception as e:
        print(f"Could not add title card: {e}")

    # Concatenate all clips
    print("\nCombining clips...")
    final_video = concatenate_videoclips(clips, method="compose")

    # Write final video
    print(f"\nRendering video to {output_path}...")
    final_video.write_videofile(
        str(output_path),
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile=str(TEMP_DIR / "temp_audio.m4a"),
        remove_temp=True,
        verbose=False,
        logger=None
    )

    # Cleanup temp files
    for f in TEMP_DIR.glob("*"):
        f.unlink()

    print(f"\nVideo created: {output_path}")
    return str(output_path)


def upload_to_youtube(video_path: str, title: str, description: str):
    """Upload video to YouTube using API"""
    # This requires OAuth setup - see setup instructions
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials

        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        creds_file = Path("./youtube_credentials.json")
        token_file = Path("./youtube_token.json")

        if not creds_file.exists():
            print("YouTube credentials not found. Skipping upload.")
            print("To enable: Add youtube_credentials.json from Google Cloud Console")
            return None

        creds = None
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_file, 'w') as f:
                f.write(creds.to_json())

        youtube = build('youtube', 'v3', credentials=creds)

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': ['kids', 'children', 'story', 'animated', 'educational', 'bedtime story'],
                'categoryId': '24'  # Entertainment
            },
            'status': {
                'privacyStatus': 'public',  # or 'unlisted' for testing
                'selfDeclaredMadeForKids': True
            }
        }

        media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)

        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )

        response = request.execute()
        video_id = response['id']
        print(f"Uploaded to YouTube: https://youtube.com/watch?v={video_id}")
        return video_id

    except Exception as e:
        print(f"YouTube upload failed: {e}")
        return None


@app.route('/generate', methods=['POST'])
def handle_generate():
    """Webhook endpoint for n8n"""
    try:
        data = request.json
        print(f"Received story: {data.get('title', 'Unknown')}")

        # Generate video
        video_path = create_video(data)

        # Upload to YouTube
        title = f"{data.get('title', 'Kids Story')} | Animated Story for Kids"
        description = f"""
A fun animated story for children!

This story was created with love for kids aged 4-8.
Subscribe for daily stories!

#KidsStory #AnimatedStory #ChildrenStory #BedtimeStory
        """

        youtube_id = upload_to_youtube(video_path, title, description)

        return jsonify({
            'success': True,
            'video_path': video_path,
            'youtube_id': youtube_id
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test the video generation with a sample story"""
    sample_story = {
        "title": "The Brave Little Star",
        "scenes": [
            {
                "narration": "Once upon a time, there was a little star who lived high up in the sky.",
                "imageUrl": "https://image.pollinations.ai/prompt/cute%20cartoon%20star%20character%20in%20night%20sky%20with%20moon%2C%20kids%20illustration%2C%20bright%20colors?width=1280&height=720"
            },
            {
                "narration": "The little star wanted to shine the brightest, but was too shy to try.",
                "imageUrl": "https://image.pollinations.ai/prompt/shy%20cartoon%20star%20hiding%20behind%20clouds%2C%20cute%20childrens%20book%20illustration?width=1280&height=720"
            },
            {
                "narration": "One night, a lost firefly needed help finding its way home.",
                "imageUrl": "https://image.pollinations.ai/prompt/cartoon%20firefly%20looking%20lost%20in%20dark%20forest%2C%20friendly%20style%2C%20kids%20book?width=1280&height=720"
            },
            {
                "narration": "The little star took a deep breath and shined as bright as it could!",
                "imageUrl": "https://image.pollinations.ai/prompt/bright%20shining%20cartoon%20star%20with%20sparkles%2C%20happy%20expression%2C%20vibrant%20colors?width=1280&height=720"
            },
            {
                "narration": "The firefly found its way home. Remember, you are braver than you think! The End.",
                "imageUrl": "https://image.pollinations.ai/prompt/happy%20cartoon%20star%20and%20firefly%20together%2C%20rainbow%20background%2C%20The%20End%20text%2C%20kids%20illustration?width=1280&height=720"
            }
        ]
    }

    video_path = create_video(sample_story)
    return jsonify({'success': True, 'video_path': video_path})


if __name__ == "__main__":
    print("""
    ========================================
    Kids Story Video Generator
    ========================================

    Endpoints:
    - GET  /test     - Generate a test video
    - POST /generate - Generate video from n8n

    Starting server on http://localhost:5000
    ========================================
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
