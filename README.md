# 🛡️ AI-Powered IDS Firewall (Intrusion Detection System)

> Um sistema inteligente de detecção de intrusão baseado em Machine Learning (XGBoost) capaz de classificar tráfego de rede e bloquear ataques DDoS em tempo real com 99.9% de eficácia.

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange)

## 📋 Sobre o Projeto
Este projeto utiliza datasets reais de cibersegurança (CICIDS2017 e CICDDoS2019) para treinar um modelo de Inteligência Artificial capaz de distinguir entre tráfego legítimo (Benign) e malicioso (DDoS, PortScan, Botnet, Web Attacks).

O objetivo é simular um **Next-Generation Firewall** que não depende apenas de regras estáticas, mas aprende padrões comportamentais de ataques.

## 🚀 Pipeline de Engenharia de Dados
O projeto foi estruturado em etapas profissionais de Big Data:

1.  **Ingestão:** Download e fusão de datasets massivos (CICIDS2017 + CICDDoS2019).
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
* **Manipulação de Dados:** Pandas, PyArrow, NumPy
* **Machine Learning:** XGBoost, Scikit-Learn
* **Visualização:** Matplotlib, Seaborn, Tqdm
* **Formato de Dados:** Parquet (Snappy Compression)

## 📂 Estrutura do Repositório
```text
├── Notebooks/
│   ├── 00_etl_conversao.ipynb       # Conversão CSV -> Parquet (Chunking)
│   ├── 01_preparacao_treino.ipynb   # Amostragem e fusão dos datasets
│   ├── 02_analise_exploratoria.ipynb# Análise de dados (EDA) e verificação de classes
│   ├── 03_limpeza_dados.ipynb       # Remoção de ruídos e features inúteis
│   ├── 04_treinamento_modelo.ipynb  # Treino do XGBoost e Avaliação
│   └── 05_simulacao_firewall.ipynb  # Simulação de detecção em tempo real
├── README.md                        # Documentação

🎮 Como Executar (Simulação)
Instale as dependências:

Bash
pip install pandas xgboost pyarrow scikit-learn tqdm colorama
Execute o notebook 05_simulacao_firewall.ipynb para ver o log de bloqueio em tempo real.