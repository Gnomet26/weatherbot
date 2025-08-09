from pyngrok import conf, installer
import os

def setup_ngrok():
    # Pyngrok konfiguratsiyasi
    ngrok_bin_path = os.path.expanduser("~/.ngrok2/ngrok")

    # Agar ngrok allaqachon yuklangan bo'lsa, qayta yuklamaymiz
    if os.path.exists(ngrok_bin_path):
        print(f"✅ Ngrok binari allaqachon mavjud: {ngrok_bin_path}")
        return

    print("⬇️ Ngrok binarini yuklab olyapmiz...")
    # Binarni yuklab olish (installer.download_ngrok)
    download_path = installer.install_ngrok(ngrok_bin_path)
    print(f"✅ Ngrok yuklandi: {download_path}")

if __name__ == "__main__":
    setup_ngrok()
