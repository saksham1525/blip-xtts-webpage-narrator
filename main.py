import os
import re
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from PIL import Image, UnidentifiedImageError
from scipy.io.wavfile import write
from transformers import BlipProcessor, BlipForConditionalGeneration
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Config
URL = "https://www.flatsound.org/"
VOICE_FILES = ["./sample_voice1.wav", "./sample_voice2.wav"]

def get_text_and_images(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    text = soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text)
    print("Text Scraped Successfully: ", text)
    
    images = []
    for img in soup.find_all('img'):
        if 'src' in img.attrs:
            src = img['src']
            if src.startswith('http'):
                images.append(src)
    
    print(f"Found {len(images)} images from {url}")
    return text, images

def caption_images(image_urls):
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    model.generation_config.pad_token_id = model.generation_config.eos_token_id
    
    captions = []
    for url in image_urls:
        try:
            response = requests.get(url)
            image = Image.open(BytesIO(response.content)).convert('RGB')
            inputs = processor(image, "a picture of", return_tensors="pt")
            output = model.generate(**inputs, max_new_tokens=50)
            caption = processor.decode(output[0], skip_special_tokens=True)
            captions.append(caption)
        except:
            print(f"Error Captioning Image: {url}")
    
    return captions

def make_audio(text):
    config = XttsConfig()
    config.load_json("./XTTS-v2/config.json")
    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_dir="./XTTS-v2/")
    
    # Split text into chunks
    chunks = [text[i:i+200] for i in range(0, len(text), 200)]
    
    if not os.path.exists('./outputs'):
        os.makedirs('./outputs')
    
    for i, chunk in enumerate(chunks):
        audio = model.synthesize(chunk, config, speaker_wav=VOICE_FILES, language="en")
        filename = f'./outputs/audio_{i+1}.wav'
        write(filename, 24000, audio['wav'])
        print(f"\nSaved Audio File: {filename}")

def main():
    print("Web Content Narrator")
    
    text, images = get_text_and_images(URL)
    captions = caption_images(images)
    full_text = text + " " + " ".join(captions)
    
    make_audio(full_text)
    print("Done!")

main()