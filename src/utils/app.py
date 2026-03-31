import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import joblib
import pandas as pd
import numpy as np
import time
from typing import Dict

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

# 3. Definir o formato dos dados de entrada (Schema)
# O usuÃ¡rio envia um JSON, nÃ³s validamos aqui
class NetworkPacket(BaseModel):
    # Dica: Em produÃ§Ã£o real, vocÃª listaria todos os 78 campos.
    # Aqui, garantimos que todos os valores sejam float para validaÃ§Ã£o bÃ¡sica.
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
        # 1. Converter JSON para DataFrame (formato que o XGBoost entende)
        # O modelo espera as colunas na mesma ordem do treino.
        # Aqui assumimos que o JSON jÃ¡ vem com as chaves certas.
        input_data = pd.DataFrame([packet.features])
        
        # 2. Fazer a PrevisÃ£o
        pred_cod = model.predict(input_data)[0]
        pred_prob = model.predict_proba(input_data).max()
        pred_label = le.inverse_transform([pred_cod])[0]
        
        # 3. Regra de NegÃ³cio (Firewall)
        action = "ALLOW" if pred_label == "BENIGN" else "BLOCK"
        
        # 4. Logging de Performance (LatÃªncia)
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