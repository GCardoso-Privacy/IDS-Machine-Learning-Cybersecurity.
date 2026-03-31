import os
import sys
import shutil

# Força saída em UTF-8 para evitar erros com emojis no console do Windows
sys.stdout.reconfigure(encoding='utf-8')

try:
    import kagglehub
except ImportError:
    print("❌ A biblioteca 'kagglehub' não está instalada. Execute: pip install kagglehub")
    sys.exit(1)

# O script está na raiz (e:\Estudos_Cyber_Oficial)
base_dir = os.path.dirname(os.path.abspath(__file__))

DATASETS = {
    "CICIDS2017": {
        "slug": "chethuhn/network-intrusion-dataset",
        "dest": os.path.join(base_dir, "data", "raw", "CICIDS2017")
    },
    "CICDDoS2019": {
        "slug": "dhoogla/cicddos2019",
        "dest": os.path.join(base_dir, "data", "raw", "CICDDoS2019", "Treino")
    }
}

def copy_contents(src, dst):
    """Copia o conteúdo do diretório src para dst ou arquivo src para dst."""
    if not os.path.exists(dst):
        os.makedirs(dst)
        
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

def fetch_via_kagglehub():
    print("🚀 Iniciando Download via kagglehub (Era 3)...")
    
    for name, info in DATASETS.items():
        dest_path = info["dest"]
        slug = info["slug"]
        
        print(f"\n📥 Baixando dataset [{name}] do Kagglehub (Slug: {slug})...")
        try:
            # Baixa o dataset
            path = kagglehub.dataset_download(slug)
            print(f"✅ Download concluído no cache: {path}")
            
            print(f"Copiando arquivos para {dest_path}...")
            copy_contents(path, dest_path)
            
            print(f"✅ {name} copiado com sucesso para a pasta do projeto!")
        except Exception as e:
            print(f"❌ Erro ao baixar ou copiar {name}: {e}")

if __name__ == "__main__":
    fetch_via_kagglehub()