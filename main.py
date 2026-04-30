import os
import asyncio
import json
import requests
import random
from PIL import Image
from google.genai import Client
from moviepy import (
    ImageClip, TextClip, CompositeVideoClip, 
    concatenate_videoclips, AudioFileClip, ColorClip
)

# --- SETUP KREDENSIAL ---
# Masukkan API Key Gemini dan Telegram Token ke GitHub Secrets
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

client = Client(api_key=GEMINI_KEY)

def analyze_product(image_path):
    """AI melihat gambar untuk nentuin kategori kostum maskot."""
    print("👁️ AI sedang 'ngintip' barang baru...")
    img = Image.open(image_path)
    
    prompt = """
    Identifikasi produk ini. Masukkan ke salah satu kategori: [kacamata, baju, jam, gadget, lainnya].
    Lalu buat narasi TikTok Affiliate (max 18 kata) pake bahasa Jaksel 2026, No Cap, Aura Points. JANGAN BAKU!
    Output HANYA JSON mentah:
    {
      "nama": "nama produknya",
      "kategori": "kategori tadi",
      "script": "isi narasinya"
    }
    """
    try:
        response = client.models.generate_content(
            model="models/gemini-1.5-flash", 
            contents=[prompt, img]
        )
        # Menghapus markdown JSON jika ada
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Vision Error: {e}. Menggunakan fallback narasi...")
        return {"nama": "Produk Viral", "kategori": "lainnya", "script": "Real banget sih kacamata ini, nambah aura points parah. Sikat di keranjang kuning! 🔥"}

async def generate_voice(text, output_path):
    import edge_tts
    # Pilih secara acak id-ID-GadisNeural (Cewe) atau id-ID-ArdiNeural (Cowo)
    voice = random.choice(["id-ID-GadisNeural", "id-ID-ArdiNeural"])
    communicate = edge_tts.Communicate(text, voice)
    # Menambahkan timeout agar tidak hang
    await asyncio.wait_for(communicate.save(output_path), timeout=30)

def create_pro_video(image_path, output_path):
    # 1. Analisa Gambar via Vision
    data = analyze_product(image_path)
    print(f"📦 Kategori Terdeteksi: {data['kategori']}")

    # 2. Bikin Suara
    asyncio.run(generate_voice(data['script'], "audio.mp3"))
    audio_clip = AudioFileClip("audio.mp3")
    duration = audio_clip.duration + 0.8 # Tambah nafas di akhir
    
    # 3. Canvas HD TikTok (9:16, 1080x1920)
    W, H = 1080, 1920
    # Background Gradasi Gelap (Elegan, cocok jualan barang estetik)
    bg = ColorClip(size=(W, H), color=(20, 20, 20)).with_duration(duration)
    
    # 4. Gambar Produk Jernih (Anti-Sobek/Glitch)
    prod_img = ImageClip(image_path).with_duration(duration)
    # Pastikan ukuran adalah integer untuk menghindari glitch pada cobaan sebelumnya
    prod_img = prod_img.resized(width=int(W * 0.9))
    prod_img = prod_img.with_position(('center', 'center'))
    
    # 5. SMART MASCOT (Switching berdasarkan kategori produk)
    # Gunakan path absolut file mascot.png yang telah dihasilkan
    FILE_MASCOT = "mascot.png"

    overlays = [bg, prod_img]
    if os.path.exists(FILE_MASCOT):
        mascot = ImageClip(FILE_MASCOT).with_duration(duration)
        mascot = mascot.resized(height=int(H * 0.3)) # Ukuran 30% layar
        # Animasi gerak tipis (bouncing)
        mascot = mascot.with_position(lambda t: (int(W*0.05), int(H*0.65 + (int(8 * (t % 0.4 > 0.2))))))
        overlays.append(mascot)
        print("Mascot narrator ditambahkan.")

    # 6. Text Overlay ala TikTok Pro (Fixing the Color Error)
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    
    # FIX: Gunakan Tuple (R, G, B, A) alih-alih string 'rgba' yang bikin error
    BG_TEKS = (0, 0, 0, 180) # Hitam transparan 70%

    # Teks atas (Hook, Kuning eye-catching)
    header = TextClip(
        text=data['nama'].upper(), font_size=60, color='yellow', font=FONT,
        method='caption', size=(int(W*0.8), None), bg_color='black'
    ).with_duration(duration).with_position(('center', 150))
    
    # Caption Narasi (upper case, putih)
    caption = TextClip(
        text=data['script'].upper(), font_size=40, color='white', font=FONT,
        method='caption', size=(int(W*0.85), None), bg_color=BG_TEKS
    ).with_duration(duration).with_position(('center', int(H-400)))

    overlays.extend([header, caption])

    # 7. Render Final HD
    final = CompositeVideoClip(overlays).with_audio(audio_clip)
    print("🎬 Rendering High Quality Video...")
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    if os.path.exists("produk.jpg"):
        create_pro_video("produk.jpg", "video_final.mp4")
        
        # Kirim ke Telegram
        print("Mengirim ke Telegram...")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
        with open("video_final.mp4", 'rb') as v:
            requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': '🚀 Konten Ber-Aura Siap Posting!'}, files={'video': v})
        print("Selesai!")
    
