import os
import requests
import google.generativeai as genai
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips

# --- 1. SETUP KREDENSIAL ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_slang_narration(product_name):
    """
    Meminta Gemini buat narasi pake bahasa Jaksel/TikTok 2026 yang lagi hype.
    """
    prompt = f"""
    Tugas: Jadi TikTok Content Creator Affiliate yang lagi spill produk: {product_name}.
    Aturan: 
    - JANGAN BAKU. JANGAN KAKU. 
    - Gunakan bahasa gaul TikTok 2026 (contoh: aura points, cooking, real, no cap, demure, mindful, atau slang yang lagi naik).
    - Gaya bahasa harus kayak lagi ngomong sama bestie, santai, dan persuasif tapi gak maksa.
    - Hindari kata 'Halo teman-teman' atau 'Selamat datang'. Langsung to the point.

    Output harus JSON mentah (tanpa markdown):
    {{
      "hook": "Kalimat pancingan yang bikin orang berhenti scroll (max 7 kata)",
      "body": "Penjelasan kenapa produk ini 'very mindful, very demure' atau 'menambah aura points' (max 12 kata)",
      "cta": "Ajakan klik keranjang kuning yang asik (max 6 kata)"
    }}
    """
    try:
        response = model.generate_content(prompt)
        # Menghapus karakter non-JSON jika ada
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return eval(clean_text)
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "hook": "Jujurly ini cakep parah sih..",
            "body": "Gak paham lagi kenapa harganya bisa semurah ini. Definisi real!",
            "cta": "Sikat di keranjang kuning! 🔥"
        }

def create_cool_video(image_path, product_name, output_path):
    print(f"🔥 Generating content for {product_name}...")
    script = get_slang_narration(product_name)
    
    # Durasi total 16 detik
    # Segmen 1: Hook (4s), Segmen 2: Body (8s), Segmen 3: CTA (4s)
    durations = [4, 8, 4]
    texts = [script['hook'], script['body'], script['cta']]
    clips = []

    for i in range(3):
        # Buat background dengan efek zoom bergantian
        bg = ImageClip(image_path).set_duration(durations[i])
        if i % 2 == 0:
            bg = bg.resize(lambda t: 1 + 0.04 * t) # Zoom In
        else:
            bg = bg.resize(lambda t: 1.2 - 0.04 * t) # Zoom Out
            
        # Buat Overlay Teks
        txt = TextClip(
            texts[i].upper(), # Bikin uppercase biar lebih tegas
            fontsize=50, 
            color='yellow' if i == 0 else 'white', # Hook warna kuning biar eye-catching
            font='Arial-Bold',
            method='caption',
            size=(bg.w * 0.9, None),
            bg_color='black',
            align='center'
        ).set_opacity(0.9).set_duration(durations[i]).set_position(('center', 0.7, True))
        
        clips.append(CompositeVideoClip([bg.set_position("center"), txt]))

    final_video = concatenate_videoclips(clips)
    final_video.write_videofile(output_path, fps=24, codec="libx264")

def send_to_telegram(video_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(video_path, 'rb') as v:
        requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': 'Cek auranya! Siap gas? 🚀'}, files={'video': v})

if __name__ == "__main__":
    FILE_GAMBAR = "produk.jpg"
    NAMA_PRODUK = "Smartwatch Ultra Gen 2" # Ganti tiap mau upload
    OUTPUT = "video_viral.mp4"
    
    if os.path.exists(FILE_GAMBAR):
        create_cool_video(FILE_GAMBAR, NAMA_PRODUK, OUTPUT)
        send_to_telegram(OUTPUT)
    else:
        print("Gambarnya mana? Masukin produk.jpg dulu bos!")
        
