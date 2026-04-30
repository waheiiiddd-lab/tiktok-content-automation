import os
import random
import requests
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips

# --- KONFIGURASI ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_dynamic_script(product_name):
    """
    Menghasilkan skrip yang berbeda-beda setiap kali dijalankan.
    Kamu bisa mengembangkan ini dengan API Gemini agar lebih 'pintar'.
    """
    templates = [
        {
            "hook": f"POV: Kamu baru nemu {product_name} yang lagi viral! 🔥",
            "body": "Gak nyangka banget kualitasnya sebagus ini dengan harga segini.",
            "cta": "Mumpung masih diskon, cek keranjang kuning sekarang! 🛒"
        },
        {
            "hook": f"Stop scroll! Kalian harus liat {product_name} ini.. 😱",
            "body": "Solusi buat kamu yang pengen tampil keren tapi budget pelajar.",
            "cta": "Klik keranjang kuning sebelum kehabisan stok! ✨"
        },
        {
            "hook": f"Racun TikTok hari ini: {product_name} check! ✨",
            "body": "Desainnya estetik banget dan multifungsi buat sehari-hari.",
            "cta": "Cek promo hari ini di keranjang kuning ya! 👇"
        }
    ]
    return random.choice(templates)

def create_segment(image_path, text, duration, zoom_type="in"):
    """Membuat potongan video dengan teks dan efek zoom."""
    clip = ImageClip(image_path).set_duration(duration)
    
    # Efek Gerakan (Zoom In atau Zoom Out)
    if zoom_type == "in":
        clip = clip.resize(lambda t: 1 + 0.04 * t)
    else:
        clip = clip.resize(lambda t: 1.2 - 0.04 * t)
    
    # Overlay Teks dengan Background Box agar mudah dibaca
    txt = TextClip(text, fontsize=45, color='white', font='Arial-Bold',
                   method='caption', size=(clip.w * 0.8, None), 
                   bg_color='rgba(0,0,0,0.6)')
    
    # Posisi teks sedikit di bawah tengah (aman dari UI TikTok)
    txt = txt.set_position(('center', 0.65, True)).set_duration(duration)
    
    return CompositeVideoClip([clip.set_position("center"), txt])

def build_full_video(image_path, product_name, output_path):
    print(f"Memproses konten untuk: {product_name}")
    script = get_dynamic_script(product_name)
    
    # Membagi 16 detik menjadi 3 bagian: Hook (4s), Body (8s), CTA (4s)
    segment_1 = create_segment(image_path, script['hook'], 4, "in")
    segment_2 = create_segment(image_path, script['body'], 8, "out")
    segment_3 = create_segment(image_path, script['cta'], 4, "in")
    
    final_video = concatenate_videoclips([segment_1, segment_2, segment_3])
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio=False)

def send_to_telegram(video_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(video_path, 'rb') as v:
        requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': '🚀 Konten siap posting!'}, files={'video': v})

if __name__ == "__main__":
    IMAGE_FILE = "produk.jpg"
    PRODUCT_NAME = "Produk Viral Ini" # Ubah manual atau ambil dari nama file
    OUTPUT = "tiktok_affiliate.mp4"
    
    if os.path.exists(IMAGE_FILE):
        build_full_video(IMAGE_FILE, PRODUCT_NAME, OUTPUT)
        send_to_telegram(OUTPUT)
    else:
        print("Sediakan file produk.jpg di folder!")
        
