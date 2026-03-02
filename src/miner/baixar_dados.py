import kaggle
import os

# --- CONFIGURAÇÃO DO SSD ---
# 1. Cole o caminho do seu SSD aqui dentro das aspas.
# IMPORTANTE: Coloque um 'r' na frente das aspas para o Python aceitar as barras do Windows.
caminho_ssd = r"E:\Datasets_Cybersecurity\NSL-KDD" 

# Cria a pasta no SSD se ela não existir (pra não dar erro)
os.makedirs(caminho_ssd, exist_ok=True)

print(f"Iniciando download direto para o SSD em: {caminho_ssd}")

try:
    kaggle.api.authenticate()

    print("Baixando dataset 'helreshek/nsl-kdd'...")
    
    # Aqui mudamos para usar a variável do SSD
    kaggle.api.dataset_download_files('helreshek/nsl-kdd', path=caminho_ssd, unzip=True)
    
    print("✅ Sucesso! Dados salvos no disco externo.")
    print("Arquivos:", os.listdir(caminho_ssd))

except Exception as e:
    print(f"❌ Erro: {e}")