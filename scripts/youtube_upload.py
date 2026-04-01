#!/usr/bin/env python3
"""
YouTube Video Uploader Script
Downloads video from GitHub Release and uploads to YouTube
"""

import json
import os
import sys
from pathlib import Path

def main():
    video_path = os.environ.get('VIDEO_PATH')
    thumbnail_path = os.environ.get('THUMBNAIL_PATH', '')
    metadata_path = os.environ.get('METADATA_PATH', '')
    custom_title = os.environ.get('CUSTOM_TITLE', '')

    print(f"Video path: {video_path}")
    print(f"Thumbnail: {thumbnail_path}")
    print(f"Metadata: {metadata_path}")

    if not video_path or not os.path.exists(video_path):
        print("ERROR: Video file not found!")
        sys.exit(1)

    # Load metadata if available
    metadata = {}
    if metadata_path and os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        print(f"Loaded metadata: {metadata}")

    # Get story details
    story_title = custom_title or metadata.get('title', 'Kids Story Time')
    moral = metadata.get('moral', 'Be kind and good!')
    language = metadata.get('language', 'English')

    # Language-specific title suffixes
    lang_suffix = {
        "English": "Animated Story for Kids",
        "Hindi": "बच्चों की कहानी",
        "Tamil": "குழந்தைகள் கதை",
        "Telugu": "పిల్లల కథ",
        "Kannada": "ಮಕ್ಕಳ ಕಥೆ",
        "Malayalam": "കുട്ടികളുടെ കഥ",
        "Bengali": "শিশুদের গল্প",
        "Marathi": "मुलांची गोष्ट"
    }

    suffix = lang_suffix.get(language, "Animated Story for Kids")

    # YouTube video details
    title = f"{story_title} | {suffix} | Moral Story"

    description = f"""🌟 {story_title} 🌟

📖 Language: {language}
👶 Age Group: 4+ years
🎓 Moral: {moral}

Welcome to our magical story time! This animated MORAL STORY is perfect for children aged 4 and above.

🎨 What you'll enjoy:
✨ Beautiful colorful animations
🎵 Clear {language} narration with soothing voice
📚 Important life lesson for kids
💤 Perfect for bedtime!
🧒 Safe content for young children

📝 MORAL OF THE STORY: {moral}

👍 If your little ones enjoyed this story, please LIKE and SUBSCRIBE for more magical adventures every day!

🔔 Turn on notifications so you never miss a new story!

#KidsStories #MoralStories #{language}Stories #AnimatedStories #BedtimeStories #ChildrensBooks #StoriesForKids #KidsAnimation #FairyTales #PreschoolStories #ToddlerStories #4PlusKids #EducationalStories
"""

    # Language-specific tags
    lang_tags = {
        "Hindi": ["hindi stories", "hindi kahani", "bachon ki kahani", "hindi cartoon"],
        "Tamil": ["tamil stories", "tamil kathai", "kuzhanthai kathai", "tamil cartoon"],
        "Telugu": ["telugu stories", "telugu kathalu", "pillala kathalu", "telugu cartoon"],
        "Kannada": ["kannada stories", "kannada kathe", "makkala kathe", "kannada cartoon"],
        "Malayalam": ["malayalam stories", "malayalam katha", "kuttikal katha", "malayalam cartoon"],
        "Bengali": ["bengali stories", "bangla golpo", "shishuder golpo", "bengali cartoon"],
        "Marathi": ["marathi stories", "marathi goshti", "mulanche goshti", "marathi cartoon"]
    }

    tags = [
        "kids stories", "children stories", "animated stories",
        "bedtime stories", "stories for kids", "moral stories",
        "fairy tales", "preschool", "toddler stories", "kids animation",
        "educational videos", "kids entertainment", "story time",
        "children animation", "kids videos", "4 plus kids", "moral lesson"
    ]
    tags.extend(lang_tags.get(language, []))

    # Import YouTube libraries
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2.credentials import Credentials
    except ImportError:
        print("ERROR: Required libraries not installed!")
        print("Run: pip install google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    # Load credentials
    print("\nLoading YouTube credentials...")

    if not os.path.exists("youtube_token.json"):
        print("ERROR: youtube_token.json not found!")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file("youtube_token.json")
    youtube = build('youtube', 'v3', credentials=creds)

    body = {
        'snippet': {
            'title': title[:100],
            'description': description,
            'tags': tags,
            'categoryId': '24',  # Entertainment
            'defaultLanguage': 'en',
            'defaultAudioLanguage': 'en'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': True,
            'license': 'youtube',
            'embeddable': True,
            'publicStatsViewable': True
        }
    }

    print(f"\nUploading: {title}")
    print(f"File: {video_path}")

    media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)

    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"Upload progress: {progress}%")

    video_id = response['id']
    video_url = f"https://youtube.com/watch?v={video_id}"

    print(f"\n✅ Video uploaded successfully!")
    print(f"📺 Watch: {video_url}")

    # Upload thumbnail if available
    if thumbnail_path and os.path.exists(thumbnail_path):
        print("\nUploading thumbnail...")
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
            ).execute()
            print("✅ Thumbnail uploaded!")
        except Exception as thumb_error:
            print(f"⚠️ Thumbnail upload failed: {thumb_error}")
            print("(Video uploaded successfully, thumbnail can be added manually)")

    print(f"\n🎉 All done! Video is live at: {video_url}")

    # Save video URL for summary
    with open("video_url.txt", "w") as f:
        f.write(video_url)

    with open("video_title.txt", "w") as f:
        f.write(story_title)

if __name__ == "__main__":
    main()
