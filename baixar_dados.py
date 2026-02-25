import os
import requests
import zipfile
import hashlib
from tqdm import tqdm

# =============================================================================
# CONFIGURAÇÃO DE LINKS E DIRETÓRIOS
# =============================================================================
DATASET_DIR = "Datasets_Cybersecurity"

# URLs oficiais (ou mirrors estáveis) dos datasets
URLS = {
    "CICIDS2017": {
        "url": "http://205.174.165.80/CICDataset/CIC-IDS-2017/Dataset/CIC-IDS-2017-MachineLearningCSV.zip",
        "filename": "CIC-IDS-2017.zip",
        "extract_path": os.path.join(DATASET_DIR, "CICIDS2017")
    },
    # Nota: O CICDDoS2019 é muito grande e dividido em partes, aqui colocamos um exemplo
    # de como seria a automação para a parte de CSVs de Treino.
    "CICDDoS2019_Part1": {
        "url": "http://205.174.165.80/CICDataset/CICDDoS2019/Dataset/CSV-01-12/01-12.zip",
        "filename": "CICDDoS2019_Treino.zip",
        "extract_path": os.path.join(DATASET_DIR, "CICDDoS2019", "Treino"),
        "hash_esperado": "" # TODO: Inserir hash SHA256 real após o primeiro download validado
    }
}

def baixar_arquivo(url, destino):
    """Baixa um arquivo com barra de progresso."""
    if os.path.exists(destino):
        print(f"✅ Arquivo já existe: {destino}")
        return

    print(f"⬇️ Baixando: {url}")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destino, 'wb') as file, tqdm(
        desc=os.path.basename(destino),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def extrair_zip(arquivo_zip, destino):
    """Extrai o arquivo ZIP."""
    print(f"📦 Extraindo {arquivo_zip} para {destino}...")
    with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
        zip_ref.extractall(destino)
    print("✅ Extração concluída.")

def verificar_hash(arquivo_path, hash_esperado):
    """Verifica se o arquivo baixado não foi corrompido ou alterado (Man-in-the-Middle)."""
    sha256_hash = hashlib.sha256()
    with open(arquivo_path, "rb") as f:
        # Lê o arquivo em blocos para não estourar a RAM
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    hash_calculado = sha256_hash.hexdigest()
    if hash_calculado == hash_esperado:
        print("✅ Hash Verificado: Integridade garantida.")
        return True
    else:
        print(f"❌ PERIGO: Hash inválido! Esperado: {hash_esperado}, Obtido: {hash_calculado}")
        return False

# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    # Cria a pasta base se não existir
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

    print(">>> INICIANDO PIPELINE DE INGESTÃO DE DADOS <<<")
    
    for nome, dados in URLS.items():
        print(f"\nProcessando {nome}...")
        
        # Caminho completo do arquivo zip
        caminho_zip = os.path.join(DATASET_DIR, dados["filename"])
        
        # 1. Download
        try:
            baixar_arquivo(dados["url"], caminho_zip)
            
            # Validação de Segurança (Hash)
            # Como exemplo, se houver um hash esperado configurado, validamos antes de extrair.
            if dados.get("hash_esperado"):
                seguro = verificar_hash(caminho_zip, dados["hash_esperado"])
                if not seguro:
                    print("⚠️ Extração abortada por falha de integridade.")
                    continue
            else:
                print("ℹ️ Aviso: Hash não configurado. Verificação ignorada para este arquivo.")
            
            # 2. Extração
            if not os.path.exists(dados["extract_path"]):
                extrair_zip(caminho_zip, dados["extract_path"])
            else:
                print(f"✅ Pasta de destino já existe: {dados['extract_path']}")
                
        except Exception as e:
            print(f"❌ Erro ao processar {nome}: {e}")
            print("   (Nota: Links acadêmicos podem ficar offline. Verifique a VPN ou proxy.)")

    print("\n🏁 Ingestão Finalizada! Dados prontos para o ETL.")