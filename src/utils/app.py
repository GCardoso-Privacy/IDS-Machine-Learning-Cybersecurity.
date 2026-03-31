import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import joblib
import pandas as pd
import numpy as np
import time
from typing import Dict, Optional
import pymongo

# 1. ConfiguraÃ§Ã£o da API
app = FastAPI(
    title="ðŸ›¡ï¸ AI-IDS Firewall API",
    description="API de DetecÃ§Ã£o de IntrusÃ£o usando XGBoost",
    version="1.0"
)

# 2. Carregar o CÃ©rebro (Modelo e Encoder)
import os
# Caminha para a raiz do projeto: src/utils/app.py -> src/utils -> src -> raiz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_DIR = os.path.join(BASE_DIR, "models")

MODELO_PATH = os.path.join(MODEL_DIR, "modelo_xgboost.json")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.joblib")

print("ðŸ”„ Carregando modelos...")
model = None
le = None
try:
    model = xgb.XGBClassifier()
    model.load_model(MODELO_PATH)
    le = joblib.load(ENCODER_PATH)
    print("âœ… Sistema de Defesa Ativo e Carregado.")
except Exception as e:
    print(f"âŒ Erro crÃ­tico ao carregar modelos: {e}")
    model = None
    le = None

# Configuração da Conexão com MongoDB (Banco da Era 3 - Shodan)
print("🔌 Conectando ao Banco de Threat Intelligence (MongoDB)...")
MONGO_URI = "mongodb://admin:admin123@localhost:27017/"
if os.path.exists('/.dockerenv'):
    MONGO_URI = "mongodb://admin:admin123@mongodb:27017/"

mongo_client = None
threat_intel_coll = None
alienvault_coll = None
try:
    mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    mongo_client.server_info() # Testa conexão
    threat_intel_coll = mongo_client["threat_intel"]["shodan_assets"]
    alienvault_coll = mongo_client["threat_intel"]["alienvault_assets"]
    print("✅ Conectado à Base de Dados de Threat Intelligence (Era 3).")
except Exception as e:
    print(f"⚠️ Aviso: Não foi possível conectar ao MongoDB (Era 3 desativada). Detalhes: {e}")


# 3. Definir o formato dos dados de entrada (Schema)
# O usuÃ¡rio envia um JSON, nÃ³s validamos aqui
class NetworkPacket(BaseModel):
    # IP de origem opcional para checagem na Camada 1 (Threat Intelligence)
    source_ip: Optional[str] = None
    # Dica: Em produção real, você listaria todos os 78 campos.
    # Aqui, garantimos que todos os valores sejam float para validação básica.
    features: Dict[str, float]

@app.get("/")
def home():
    return {"status": "online", "system": "AI-IDS Firewall v1.0"}

@app.post("/predict")
def predict_packet(packet: NetworkPacket):
    if model is None or le is None:
        raise HTTPException(
            status_code=503, 
            detail="ServiÃ§o indisponÃ­vel: O modelo de IA nÃ£o foi carregado. Certifique-se de executar o notebook de treinamento primeiro."
        )

    start_time = time.time()
    
    try:
        # =========================================================
        # CAMADA 1: CYBER THREAT INTELLIGENCE (Era 3 - Multi-Fontes)
        # Calcula um Risk Score de 0 a 100
        # =========================================================
        ip = packet.source_ip
        risk_score = 0
        cti_motivo = ""
        
        if ip and mongo_client is not None:
            # Fonte 1: AlienVault OTX (Indicadores Conhecidos)
            alien_data = alienvault_coll.find_one({"ip": ip})
            if alien_data:
                risk_score += 95
                cti_motivo = f"IP listado em campanhas maliciosas (AlienVault Pulse: {alien_data.get('pulse_name')}). "
                
            # Fonte 2: Shodan (Ativos Expostos e Vulneráveis)
            shodan_data = threat_intel_coll.find_one({"ip": ip})
            if shodan_data:
                # Verifica se existem CVEs (vulnerabilidades) relatadas no dado
                vulns = shodan_data.get('data', {}).get('vulns', {})
                if vulns:
                    risk_score += 90
                    cti_motivo += f"Shodan reporta CVEs ativas. "
                else:
                    risk_score += 60  # Ativo exposto (ex: porta 23 telnet / mongodb), mas sem exploits diretos
                    cti_motivo += f"Shodan reporta serviços críticos expostos. "
            
            risk_score = min(risk_score, 100) # Teto de 100
            
            # Regra de Bloqueio Imediato (Super Block - Nível Crítico)
            if risk_score >= 90:
                latency = round((time.time() - start_time) * 1000, 2)
                return {
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "prediction": "THREAT_INTEL_BLOCK",
                    "confidence": 1.0,
                    "action": "BLOCK",
                    "reason": cti_motivo,
                    "risk_score": risk_score,
                    "latency_ms": latency,
                    "layer": "Camada 1 (CTI / OTX+Shodan)"
                }

        # =========================================================
        # CAMADA 2: ANÁLISE COMPORTAMENTAL DE FLUXO (Era 1 e 2 - XGBoost)
        # =========================================================
        # 1. Converter JSON para DataFrame (formato que o XGBoost entende)
        # O modelo espera as colunas na mesma ordem do treino.
        # Aqui assumimos que o JSON já vem com as chaves certas.
        input_data = pd.DataFrame([packet.features])
        
        # 2. Fazer a Previsão
        pred_cod = model.predict(input_data)[0]
        pred_prob = model.predict_proba(input_data).max()
        pred_label = le.inverse_transform([pred_cod])[0]
        
        # 3. Regra de Negócio Padrão do Firewall
        action = "ALLOW" if pred_label == "BENIGN" else "BLOCK"
        layer_triggered = "Camada 2 (XGBoost)"
        
        # =========================================================
        # HARMONIZAÇÃO: SENSOR FUSION (Eras 2 + 3)
        # =========================================================
        # Se o modelo disser "ALLOW", mas o CTI avisou que o IP tem Risco Médio (Score >= 50).
        # Nós abaixamos a tolerância. O modelo precisa ter ALTA certeza para deixar passar.
        if action == "ALLOW" and risk_score >= 50:
            if pred_prob < 0.85: # Modelo confia menos de 85% que é benigno
                action = "BLOCK"
                pred_label = "SENSOR_FUSION_ANOMALY"
                cti_motivo = f"Suspicious IP (Risk {risk_score}) + Low Benign Confidence ({pred_prob:.2f})"
                layer_triggered = "Sensor Fusion (CTI + AI)"

        # 4. Logging de Performance (Latência)
        latency = round((time.time() - start_time) * 1000, 2) # ms
        
        resposta = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "prediction": pred_label,
            "confidence": float(round(pred_prob, 4)),
            "action": action,
            "latency_ms": latency,
            "risk_score": risk_score,
            "layer": layer_triggered
        }
        
        if cti_motivo and layer_triggered == "Sensor Fusion (CTI + AI)":
            resposta["reason"] = cti_motivo
            
        return resposta
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Para rodar direto pelo Python: python app.py
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)