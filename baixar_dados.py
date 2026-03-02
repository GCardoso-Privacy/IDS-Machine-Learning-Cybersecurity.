"""
Script de Download Automatizado - Datasets de Cibersegurança

Este script faz o download do dataset 'NSL-KDD' diretamente para o seu disco.
É necessário ter a API do Kaggle configurada na sua máquina (`~/.kaggle/kaggle.json`).

Requisitos:
- kaggle

Uso:
    python baixar_dados.py

Nota: Recomenda-se configurar o 'caminho_ssd' para um disco com espaço suficiente.
"""
import kaggle
import os

# --- CONFIGURAÇÃO DO DIRETÓRIO DE DESTINO ---
# Define o caminho onde os dados serão salvos de forma relativa ao projeto
base_dir = os.path.dirname(os.path.abspath(__file__))
caminho_dados = os.path.join(base_dir, "data", "raw", "NSL-KDD")

# Cria a pasta destino se ela não existir (pra não dar erro)
os.makedirs(caminho_dados, exist_ok=True)

print(f"Iniciando download direto para: {caminho_dados}")

try:
    kaggle.api.authenticate()

    print("Baixando dataset 'helreshek/nsl-kdd'...")
    
    # Faz o download e extrai os dados
    kaggle.api.dataset_download_files('helreshek/nsl-kdd', path=caminho_dados, unzip=True)
    
    print("✅ Sucesso! Dados salvos localmente.")
    print("Arquivos:", os.listdir(caminho_dados))

except Exception as e:
    print(f"❌ Erro: {e}")