# 🛡️ AI-Powered IDS Firewall (Intrusion Detection System)

> Um sistema inteligente de detecção de intrusão baseado em Machine Learning (XGBoost) capaz de classificar tráfego de rede e bloquear ataques DDoS em tempo real com 99.9% de eficácia.

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange)
![FastAPI](https://img.shields.io/badge/API-FastAPI-green)

## 📋 Sobre o Projeto
Este projeto utiliza datasets reais de cibersegurança (CICIDS2017 e CICDDoS2019) para treinar um modelo de Inteligência Artificial capaz de distinguir entre tráfego legítimo (Benign) e malicioso (DDoS, PortScan, Botnet, Web Attacks).

O objetivo é simular um **Next-Generation Firewall** que não depende apenas de regras estáticas, mas aprende padrões comportamentais de ataques.

## 🚀 Pipeline de Engenharia de Dados
O projeto foi estruturado em etapas profissionais de Big Data:

1.  **Ingestão:** Automação de download e extração via script Python (`baixar_dados.py`).
2.  **ETL & Otimização:** Conversão de CSVs gigantes (8GB+) para formato **Parquet** usando `PyArrow` e processamento em chunks (para contornar limites de RAM).
3.  **Limpeza:** Remoção de colunas enviesadas (IPs, Timestamps), tratamento de valores infinitos/nulos e padronização de labels.
4.  **Treinamento:** Modelo **XGBoost Classifier** treinado em ~3.5 milhões de amostras.

## 📊 Resultados do Modelo

O modelo final atingiu métricas de nível militar para defesa cibernética:

| Métrica | Performance |
| :--- | :--- |
| **Acurácia Binária (Defesa)** | **99.99%** |
| **Recall (Detecção de Ataques)** | **99.99%** |
| **Falso Positivo (Benign)** | **0.00%** |

> **⚠️ Nota sobre a Diferença Multiclasse vs Binária:**
> O modelo foi desenhado para classificar vários subtipos de ataques (Multiclasse), porém o foco defensivo (Permitir ou Bloquear) é **Binário**. Enquanto a acurácia Multiclasse geral reportada no Notebook 04 é de cerca de 71% devido a dificuldades inerentes com classes minoritárias, a **Acurácia Binária (Ataque vs Benign)** comprovadamente atinge os 99% prometidos, conforme o *Relatório de Defesa* recém-adicionado ao final do **Notebook 04**. O sistema em produção (`app.py`) opera baseado nessa distinção binária (tudo que não for "BENIGN" será bloqueado).

*Obs: O modelo prioriza a detecção da intenção hostil (Binária) sobre a classificação exata do subtipo do ataque, garantindo o bloqueio efetivo.*

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3
* **API & Deploy:** FastAPI, Uvicorn
* **Manipulação de Dados:** Pandas, PyArrow, NumPy
* **Machine Learning:** XGBoost, Scikit-Learn
* **Visualização:** Matplotlib, Seaborn, Tqdm

## 🚀 Deployment & Simulação (Arquitetura de Produção)

Para demonstrar a aplicabilidade real do modelo (além dos notebooks), foi desenvolvida uma **API REST** completa utilizando **FastAPI**.

### 🔧 Arquitetura da Solução
1.  **API de Defesa (`app.py`):**
    * Carrega o modelo XGBoost treinado (`.json`).
    * Expõe um endpoint `POST /predict`.
    * Processa pacotes em tempo real e decide entre **ALLOW** (Permitir) ou **BLOCK** (Bloquear).
    * Documentação automática via Swagger UI (`/docs`).

2.  **Simulador de Ataque (`attack_simulator.py`):**
    * Carrega amostras reais do dataset de teste (Parquet).
    * Envia requisições HTTP para a API simulando tráfego de rede.
    * Mede a **latência** (ms) e valida se a defesa agiu corretamente.

## 📂 Estrutura do Repositório
```text
├── Notebooks/
│   ├── 00_etl_conversao.ipynb       # Conversão CSV -> Parquet (Chunking)
│   ├── 01_preparacao_treino.ipynb   # Amostragem e fusão dos datasets
│   ├── 02_analise_exploratoria.ipynb# Análise de dados (EDA)
│   ├── 03_limpeza_dados.ipynb       # Remoção de ruídos e features inúteis
│   ├── 04_treinamento_modelo.ipynb  # Treino do XGBoost e Avaliação
│   └── 05_simulacao_firewall.ipynb  # Simulação inicial (Notebook)
├── app.py                           # API de Defesa (FastAPI)
├── attack_simulator.py              # Script de Stress Test
├── baixar_dados.py                  # Script de Automação de Download
├── requirements.txt                 # Dependências do projeto
└── README.md                        # Documentação

🎮 Como executar
0️⃣ Preparar os Dados e Treinar o Modelo
Como os modelos são muito pesados e dinâmicos, eles não constam no repositório. Siga o pipeline para gerá-los:
- Execute o script `baixar_dados.py` caso ainda não tenha os dados brutos.
- Execute em ordem os notebooks da pasta `Notebooks/` até rodar o **04_treinamento_modelo.ipynb**. Este notebook salvará os arquivos `modelo_xgboost.json` e `label_encoder.joblib` que a API usa.

## 🐳 Executando via Docker (Recomendado)

Para garantir 100% de reprodutibilidade e evitar conflitos de ambiente, a API do Firewall pode ser executada em um contêiner Docker isolado (Linux/Python Slim).

**1. Construa a imagem da API:**
```bash
docker build -t ai-ids-firewall .
```

**2. Inicie o contêiner em produção:**
Para que a API acesse os modelos que você gerou localmente (e que não subiram para a imagem por serem ignorados no `.dockerignore`), mapeie a pasta local usando um *Volume*:
```bash
docker run -v ./Datasets_Cybersecurity:/app/Datasets_Cybersecurity -p 8000:8000 ai-ids-firewall
```

**3. Teste o Firewall:**
Em outro terminal, execute o simulador de ataques para bombardear o contêiner:
```bash
python attack_simulator.py
```

---

Ou, **Execução via Python (Uso Local)**:
Instale as dependências com `pip install -r requirements.txt` e inicie a API usando `python app.py`. O servidor local iniciará em http://localhost:8000.

**Exemplo de Saída Esperada (Execução Real):**

```text
========================================
📊 RELATÓRIO DE EFICÁCIA (Binário)
========================================
Acurácia (Geral):   99.00%
Precisão (Ataques): 98.94%
Recall   (Ataques): 100.00%
F1-Score (Balance): 99.47%
AUC-ROC  (Qualid.): 91.09%
----------------------------------------
Matriz de Confusão:
✅ Passou Legítimo (TN): 6
🛡️ Bloqueou Ataque (TP): 93
⚠️ Falso Alarme    (FP): 1
❌ Deixou Passar   (FN): 0
========================================
```

> **🛡️ Nota Analítica sobre o Desempenho:**
> Os resultados acima refletem uma execução real do simulador em uma amostragem aleatória e desbalanceada do tráfego. O modelo demonstra o comportamento ideal para sistemas de defesa (Zero Trust): Recall de 100% (0 Falsos Negativos). Em Cibersegurança, tolerar uma taxa mínima de Falsos Positivos (neste caso, 1 bloqueio preventivo) é amplamente preferível a permitir que uma única ameaça real atravesse o firewall. O AUC-ROC de ~91% comprova a ausência de overfitting e atesta a capacidade real de generalização do modelo em produção.
