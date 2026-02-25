import requests
import pandas as pd
import time
import random
import json
from colorama import Fore, Style, init

init(autoreset=True)

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Datasets_Cybersecurity")

# Configurações
API_URL = "http://localhost:8000/predict"
DADOS_PATH = os.path.join(DATA_DIR, "dataset_limpo.parquet")

print(f"{Fore.CYAN}>>> INICIANDO SIMULADOR DE TRÁFEGO DE REDE <<<")

# 1. Carregar uma amostra de dados reais para usar de teste
try:
    print("⏳ Carregando munição (pacotes reais do dataset)...")
    df = pd.read_parquet(DADOS_PATH)
    # Pega 100 amostras aleatórias (Mistura de Benign e Ataques)
    amostra = df.sample(100)
    print(f"✅ {len(amostra)} pacotes carregados para teste.")
except Exception as e:
    print(f"❌ Erro ao ler dataset: {e}")
    exit()

# 2. Loop de Ataque
acertos = 0
erros = 0

print("-" * 60)
print(f"{'STATUS':<10} | {'PREVISÃO API':<20} | {'LATÊNCIA':<10} | {'REALIDADE'}")
print("-" * 60)

for index, row in amostra.iterrows():
    # Prepara o pacote (Remove a Label, pois o modelo não pode ver a resposta)
    label_real = row['Label']
    features = row.drop('Label').to_dict()
    
    payload = {"features": features}
    
    try:
        # Envia para o Sandbox (API)
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            resultado = response.json()
            predicao = resultado['prediction']
            acao = resultado['action']
            latencia = resultado['latency_ms']
            
            # Formatação Visual
            cor = Fore.GREEN if acao == "ALLOW" else Fore.RED
            status_icon = "🛡️ BLOQUEADO" if acao == "BLOCK" else "✅ PASSOU"
            
            print(f"{cor}{status_icon:<10} | {predicao:<20} | {latencia}ms    | (Era: {label_real})")
            acertos += 1
        else:
            print(f"{Fore.YELLOW}⚠️ Erro na API: {response.status_code}")
            erros += 1
            
    except Exception as e:
        print(f"❌ Servidor offline? {e}")
        break
    
    # Simula tráfego irregular (pausa aleatória entre requisições)
    time.sleep(random.uniform(0.05, 0.3))

print("-" * 60)
print(f"🏁 Teste finalizado. Requisições processadas: {acertos}")