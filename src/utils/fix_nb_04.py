import json

path = r'e:\Estudos_Cybersecurity\Notebooks\04_treinamento_modelo.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cell_source = """import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import gc
import joblib

# =============================================================================
# 1. CONFIGURAÇÕES
# =============================================================================
ARQUIVO_LIMPO = r"../data/processed/dataset_limpo.parquet"
MODELO_SAIDA = r"../data/processed/modelo_xgboost.json"
LABEL_ENCODER_FILE = r"../data/processed/label_encoder.joblib"

AMOSTRA_TREINO = 1.0 

print(">>> PREPARANDO AMBIENTE DE TREINAMENTO <<<")

try:
    df = pd.read_parquet(ARQUIVO_LIMPO)
    if AMOSTRA_TREINO < 1.0:
        df = df.sample(frac=AMOSTRA_TREINO, random_state=42)
        print(f"⚠️ Usando amostra de {AMOSTRA_TREINO*100}% dos dados.")
    print(f"✅ Dados Carregados: {df.shape[0]} linhas x {df.shape[1]} colunas")
except Exception as e:
    print(f"❌ Erro ao carregar: {e}")
    exit()

# =============================================================================
# 2. PREPARAÇÃO (X e y)
# =============================================================================
print("\\n🔧 Separando Features (X) e Alvo (y)...")

y = df['Label']
X = df.drop(columns=['Label'])

del df
gc.collect()

print("🔢 Codificando Labels (Benign -> 0, DDoS -> 1, ...)")
le = LabelEncoder()
y_encoded = le.fit_transform(y)
joblib.dump(le, LABEL_ENCODER_FILE)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print(f"📊 Treino: {X_train.shape[0]} amostras | Teste: {X_test.shape[0]} amostras")

# =============================================================================
# 3. TREINAMENTO (O MOMENTO MÁGICO)
# =============================================================================
print("\\n🚀 INICIANDO TREINAMENTO DO XGBOOST (Pode demorar!)...")
import warnings
warnings.filterwarnings('ignore')

base_model = xgb.XGBClassifier(
    objective='multi:softmax', 
    num_class=len(le.classes_), 
    n_jobs=-1,
    tree_method='hist'
)

param_dist = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.05, 0.1],
    'gamma': [0.1, 0.5, 1.0],
    'min_child_weight': [1, 3]
}

random_search = RandomizedSearchCV(
    estimator=base_model,
    param_distributions=param_dist,
    n_iter=5, # 5 combinacões limitadas
    scoring='f1_macro', # Métrica alvo alterada para F1
    cv=3,
    verbose=2,
    random_state=42,
    n_jobs=-1
)

random_search.fit(X_train, y_train)

model = random_search.best_estimator_
print(f"🌟 Melhores Hiperparâmetros: {random_search.best_params_}")
print("✅ MODELO TREINADO COM SUCESSO!")

model.save_model(MODELO_SAIDA)
print(f"💾 Cérebro salvo em: {MODELO_SAIDA}")

# =============================================================================
# 4. AVALIAÇÃO (A PROVA)
# =============================================================================
print("\\n📝 APLICANDO A PROVA (PREDIÇÃO NO TESTE)...")

y_pred = model.predict(X_test)

print("\\n📋 RELATÓRIO DE DESEMPENHO:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

plt.figure(figsize=(12, 10))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=le.classes_, yticklabels=le.classes_)
plt.title("Matriz de Confusão XGBoost")
plt.xlabel("O Modelo Previu...")
plt.ylabel("A Realidade Era...")
plt.xticks(rotation=90)
plt.savefig("matriz_xgb.png")
print("✅ Matriz de confusão salva em matriz_xgb.png")
# plt.show()
"""

nb['cells'][1]['source'] = [line + '\\n' for line in cell_source.split('\\n')][:-1]

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print("Notebook 04 Fixed and Refactored!")
