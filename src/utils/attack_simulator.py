import requests
import pandas as pd
import time
import random
import json
import sys
from colorama import Fore, Style, init
from sklearn.metrics import f1_score, roc_auc_score
import pymongo

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

print("-" * 80)
print(f"{'STATUS':<15} | {'PREVISÃO API':<20} | {'LATÊNCIA':<8} | {'CAMADA':<15} | {'REALIDADE/ORIGEM'}")
print("-" * 80)

# TESTE ESPECIAL DA MUNIÇÃO DE PRECISÃO (ERA 3 - SHODAN)
print(f"\n{Fore.YELLOW}>>> INJETANDO TESTE DA CAMADA 1: IP VULNERÁVEL OBTIDO PELO SHODAN <<<{Style.RESET_ALL}")
try:
    mongo_client = pymongo.MongoClient("mongodb://admin:admin123@localhost:27017/", serverSelectionTimeoutMS=2000)
    threat_coll = mongo_client["threat_intel"]["shodan_assets"]
    bad_asset = threat_coll.find_one()  # Pega qualquer um que o Shodan minerou
    
    if bad_asset:
        bad_ip = bad_asset["ip"]
        # Pega uma amostra aleatória benigna
        row = amostra[amostra['Label'] == 'BENIGN'].iloc[0] if 'BENIGN' in amostra['Label'].values else amostra.iloc[0]
        features = row.drop('Label').to_dict()
        
        # Mas enviamos com o IP do Shodan
        payload = {"source_ip": bad_ip, "features": features}
        
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            resultado = response.json()
            acao = resultado['action']
            cor = Fore.MAGENTA if acao == "BLOCK" else Fore.GREEN
            layer = resultado.get('layer', 'Unknown')
            print(f"{cor}🔒 SUPER BLOCK  | {resultado['prediction']:<20} | {resultado['latency_ms']}ms   | {layer:<15} | (IP CTI: {bad_ip}){Style.RESET_ALL}")
        else:
            print("Erro API: ", response.text)
    else:
        print(f"⚠️ Banco Shodan vazio. Não é possível testar a Camada 1.")
except Exception as e:
    print(f"⚠️ Erro ao conectar no MongoDB para teste CTI: {e}")

time.sleep(1)
print(f"\n{Fore.CYAN}>>> INICIANDO TRÁFEGO COMUM (CAMADA 2 - COMPORTAMENTO) <<<{Style.RESET_ALL}")

for index, row in amostra.iterrows():
    # Prepara o pacote (Remove a Label, pois o modelo não pode ver a resposta)
    label_real = row['Label']
    features = row.drop('Label').to_dict()
    
    # Gera um IP aleatório falso para passar batido pela Camada 1
    random_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    
    payload = {"source_ip": random_ip, "features": features}
    
    try:
        # Envia para o Sandbox (API)
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            resultado = response.json()
            predicao = resultado['prediction']
            acao = resultado['action']
            latencia = resultado['latency_ms']
            confianca = resultado.get('confidence', 0.0)
            layer = resultado.get('layer', 'Desconhecida')
            
            # Formatação Visual
            cor = Fore.GREEN if acao == "ALLOW" else Fore.RED
            status_icon = "🛡️  BLOQUEADO" if acao == "BLOCK" else "✅ PASSOU"
            
            print(f"{cor}{status_icon:<15} | {predicao:<20} | {latencia}ms   | {layer:<15} | (Era: {label_real}){Style.RESET_ALL}")
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