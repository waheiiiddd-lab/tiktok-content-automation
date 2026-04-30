import os
import requests
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip

# Ambil kredensial dari GitHub Secrets
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def create_video_affiliate(image_path, product_name, output_path):
    duration = 16 # Durasi aman untuk Affiliate
    
    # 1. Load Gambar & Buat Efek Zoom
    clip = ImageClip(image_path).set_duration(duration)
    # Animasi Zoom: dari ukuran 1.0 ke 1.15
    clip = clip.resize(lambda t: 1 + 0.01*t) 
    
    # 2. Narasi AI (Sederhana)
    narasi = (f"Lagi cari {product_name}?\n"
              f"Kualitas terbaik & harga terjangkau!\n"
              f"Cek link di bio/keranjang kuning ✨")

    # 3. Tambahkan Teks ke Video
    txt_clip = TextClip(narasi, fontsize=40, color='white', font='Arial', 
                        method='caption', size=(clip.w*0.8, None), bg_color='black')
    txt_clip = txt_clip.set_position(('center', 0.7, True)).set_duration(duration).set_opacity(0.8)
    
    # 4. Render
    final_video = CompositeVideoClip([clip.set_position("center"), txt_clip])
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio=False)

def send_to_telegram(video_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(video_path, 'rb') as v:
        requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': 'Video siap di-upload!'}, files={'video': v})

if __name__ == "__main__":
    # Pastikan ada file 'produk.jpg' di folder repo kamu
    if os.path.exists("produk.jpg"):
        create_video_affiliate("produk.jpg", "Produk Rekomendasi", "hasil_konten.mp4")
        send_to_telegram("hasil_konten.mp4")
  
