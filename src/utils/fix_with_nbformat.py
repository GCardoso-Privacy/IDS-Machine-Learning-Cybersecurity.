import nbformat

path = r'e:\Estudos_Cybersecurity\Notebooks\04_treinamento_modelo.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

new_source = """import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import gc
import joblib
import warnings
warnings.filterwarnings('ignore')

ARQUIVO_LIMPO = r"../data/processed/dataset_limpo.parquet"
MODELO_SAIDA = r"../data/processed/modelo_xgboost.json"
LABEL_ENCODER_FILE = r"../data/processed/label_encoder.joblib"

AMOSTRA = 0.5 

try:
    df = pd.read_parquet(ARQUIVO_LIMPO)
    
    # Filtro essencial contra bugs do CV no Scikit-Learn (classes diminutas)
    contagens = df['Label'].value_counts()
    raras = contagens[contagens < 4].index
    df = df[~df['Label'].isin(raras)]
    
    if AMOSTRA < 1.0:
        df = df.sample(frac=AMOSTRA, random_state=42)
    print(f"Dataset carregado: {df.shape[0]} linhas prontas.")
except Exception as e:
    exit()

y = df['Label']
X = df.drop(columns=['Label'])

del df
gc.collect()

le = LabelEncoder()
y_encoded = le.fit_transform(y)
joblib.dump(le, LABEL_ENCODER_FILE)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print(f"Treino: {X_train.shape[0]} | Teste: {X_test.shape[0]}")

# TREINAMENTO
base_model = xgb.XGBClassifier(
    objective='multi:softmax', 
    num_class=len(le.classes_), 
    n_jobs=-1,  # Usa nucleos internamente no xgboost
    tree_method='hist'
)

param_dist = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5],      
    'learning_rate': [0.05, 0.1],
    'gamma': [0.5, 1.0],    
    'min_child_weight': [1, 3]
}

random_search = RandomizedSearchCV(
    estimator=base_model,
    param_distributions=param_dist,
    n_iter=3, 
    scoring='f1_macro', 
    cv=3,
    verbose=2,
    random_state=42,
    n_jobs=1  # Evita duplicacao de RAM (MemoryError) pelo Scikit-Learn!
)

random_search.fit(X_train, y_train)

model = random_search.best_estimator_
print(f"Melhor rede parametrizada: {random_search.best_params_}")

model.save_model(MODELO_SAIDA)

# AVALIACAO
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=le.classes_))

plt.figure(figsize=(12, 10))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=le.classes_, yticklabels=le.classes_)
plt.title("Matriz XGBoost Otimizada")
plt.xlabel("Previsao")
plt.ylabel("Verdade")
plt.xticks(rotation=90)
plt.savefig("matriz_xgb_final.png")
"""

nb.cells[1].source = new_source

with open(path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)
print("Notebook salvo com prevencao de falhas.")
