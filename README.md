# Web Content Narrator

Scrapes text and images from a webpage, generates image captions using BLIP, and converts everything to speech with XTTS.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download XTTS-v2 model files and place them in `./XTTS-v2/` folder with `config.json`

## Usage

1. Edit the `URL` in `main.py` to your target webpage
2. Run the script:
```bash
python main.py
```

Audio files will be saved to `./outputs/` directory.

## Requirements

- Python 3.7+
- Reference voice files: `sample_voice1.wav` and `sample_voice2.wav`
- XTTS-v2 model files in `./XTTS-v2/` folder