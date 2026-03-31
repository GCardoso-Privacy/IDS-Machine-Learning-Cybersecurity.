import requests
import pandas as pd
import time
import random
import json
import sys
from colorama import Fore, Style, init
from sklearn.metrics import f1_score, roc_auc_score

# ForÃ§a a saÃ­da em UTF-8 no Windows para suportar emojis
sys.stdout.reconfigure(encoding='utf-8')

init(autoreset=True)

import os
# A raiz fica três níveis acima (src/utils/attack_simulator.py -> src/utils -> src -> raiz)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# Configurações
API_URL = "http://localhost:8000/predict"
DADOS_PATH = os.path.join(DATA_DIR, "dataset_limpo.parquet")

print(f"{Fore.CYAN}>>> INICIANDO SIMULADOR DE TRÃFEGO DE REDE <<<")

# 1. Carregar uma amostra de dados reais para usar de teste
try:
    print("â³ Carregando muniÃ§Ã£o (pacotes reais do dataset)...")
    df = pd.read_parquet(DADOS_PATH)
    # Pega 100 amostras aleatÃ³rias (Mistura de Benign e Ataques)
    amostra = df.sample(100)
    print(f"âœ… {len(amostra)} pacotes carregados para teste.")
except Exception as e:
    print(f"âŒ Erro ao ler dataset: {e}")
    exit()

# 2. Loop de Ataque
acertos = 0
erros = 0
y_true_bin = []
y_pred_bin = []
y_prob_bin = []

print("-" * 60)
print(f"{'STATUS':<10} | {'PREVISÃƒO API':<20} | {'LATÃŠNCIA':<10} | {'REALIDADE'}")
print("-" * 60)

for index, row in amostra.iterrows():
    # Prepara o pacote (Remove a Label, pois o modelo nÃ£o pode ver a resposta)
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
            
            # FormataÃ§Ã£o Visual
            cor = Fore.GREEN if acao == "ALLOW" else Fore.RED
            status_icon = "ðŸ›¡ï¸ BLOQUEADO" if acao == "BLOCK" else "âœ… PASSOU"
            
            print(f"{cor}{status_icon:<10} | {predicao:<20} | {latencia}ms    | (Era: {label_real})")
            acertos += 1
            
            # Registro das mÃ©tricas (BinÃ¡rio: 0 = Benign, 1 = Attack)
            y_true_bin.append(0 if label_real == 'BENIGN' else 1)
            y_pred_bin.append(0 if predicao == 'BENIGN' else 1)
            
            # Probabilidade do ataque para AUC-ROC
            prob_ataque = confianca if predicao != 'BENIGN' else (1.0 - confianca)
            y_prob_bin.append(prob_ataque)
        else:
            print(f"{Fore.YELLOW}âš ï¸ Erro na API: {response.text}")
            erros += 1
            
    except Exception as e:
        print(f"âŒ Servidor offline? {e}")
        break
    
    # Simula trÃ¡fego irregular (pausa aleatÃ³ria entre requisiÃ§Ãµes)
    time.sleep(random.uniform(0.05, 0.3))

print("-" * 60)
print(f"ðŸ Teste finalizado. RequisiÃ§Ãµes processadas: {acertos}")

if y_true_bin and len(y_true_bin) == len(y_pred_bin):
    tp = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == 1 and p == 0)
    
    acc = (tp + tn) / len(y_true_bin)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = f1_score(y_true_bin, y_pred_bin)
    # ProteÃ§Ã£o caso a amostra aleatÃ³ria sÃ³ tenha 1 classe
    auc = roc_auc_score(y_true_bin, y_prob_bin) if len(set(y_true_bin)) > 1 else 0.0
    
    print("\n" + "="*40)
    print("ðŸ“Š RELATÃ“RIO DE EFICÃCIA (BinÃ¡rio)")
    print("="*40)
    print(f"AcurÃ¡cia (Geral):   {acc:.2%}")
    print(f"PrecisÃ£o (Ataques): {precision:.2%}")
    print(f"Recall   (Ataques): {recall:.2%}")
    print(f"F1-Score (Balance): {f1:.2%}")
    print(f"AUC-ROC  (Qualid.): {auc:.2%}")
    print("-" * 40)
    print("Matriz de ConfusÃ£o:")
    print(f"âœ… Passou LegÃ­timo (TN): {tn}")
    print(f"ðŸ›¡ï¸ Bloqueou Ataque (TP): {tp}")
    print(f"âš ï¸ Falso Alarme    (FP): {fp}")
    print(f"âŒ Deixou Passar   (FN): {fn}")
    print("="*40)