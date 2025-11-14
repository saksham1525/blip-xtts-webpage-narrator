# Web Content Narrator

Scrapes text and images from a webpage, generates image captions using BLIP, and converts everything to speech with XTTS voice cloning.

## Requirements

- Python 3.11+
- Reference voice file: `sample_voice1.wav` (for voice cloning)
- PostgreSQL

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **PostgreSQL Setup:**
```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb narrations
```

4. Initialize database tables:
```bash
python database.py
```

5. Accept TTS license (first run only):
```bash
export COQUI_TOS_AGREED=1  # On Windows: set COQUI_TOS_AGREED=1
```

**Note:** On first run, XTTS-v2 model (~1.87GB) will auto-download to `~/.local/share/tts/`

## Usage

Run the script with a URL:
```bash
python main.py <URL>
```

**Example:**
```bash
python main.py https://example.com/article
python main.py https://www.flatsound.org/
```

Audio files will be saved to `./outputs/` directory as `audio_1.wav`, `audio_2.wav`, etc.

## Query Database

```bash
python query_db.py list      # List all
python query_db.py show 1    # Show details
python query_db.py delete 1  # Delete
```

## What It Does

- **Web Scraping**: Extracts text and images from any webpage
- **Image Captioning**: Uses BLIP model to generate descriptions
- **Voice Cloning**: XTTS generates speech matching your reference voice
- **Model Caching**: Models load once and stay in memory for faster subsequent runs
- **Postgres Database**: Storing results of images, captions and text in database