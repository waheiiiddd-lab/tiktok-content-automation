import os
import asyncio
import json
import requests
import random
from google.genai import Client
from moviepy import (
    ImageClip, TextClip, CompositeVideoClip, 
    concatenate_videoclips, AudioFileClip, ColorClip
)

# --- 1. SETUP KREDENSIAL ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
client = Client(api_key=GEMINI_KEY)

async def generate_voice(text, output_path):
    """Voiceover jernih ala TikTok Influencer."""
    import edge_tts
    # Suara Gadis (Cewek) atau Ardi (Cowok)
    voice = random.choice(["id-ID-GadisNeural", "id-ID-ArdiNeural"])
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def get_ai_creative_script(product_name):
    """Bikin skrip yang gak template-an sama sekali."""
    prompt = f"""
    Tugas: Jadi TikTok Creator yang lagi spill {product_name}. 
    Konteks: Bahasa 2026, sangat santai, pake slang 'real', 'aura', 'cooking'. 
    Buatlah 1 paragraf narasi (max 20 kata) yang isinya: Hook menarik + spill dikit + suruh cek keranjang.
    Output HANYA teks narasinya saja, jangan ada embel-embel lain.
    """
    try:
        response = client.models.generate_content(model="models/gemini-1.5-flash", contents=prompt)
        return response.text.strip()
    except:
        return f"Real banget sih produk {product_name} ini, nambah aura points parah. Sikat di keranjang kuning sekarang!"

def create_advanced_video(image_path, mascot_path, product_name, output_path):
    # 1. Siapkan Narasi & Voiceover
    narasi = get_ai_creative_script(product_name)
    asyncio.run(generate_voice(narasi, "audio.mp3"))
    audio_clip = AudioFileClip("audio.mp3")
    duration = audio_clip.duration + 0.5
    
    # 2. Canvas TikTok HD (9:16)
    W, H = 1080, 1920
    # Background Gradasi Gelap (Elegan)
    bg = ColorClip(size=(W, H), color=(15, 15, 15)).with_duration(duration)
    
    # 3. Konten Utama (Gambar Produk)
    # Kita bikin sedikit zoom-in tapi dengan angka bulat agar tidak pecah
    prod_img = ImageClip(image_path).with_duration(duration)
    prod_img = prod_img.resized(width=int(W * 0.85))
    prod_img = prod_img.with_position(('center', 450))
    
    # 4. Fitur Baru: MASCOT NARRATOR (Jika file ada)
    overlays = [bg, prod_img]
    if os.path.exists(mascot_path):
        mascot = ImageClip(mascot_path).with_duration(duration)
        mascot = mascot.resized(height=int(H * 0.25)) # Ukuran 25% layar
        
        # Efek "Bouncing" agar karakter terlihat hidup saat bicara
        mascot = mascot.with_position(lambda t: (int(W*0.05), int(H*0.65 + (5 * (t % 0.5 > 0.25)))))
        overlays.append(mascot)

    # 5. Dynamic Text (Caption Otomatis)
    # Teks atas (Hook)
    txt_top = TextClip(
        text="SPILL BARANG VIRAL 2026 🚀",
        font_size=55, color='yellow', font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        method='caption', size=(int(W*0.9), None)
    ).with_duration(duration).with_position(('center', 150))
    
    # Teks bawah (Sesuai Voiceover)
    txt_main = TextClip(
        text=narasi.upper(),
        font_size=40, color='white', font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        bg_color='rgba(0,0,0,0.6)', method='caption', size=(int(W*0.8), None)
    ).with_duration(duration).with_position(('center', H-450))

    overlays.extend([txt_top, txt_main])

    # 6. Gabungkan & Render
    final_video = CompositeVideoClip(overlays)
    final_video = final_video.with_audio(audio_clip)
    
    print("🚀 Sedang merender video HD...")
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    PRODUCT = os.getenv('PRODUCT_NAME', 'Produk Rahasia')
    if os.path.exists("produk.jpg"):
        create_advanced_video("produk.jpg", "mascot.png", PRODUCT, "video_final.mp4")
        
        # Kirim ke Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
        with open("video_final.mp4", 'rb') as v:
            requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': f'✅ Hasil konten: {PRODUCT}'}, files={'video': v})
    else:
        print("Error: Pastikan produk.jpg ada di folder.")
    
