import os
import re
import sys
from io import BytesIO
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from TTS.api import TTS
from database import get_db, Narration, ImageCaption, AudioChunk

VOICE_FILE = "./sample_voice1.wav"
_tts, _blip_proc, _blip_model = None, None, None

def get_text_and_images(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    text = re.sub(r'\s+', ' ', soup.get_text(separator=' ', strip=True))
    
    base_url = '/'.join(url.split('/')[:3])
    images = [img['src'] if img['src'].startswith('http') else base_url + img['src']
              for img in soup.find_all('img') if 'src' in img.attrs]
    
    print(f"Scraped {len(text)} chars, {len(images)} images")
    return text, images

def caption_images(image_urls, narration_id=None):
    global _blip_proc, _blip_model
    
    if _blip_proc is None:
        print("Loading BLIP model...")
        _blip_proc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        _blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        _blip_model.generation_config.pad_token_id = _blip_model.generation_config.eos_token_id
    
    captions, db = [], get_db() if narration_id else None
    
    for url in image_urls:
        try:
            img = Image.open(BytesIO(requests.get(url, timeout=5).content)).convert('RGB')
            inputs = _blip_proc(img, "a picture of", return_tensors="pt")
            caption = _blip_proc.decode(_blip_model.generate(**inputs, max_new_tokens=50)[0], skip_special_tokens=True)
            captions.append(caption)
            
            if db:
                db.add(ImageCaption(narration_id=narration_id, image_url=url, caption=caption))
                db.commit()
        except:
            pass
    
    if db:
        db.close()
    print(f"Captioned {len(captions)}/{len(image_urls)} images")
    return captions

def make_audio(text, speaker_wav, narration_id=None):
    global _tts
    
    if _tts is None:
        print("Loading TTS model...")
        _tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
    
    os.makedirs('./outputs', exist_ok=True)
    chunks = [text[i:i+250] for i in range(0, len(text), 250)]
    print(f"Generating {len(chunks)} audios")
    
    db = get_db() if narration_id else None
    
    for i, chunk in enumerate(chunks, 1):
        if chunk.strip():
            filename = f'./outputs/audio_{i}.wav'
            _tts.tts_to_file(text=chunk, speaker_wav=speaker_wav, language="en", file_path=filename)
            print(f"{filename} generated")
            
            if db:
                db.add(AudioChunk(narration_id=narration_id, chunk_number=i, text=chunk, file_path=filename))
                db.commit()
    
    if db:
        db.close()
    return len(chunks)

def main(url):
    print("\nWeb Content Narrator\n")
    
    db = get_db()
    narration = Narration(url=url, status='processing')
    db.add(narration)
    db.commit()
    db.refresh(narration)
    print(f"Narration #{narration.id}")
    
    try:
        text, images = get_text_and_images(url)
        captions = caption_images(images, narration.id)
        narration.text = text + " " + " ".join(captions)
        db.commit()
        
        make_audio(narration.text, VOICE_FILE, narration.id)
        narration.status = 'complete'
        db.commit()
        print("\nComplete! Saved to database")
    except Exception as e:
        narration.status = 'failed'
        db.commit()
        print(f"\nFailed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <URL>")
        print("Example: python main.py https://example.com")
        sys.exit(1)
    main(sys.argv[1])