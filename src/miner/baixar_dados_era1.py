import os
import sys

# Força saída em UTF-8 para evitar erros com emojis no console do Windows
sys.stdout.reconfigure(encoding='utf-8')

import requests
import zipfile

URL_NSL_KDD = "https://github.com/defcom17/NSL_KDD/archive/refs/heads/master.zip"
# Como este script está na RAIZ, usamos o caminho direto
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEST_DIR = os.path.join(base_dir, "data", "raw", "NSL-KDD")
ZIP_PATH = os.path.join(base_dir, "data", "raw", "nsl-kdd.zip")

def setup_nsl_kdd():
    print("🚀 Iniciando Setup da Era 1 (NSL-KDD)...")
    if not os.path.exists(os.path.dirname(ZIP_PATH)):
        os.makedirs(os.path.dirname(ZIP_PATH), exist_ok=True)
    
    print(f"📥 Baixando NSL-KDD do GitHub...")
    try:
        response = requests.get(URL_NSL_KDD, stream=True)
        response.raise_for_status()
        with open(ZIP_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("📦 Extraindo arquivos...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(ZIP_PATH))
        
        # O github zip extrai para NSL_KDD-master. Precisamos renomear para NSL-KDD/nsl-kdd
        extracted_folder = os.path.join(os.path.dirname(ZIP_PATH), "NSL_KDD-master")
        target_folder_base = os.path.join(base_dir, "data", "raw", "NSL-KDD")
        target_folder = os.path.join(target_folder_base, "nsl-kdd")
        
        if os.path.exists(extracted_folder):
            if not os.path.exists(target_folder_base):
                os.makedirs(target_folder_base, exist_ok=True)
            if os.path.exists(target_folder):
                import shutil
                shutil.rmtree(target_folder)
            os.rename(extracted_folder, target_folder)
            
        os.remove(ZIP_PATH)
        print(f"✅ NSL-KDD pronto em: {target_folder}")
    except Exception as e:
        print(f"❌ Erro no download/extração: {e}")

if __name__ == "__main__":
    setup_nsl_kdd()