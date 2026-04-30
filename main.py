import os
import requests
import json
import time
from google.genai import Client
from moviepy import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips

# --- 1. SETUP KREDENSIAL ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

client = Client(api_key=GEMINI_KEY)

def get_slang_narration(product_name):
    """Meminta narasi dengan model 1.5-flash yang lebih stabil kuotanya."""
    prompt = f"""
    Buat skrip TikTok Affiliate: {product_name}. 
    Bahasa: Gaul TikTok 2026, Jaksel, No Cap. JANGAN BAKU!
    Format JSON:
    {{
      "hook": "pancingan (max 7 kata)",
      "body": "penjelasan (max 12 kata)",
      "cta": "ajakan klik (max 6 kata)"
    }}
    """
    try:
        # Pindah ke gemini-1.5-flash agar tidak kena limit 429
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        text_data = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text_data)
    except Exception as e:
        print(f"AI Error: {e}. Menggunakan fallback narasi...")
        return {
            "hook": f"POV: NEMU {product_name.upper()} VIRAL!",
            "body": "Beneran sebagus itu, nambah aura points parah sih.",
            "cta": "Cek keranjang kuning! 🛒"
        }

def create_cool_video(image_path, product_name, output_path):
    print(f"🎬 Meracik konten untuk {product_name}...")
    script = get_slang_narration(product_name)
    
    durations = [4, 8, 4]
    texts = [script['hook'], script['body'], script['cta']]
    clips = []

    # DAFTAR FONT LINUX (Ubuntu): DejaVu-Sans-Bold atau Liberation-Sans-Bold
    # Ini supaya tidak error 'cannot open resource'
    FONT_NAME = "DejaVu-Sans-Bold"

    for i in range(3):
        bg = ImageClip(image_path).with_duration(durations[i])
        
        # Animasi Zoom
        if i % 2 == 0:
            bg = bg.resized(lambda t: 1 + 0.04 * t)
        else:
            bg = bg.resized(lambda t: 1.2 - 0.04 * t)
            
        # Teks Overlay
        try:
            txt = TextClip(
                text=texts[i].upper(),
                font_size=50, 
                color='yellow' if i == 0 else 'white',
                font=FONT_NAME, # PAKAI FONT LINUX
                method='caption',
                size=(bg.w * 0.9, None),
                bg_color='black'
            ).with_opacity(0.85).with_duration(durations[i]).with_position(('center', 0.7, True))
        except Exception as e:
            print(f"Font {FONT_NAME} gagal, mencoba font default...")
            # Fallback jika font masih gagal
            txt = TextClip(
                text=texts[i].upper(),
                font_size=50,
                color='white',
                method='caption',
                size=(bg.w * 0.9, None)
            ).with_duration(durations[i]).with_position(('center', 0.7, True))
        
        clips.append(CompositeVideoClip([bg.with_position("center"), txt]))

    final_video = concatenate_videoclips(clips)
    final_video.write_videofile(output_path, fps=24, codec="libx264")

def send_to_telegram(video_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(video_path, 'rb') as v:
        requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': 'Video FYP 2026 Ready! 🚀'}, files={'video': v})

if __name__ == "__main__":
    FILE_GAMBAR = "produk.jpg"
    NAMA_PRODUK = os.getenv('PRODUCT_NAME', 'Produk Viral')
    OUTPUT = "video_viral.mp4"
    
    if os.path.exists(FILE_GAMBAR):
        create_cool_video(FILE_GAMBAR, NAMA_PRODUK, OUTPUT)
        send_to_telegram(OUTPUT)
    else:
        print("File produk.jpg tidak ditemukan!")
        
