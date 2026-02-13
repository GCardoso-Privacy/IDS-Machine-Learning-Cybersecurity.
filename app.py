import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import joblib
import pandas as pd
import numpy as np
import time

# 1. Configuração da API
app = FastAPI(
    title="🛡️ AI-IDS Firewall API",
    description="API de Detecção de Intrusão usando XGBoost",
    version="1.0"
)

# 2. Carregar o Cérebro (Modelo e Encoder)
# Ajuste os caminhos se necessário
MODELO_PATH = "Datasets_Cybersecurity/modelo_xgboost.json"
ENCODER_PATH = "Datasets_Cybersecurity/label_encoder.joblib"

print("🔄 Carregando modelos...")
try:
    model = xgb.XGBClassifier()
    model.load_model(MODELO_PATH)
    le = joblib.load(ENCODER_PATH)
    print("✅ Sistema de Defesa Ativo e Carregado.")
except Exception as e:
    print(f"❌ Erro crítico ao carregar modelos: {e}")

# 3. Definir o formato dos dados de entrada (Schema)
# O usuário envia um JSON, nós validamos aqui
class NetworkPacket(BaseModel):
    # Dica: Em produção real, você listaria todos os 78 campos.
    # Aqui, vamos aceitar um dicionário genérico para facilitar o teste.
    features: dict

@app.get("/")
def home():
    return {"status": "online", "system": "AI-IDS Firewall v1.0"}

@app.post("/predict")
def predict_packet(packet: NetworkPacket):
    start_time = time.time()
    
    try:
        # 1. Converter JSON para DataFrame (formato que o XGBoost entende)
        # O modelo espera as colunas na mesma ordem do treino.
        # Aqui assumimos que o JSON já vem com as chaves certas.
        input_data = pd.DataFrame([packet.features])
        
        # 2. Fazer a Previsão
        pred_cod = model.predict(input_data)[0]
        pred_prob = model.predict_proba(input_data).max()
        pred_label = le.inverse_transform([pred_cod])[0]
        
        # 3. Regra de Negócio (Firewall)
        action = "ALLOW" if pred_label == "BENIGN" else "BLOCK"
        
        # 4. Logging de Performance (Latência)
        latency = round((time.time() - start_time) * 1000, 2) # ms
        
        return {
            "timestamp": pd.Timestamp.now().isoformat(),
            "prediction": pred_label,
            "confidence": float(round(pred_prob, 4)),
            "action": action,
            "latency_ms": latency
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Para rodar direto pelo Python: python app.py
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)