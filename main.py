import os
import requests
import json
from google.genai import Client
from moviepy import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips

# --- 1. SETUP KREDENSIAL ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

client = Client(api_key=GEMINI_KEY)

def get_slang_narration(product_name):
    prompt = f"Buat skrip TikTok Affiliate: {product_name}. Bahasa gaul TikTok 2026, No Cap. Output JSON: {{'hook': '...', 'body': '...', 'cta': '...'}}"
    try:
        # FIX 1: Gunakan path model yang lengkap
        response = client.models.generate_content(
            model="models/gemini-1.5-flash", 
            contents=prompt
        )
        text_data = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text_data)
    except:
        return {"hook": "POV: NEMU BARANG VIRAL!", "body": "Nambah aura points parah sih.", "cta": "Cek keranjang kuning!"}

def create_cool_video(image_path, product_name, output_path):
    print(f"🎬 Meracik konten untuk {product_name}...")
    script = get_slang_narration(product_name)
    
    durations = [4, 8, 4]
    texts = [script['hook'], script['body'], script['cta']]
    clips = []

    # FIX 2: Gunakan PATH ABSOLUT font di Linux GitHub Runner
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    for i in range(3):
        bg = ImageClip(image_path).with_duration(durations[i])
        
        if i % 2 == 0:
            bg = bg.resized(lambda t: 1 + 0.04 * t)
        else:
            bg = bg.resized(lambda t: 1.2 - 0.04 * t)
            
        # FIX 3: Gunakan int() untuk ukuran agar tidak kena TypeError desimal
        target_width = int(bg.w * 0.9)
        
        txt = TextClip(
            text=texts[i].upper(),
            font_size=50, 
            color='yellow' if i == 0 else 'white',
            font=FONT_PATH, 
            method='caption',
            size=(target_width, None), # Ukuran sudah bulat (integer)
            bg_color='black'
        ).with_opacity(0.85).with_duration(durations[i]).with_position(('center', 0.7, True))
        
        clips.append(CompositeVideoClip([bg.with_position("center"), txt]))

    final_video = concatenate_videoclips(clips)
    final_video.write_videofile(output_path, fps=24, codec="libx264")

def send_to_telegram(video_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(video_path, 'rb') as v:
        requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': 'Video FYP Ready! 🚀'}, files={'video': v})

if __name__ == "__main__":
    if os.path.exists("produk.jpg"):
        create_cool_video("produk.jpg", os.getenv('PRODUCT_NAME', 'Produk Viral'), "video_viral.mp4")
        send_to_telegram("video_viral.mp4")
    
