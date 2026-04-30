import os
import asyncio
import json
import requests
import random
from PIL import Image
from google.genai import Client
from google.genai import types
from moviepy import (
    ImageClip, TextClip, CompositeVideoClip, 
    concatenate_videoclips, AudioFileClip, ColorClip
)

# --- SETUP KREDENSIAL ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

client = Client(api_key=GEMINI_KEY)

def analyze_image_and_get_script(image_path):
    """
    AI bakal 'melihat' gambar produk dan bikin skrip otomatis
    tanpa kamu kasih tahu itu barang apa.
    """
    print("👁️ AI sedang menganalisa gambar produk...")
    img = Image.open(image_path)
    
    prompt = """
    Lihat gambar ini. Identifikasi produk apa ini.
    Lalu buatkan skrip TikTok Affiliate (max 20 kata). 
    Gaya bahasa: Trend 2026, Jaksel, No Cap, pake slang 'Aura Points' atau 'Cooking'.
    Anggap kamu (si narator) lagi pake/megang produk ini sekarang.
    
    Output HANYA JSON mentah:
    {
      "product_name": "nama produknya",
      "script": "isi narasi buat voiceover"
    }
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Pakai 2.0 untuk Vision yang lebih akurat
            contents=[prompt, img]
        )
        # Bersihkan response JSON
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Vision Error: {e}")
        return {
            "product_name": "Produk Viral",
            "script": "Jujurly ini cakep parah, nambah aura points. Sikat di keranjang kuning!"
        }

async def generate_voice(text, output_path):
    import edge_tts
    # Suara acak biar gak bosen
    voice = random.choice(["id-ID-GadisNeural", "id-ID-ArdiNeural"])
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def create_dynamic_video(image_path, mascot_path, output_path):
    # 1. AI Menganalisa Gambar & Bikin Skrip
    ai_data = analyze_image_and_get_script(image_path)
    product_name = ai_data['product_name']
    narasi = ai_data['script']
    
    print(f"📦 Produk Terdeteksi: {product_name}")
    print(f"🎙️ Narasi: {narasi}")

    # 2. Bikin Voiceover
    asyncio.run(generate_voice(narasi, "audio.mp3"))
    audio_clip = AudioFileClip("audio.mp3")
    duration = audio_clip.duration + 0.5
    
    # 3. Canvas HD (1080x1920)
    W, H = 1080, 1920
    bg = ColorClip(size=(W, H), color=(10, 10, 10)).with_duration(duration)
    
    # 4. Gambar Produk (Posisikan di tengah)
    prod_img = ImageClip(image_path).with_duration(duration)
    prod_img = prod_img.resized(width=int(W * 0.9))
    prod_img = prod_img.with_position(('center', 'center'))
    
    # 5. Mascot (Si Narator)
    overlays = [bg, prod_img]
    if os.path.exists(mascot_path):
        mascot = ImageClip(mascot_path).with_duration(duration)
        mascot = mascot.resized(height=int(H * 0.25))
        # Efek goyang dikit biar hidup
        mascot = mascot.with_position(lambda t: (int(W*0.05), int(H*0.7 + (5 * (t % 0.4 > 0.2)))))
        overlays.append(mascot)

    # 6. Teks Dinamis
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    
    # Header Nama Produk
    header = TextClip(
        text=product_name.upper(), font_size=60, color='yellow', font=FONT,
        method='caption', size=(int(W*0.8), None), bg_color='black'
    ).with_duration(duration).with_position(('center', 150))
    
    # Caption Narasi (di bawah)
    caption = TextClip(
        text=narasi.upper(), font_size=40, color='white', font=FONT,
        method='caption', size=(int(W*0.85), None), bg_color='rgba(0,0,0,0.7)'
    ).with_duration(duration).with_position(('center', H-400))

    overlays.extend([header, caption])

    # 7. Render
    final = CompositeVideoClip(overlays).with_audio(audio_clip)
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    if os.path.exists("produk.jpg"):
        create_dynamic_video("produk.jpg", "mascot.png", "video_final.mp4")
        
        # Kirim ke Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
        with open("video_final.mp4", 'rb') as v:
            requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': '✅ Video Otomatis Ready!'}, files={'video': v})
    
