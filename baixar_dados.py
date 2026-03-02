import os
import requests
import zipfile

# Configurações Era 1 - Baseline (NSL-KDD)
URL_NSL_KDD = "https://archive.ics.uci.edu/static/public/183/nsl+kdd.zip"
base_dir = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.join(base_dir, "data", "raw")
ZIP_PATH = os.path.join(DEST_DIR, "nsl-kdd.zip")

def setup_nsl_kdd():
    print("🚀 Iniciando Setup da Era 1 (NSL-KDD)...")
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    
    print(f"📥 Baixando NSL-KDD...")
    response = requests.get(URL_NSL_KDD, stream=True)
    with open(ZIP_PATH, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("📦 Extraindo arquivos...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(DEST_DIR)
    
    os.remove(ZIP_PATH)
    print(f"✅ NSL-KDD pronto em: {DEST_DIR}")

if __name__ == "__main__":
    setup_nsl_kdd()