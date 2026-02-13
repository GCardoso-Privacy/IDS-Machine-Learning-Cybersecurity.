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

> **⚠️ Nota sobre a Acurácia em Produção:**
> O desempenho de **99.99%** reflete a natureza controlada e sintética dos datasets acadêmicos (CICIDS). Em um ambiente corporativo real, com tráfego ruidoso e imprevisível, espera-se uma redução natural dessas métricas.
> Para mitigar *Overfitting*, features específicas de topologia (como IPs de Origem/Destino e Timestamps exatos) foram removidas intencionalmente durante o treinamento.

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

## 🎮 Como Executar

### 1️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

### 2️⃣ Rodar a API (Firewall)

```bash
python app.py
```

O servidor iniciará em:  
👉 http://localhost:8000  

Documentação Swagger:  
👉 http://localhost:8000/docs  

---

### 3️⃣ Rodar o Simulador de Ataques

(Em um novo terminal)

```bash
python attack_simulator.py
```
