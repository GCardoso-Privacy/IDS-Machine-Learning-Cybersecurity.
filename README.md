# 🛡️ AI-Powered Intrusion Detection System (IDS)

Um sistema de Detecção de Intrusão baseado em Machine Learning treinado no dataset **NSL-KDD**. O projeto simula um firewall inteligente capaz de classificar tráfego de rede como "Normal" ou "Ataque" com alta precisão.

## 📊 Resultados do Modelo (Random Forest)

| Métrica | Fase de Treino (Validada) | Fase de Teste (Dados Desconhecidos) |
| :--- | :---: | :---: |
| **Acurácia** | **99.89%** | **76.89%** |
| **Cenário** | Dados conhecidos (Hold-out 30%) | Ataques Zero-Day (KDDTest+) |

> **Insight de Segurança:** O modelo demonstrou excelente capacidade de bloquear ataques conhecidos (Precision 97%), mas, como esperado, a performance caiu ao enfrentar assinaturas de ataques inéditos no arquivo de teste final, simulando um cenário real de *Zero-Day exploits*.

## 🛠️ Pipeline do Projeto

O projeto foi dividido em 4 etapas estratégicas:

1.  **Exploração (`01_exploracao`):** Análise estatística do tráfego. Identificação de desbalanceamento e tipos de ataques (DoS Neptune, Satan, etc.).
2.  **Engenharia de Dados (`02_pre_processamento`):**
    * Limpeza de dados.
    * **One-Hot Encoding:** Transformação de variáveis categóricas (protocolos, serviços).
    * **Normalização (MinMax):** Escalonamento de dados para evitar viés numérico.
3.  **Modelagem (`03_modelo`):** Treinamento de um algoritmo **Random Forest Classifier**.
4.  **Auditoria (`04_prova_real`):** Teste de robustez contra o dataset `KDDTest+`, incluindo alinhamento de colunas para compatibilidade em produção.

## 🚀 Como Executar

1. Clone o repositório.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt