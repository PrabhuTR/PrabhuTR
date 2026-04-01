# Kids Story Video Generator - Setup Guide

Automatically generates daily animated story videos for kids using **100% free tools**.

## Free Tools Used

| Tool | Purpose | Cost |
|------|---------|------|
| **Groq API** | AI story generation | Free (rate limited) |
| **Pollinations.ai** | AI image generation | Free |
| **Edge-TTS** | Voice narration | Free (Microsoft voices) |
| **FFmpeg/MoviePy** | Video creation | Free |
| **n8n** | Workflow automation | Free (self-hosted) |
| **YouTube API** | Auto upload | Free |

## Step 1: Get Free API Keys

### Groq API (Story Generation)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free
3. Create API key
4. Add to n8n as HTTP Header Auth: `Authorization: Bearer YOUR_KEY`

### YouTube API (Optional - for auto upload)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 credentials (Desktop app)
5. Download as `youtube_credentials.json`
6. Place in `kids-story-automation` folder

## Step 2: Install Dependencies

```bash
cd kids-story-automation
pip install -r requirements.txt
```

Also install FFmpeg:
- **Windows**: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org)
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

## Step 3: Setup n8n

### Option A: n8n Cloud (Easiest)
1. Sign up at [n8n.io](https://n8n.io) (free tier available)
2. Import `n8n-workflow.json`
3. Add Groq credentials
4. Update webhook URL to your Python server

### Option B: Self-hosted (Completely Free)
```bash
# Using Docker
docker run -it --rm -p 5678:5678 n8nio/n8n

# Or npm
npm install -g n8n
n8n start
```

## Step 4: Run the Video Generator

```bash
python video_generator.py
```

Server starts at `http://localhost:5000`

### Test it:
```bash
# Generate a test video
curl http://localhost:5000/test
```

## Step 5: Connect n8n to Video Generator

1. In n8n, update the "Send to Video Generator" node
2. Set URL to: `http://YOUR_IP:5000/generate`
3. If running locally, use `http://localhost:5000/generate`

For cloud n8n → local server, use [ngrok](https://ngrok.com):
```bash
ngrok http 5000
# Use the ngrok URL in n8n
```

## Step 6: Automate Daily Runs

The n8n workflow is set to run daily. You can also:

### Run Manually in n8n
Click "Execute Workflow" to generate a video now

### Windows Task Scheduler (if not using n8n)
```bash
# Create a batch file: run_daily.bat
python video_generator.py &
timeout /t 10
curl http://localhost:5000/test
```

## Folder Structure

```
kids-story-automation/
├── video_generator.py      # Main Python script
├── n8n-workflow.json       # n8n workflow to import
├── requirements.txt        # Python dependencies
├── SETUP_GUIDE.md          # This file
├── youtube_credentials.json # (You add this)
├── youtube_token.json      # (Auto-generated)
├── output/                 # Generated videos
└── temp/                   # Temporary files
```

## Customization

### Change Voice
Edit `video_generator.py`, line with `VOICES`:
```python
VOICES = [
    "en-US-AnaNeural",      # Young female (default)
    "en-US-GuyNeural",      # Male voice
    "en-GB-SoniaNeural",    # British accent
    "en-IN-NeerjaNeural",   # Indian accent
]
```

### Change Video Style
Modify the image prompts in the n8n Code node to change art style:
- "cartoon style" → "watercolor style"
- "bright colors" → "pastel colors"
- Add "disney style" or "pixar style"

### Change Target Age
Edit the system prompt in n8n's "Generate Story" node:
- "kids aged 4-8" → "toddlers aged 2-4"
- "kids aged 4-8" → "children aged 8-12"

## Troubleshooting

### "FFmpeg not found"
Install FFmpeg and add to PATH

### "Image download failed"
Pollinations.ai might be slow. The script auto-retries.

### "YouTube upload failed"
1. Check `youtube_credentials.json` exists
2. Delete `youtube_token.json` and re-authenticate
3. Verify YouTube API is enabled in Google Cloud

### Videos not generating
Check if port 5000 is available:
```bash
netstat -an | grep 5000
```

## Daily Automation Checklist

- [ ] Groq API key added to n8n
- [ ] Video generator running (`python video_generator.py`)
- [ ] n8n workflow activated
- [ ] YouTube credentials configured (optional)
- [ ] ngrok running if using cloud n8n

## Example Output

Each video will be:
- **Duration**: 1-2 minutes
- **Resolution**: 1280x720 (HD)
- **Format**: MP4 (H.264)
- **Audio**: AAC with clear narration

---

**Need help?** The system is modular - you can run just the video generator manually without n8n!
