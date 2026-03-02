import json

def refactor_03():
    path = '../../notebooks/03_modelo.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    cell_0_source = """import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import time

# --- 1. CARREGAR OS DADOS PROCESSADOS ---
caminho_dados = r"..\Datasets_Cybersecurity\train_ready.csv"

print("â³ Carregando dataset processado...")
df = pd.read_csv(caminho_dados)

X = df.drop('target', axis=1)
y = df['target']

print(f"ðŸ“Š Dados carregados! Features: {X.shape[1]} | Linhas: {X.shape[0]}")

# --- 2. DIVISÃƒO TREINO vs TESTE ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print(f"âœ‚ï¸ DivisÃ£o feita: {len(X_train)} para treino, {len(X_test)} para teste.")

# --- 3. TREINAMENTO (A MÃ¡gica) ---
print("\\nðŸŒ² Iniciando treinamento da Random Forest com RandomizedSearchCV...")
inicio = time.time()

base_rf = RandomForestClassifier(random_state=42, n_jobs=-1)
param_rf = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30, None],
    'min_samples_leaf': [1, 2, 4]  # Regularizacao
}

rf_search = RandomizedSearchCV(
    estimator=base_rf,
    param_distributions=param_rf,
    n_iter=5,
    scoring='recall', # Foco em RECALL
    cv=3,
    verbose=2,
    random_state=42,
    n_jobs=-1
)

rf_search.fit(X_train, y_train)
modelo = rf_search.best_estimator_

fim = time.time()
print(f"ðŸŒŸ Melhores Params: {rf_search.best_params_}")
print(f"âœ… Modelo treinado em {fim - inicio:.2f} segundos!")

# --- 4. A PROVA FINAL ---
print("\\nðŸ“ Aplicando a prova nos dados de teste...")
previsoes = modelo.predict(X_test)
acuracia = accuracy_score(y_test, previsoes) * 100
print(f"ðŸ† AcurÃ¡cia do Modelo: {acuracia:.2f}%")
"""
    nb['cells'][0]['source'] = [line + '\n' for line in cell_0_source.split('\n')][:-1]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Notebook 03 refatorado.")

def refactor_04():
    path = '../../notebooks/04_treinamento_modelo.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    old_source = "".join(nb['cells'][1]['source'])
    old_lines = old_source.split('\n')
    part_before = []
    part_after = []
    state = 0
    for line in old_lines:
        if '3. TREINAMENTO (O MOMENTO MÃGICO)' in line:
            if part_before and part_before[-1].startswith('# ======'):
                part_before.pop()
            state = 1
        elif '4. AVALIAÃ‡ÃƒO (A PROVA)' in line:
            if part_after and part_after[-1].startswith('# ======'):
                part_after.pop()
            state = 2
            part_after.append('# =============================================================================')
            part_after.append(line)
        else:
            if state == 0:
                part_before.append(line)
            elif state == 2:
                part_after.append(line)
                
    new_train_block = """# =============================================================================
# 3. TREINAMENTO (O MOMENTO MÃGICO)
# =============================================================================
print("\\nðŸš€ INICIANDO TREINAMENTO DO XGBOOST (Pode demorar!)...")
from sklearn.model_selection import RandomizedSearchCV

base_model = xgb.XGBClassifier(
    objective='multi:softmax', 
    num_class=len(le.classes_), 
    n_jobs=-1,
    tree_method='hist'
)

param_dist = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],      # Controla profundidade 
    'learning_rate': [0.01, 0.05, 0.1],
    'gamma': [0.1, 0.5, 1.0],    # Regularizacao
    'min_child_weight': [1, 3, 5]
}

random_search = RandomizedSearchCV(
    estimator=base_model,
    param_distributions=param_dist,
    n_iter=5, 
    scoring='recall_macro', # Foco em Falsos Negativos multiclasse
    cv=3,
    verbose=2,
    random_state=42,
    n_jobs=-1
)

random_search.fit(X_train, y_train)
model = random_search.best_estimator_

print(f"ðŸŒŸ Melhores HiperparÃ¢metros: {random_search.best_params_}")
print("âœ… MODELO TREINADO COM SUCESSO!")

model.save_model(MODELO_SAIDA)
print(f"ðŸ’¾ CÃ©rebro salvo em: {MODELO_SAIDA}")

"""
    full_new_source = "\\n".join(part_before) + "\\n" + new_train_block + "\\n".join(part_after)
    nb['cells'][1]['source'] = [line + '\n' for line in full_new_source.split('\n')][:-1]

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Notebook 04 refatorado.")

refactor_03()
refactor_04()
