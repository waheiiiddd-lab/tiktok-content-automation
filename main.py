import os
import requests
import json
from google import genai
from moviepy import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips

# --- 1. SETUP KREDENSIAL ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Inisialisasi Client Gemini Baru (Versi 2026)
client = genai.Client(api_key=GEMINI_KEY)

def get_slang_narration(product_name):
    """Meminta narasi trendi menggunakan SDK google-genai terbaru."""
    prompt = f"""
    Spill produk: {product_name}. Gunakan bahasa TikTok 2026 yang lagi hype, 
    no cap, aura points, atau slang terbaru lainnya. JANGAN BAKU!
    Output JSON mentah:
    {{
      "hook": "pancingan (max 7 kata)",
      "body": "penjelasan asik (max 12 kata)",
      "cta": "ajakan klik keranjang (max 6 kata)"
    }}
    """
    try:
        # Menggunakan model flash terbaru yang lebih cepat
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        # Menangani parsing JSON yang lebih aman
        text_response = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text_response)
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "hook": "POV: Kamu nemu barang sekeren ini..",
            "body": "Jujurly ini worth it parah buat nambah aura points!",
            "cta": "Sikat di keranjang kuning! 🛒"
        }

def create_cool_video(image_path, product_name, output_path):
    print(f"🎬 Meracik konten masa depan untuk {product_name}...")
    script = get_slang_narration(product_name)
    
    durations = [4, 8, 4]
    texts = [script['hook'], script['body'], script['cta']]
    clips = []

    for i in range(3):
        # MoviePy v2: ImageClip langsung dipanggil
        bg = ImageClip(image_path).with_duration(durations[i])
        
        # Animasi Zoom
        if i % 2 == 0:
            bg = bg.resized(lambda t: 1 + 0.04 * t)
        else:
            bg = bg.resized(lambda t: 1.2 - 0.04 * t)
            
        # MoviePy v2: TextClip menggunakan parameter yang lebih ringkas
        txt = TextClip(
            text=texts[i].upper(),
            font_size=50, 
            color='yellow' if i == 0 else 'white',
            font='Arial-Bold',
            method='caption',
            size=(bg.w * 0.9, None),
            bg_color='black'
        ).with_opacity(0.9).with_duration(durations[i]).with_position(('center', 0.7, True))
        
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
        print("Mana file produk.jpg-nya?")
        
