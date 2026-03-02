import requests
import pandas as pd
import time
import random
import json
import sys
from colorama import Fore, Style, init
from sklearn.metrics import f1_score, roc_auc_score

# Força a saída em UTF-8 no Windows para suportar emojis
sys.stdout.reconfigure(encoding='utf-8')

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
y_true_bin = []
y_pred_bin = []
y_prob_bin = []

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
            confianca = resultado.get('confidence', 0.0)
            
            # Formatação Visual
            cor = Fore.GREEN if acao == "ALLOW" else Fore.RED
            status_icon = "🛡️ BLOQUEADO" if acao == "BLOCK" else "✅ PASSOU"
            
            print(f"{cor}{status_icon:<10} | {predicao:<20} | {latencia}ms    | (Era: {label_real})")
            acertos += 1
            
            # Registro das métricas (Binário: 0 = Benign, 1 = Attack)
            y_true_bin.append(0 if label_real == 'BENIGN' else 1)
            y_pred_bin.append(0 if predicao == 'BENIGN' else 1)
            
            # Probabilidade do ataque para AUC-ROC
            prob_ataque = confianca if predicao != 'BENIGN' else (1.0 - confianca)
            y_prob_bin.append(prob_ataque)
        else:
            print(f"{Fore.YELLOW}⚠️ Erro na API: {response.text}")
            erros += 1
            
    except Exception as e:
        print(f"❌ Servidor offline? {e}")
        break
    
    # Simula tráfego irregular (pausa aleatória entre requisições)
    time.sleep(random.uniform(0.05, 0.3))

print("-" * 60)
print(f"🏁 Teste finalizado. Requisições processadas: {acertos}")

if y_true_bin and len(y_true_bin) == len(y_pred_bin):
    tp = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 1 and p == 0)
    
    acc = (tp + tn) / len(y_true_bin)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = f1_score(y_true_bin, y_pred_bin)
    # Proteção caso a amostra aleatória só tenha 1 classe
    auc = roc_auc_score(y_true_bin, y_prob_bin) if len(set(y_true_bin)) > 1 else 0.0
    
    print("\n" + "="*40)
    print("📊 RELATÓRIO DE EFICÁCIA (Binário)")
    print("="*40)
    print(f"Acurácia (Geral):   {acc:.2%}")
    print(f"Precisão (Ataques): {precision:.2%}")
    print(f"Recall   (Ataques): {recall:.2%}")
    print(f"F1-Score (Balance): {f1:.2%}")
    print(f"AUC-ROC  (Qualid.): {auc:.2%}")
    print("-" * 40)
    print("Matriz de Confusão:")
    print(f"✅ Passou Legítimo (TN): {tn}")
    print(f"🛡️ Bloqueou Ataque (TP): {tp}")
    print(f"⚠️ Falso Alarme    (FP): {fp}")
    print(f"❌ Deixou Passar   (FN): {fn}")
    print("="*40)