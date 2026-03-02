import os
import urllib.request
import hashlib

# Configurações Era 2 - Archival (CICIDS2017)
URL_CICIDS = "http://205.174.165.80/CICDataset/CIC-IDS-2017/Dataset/MachineLearningCSV.zip"
EXPECTED_HASH = "869e5d4825d48348d7c4826d4827d483" # Hash de exemplo (substitua pelo real do ZIP)
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEST_DIR = os.path.join(base_dir, "data", "raw", "cicids2017")
FILE_NAME = "cicids_full.zip"

def verify_hash(file_path, expected_hash):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() == expected_hash

def download_progress(block_num, block_size, total_size):
    read_so_far = block_num * block_size
    if total_size > 0:
        percent = read_so_far * 1e2 / total_size
        print(f"\r progress: {percent:5.1f}%", end="")

def fetch_heavy_dataset():
    print("🏗️ Iniciando Download da Era 2 (CICIDS2017)...")
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    
    target_path = os.path.join(DEST_DIR, FILE_NAME)
    
    print(f"📡 Baixando de: {URL_CICIDS}")
    urllib.request.urlretrieve(URL_CICIDS, target_path, reporthook=download_progress)
    
    print(f"\n🛡️ Verificando integridade (SHA-256)...")
    if verify_hash(target_path, EXPECTED_HASH):
        print("✅ Hash validado! Arquivo íntegro.")
    else:
        print("❌ AVISO: Hash não confere. O arquivo pode estar corrompido.")

if __name__ == "__main__":
    fetch_heavy_dataset()