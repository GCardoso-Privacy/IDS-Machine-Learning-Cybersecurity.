
# 🛡️ AI-Powered Intrusion Detection System (NIDS)

Um Sistema de Detecção de Intrusão de Rede (NIDS) desenvolvido com **Machine Learning** (Random Forest). O projeto simula um firewall inteligente capaz de classificar tráfego de rede como "Normal" ou "Ataque" (DoS, Probe, R2L, U2R) com alta precisão, focado em cenários de **Cibersegurança e Governança de Dados**.

## 📊 Resultados do Modelo

O projeto destaca a importância da generalização em modelos de IA aplicados à segurança.

| Métrica | Fase de Treino (Validada) | Fase de Teste (Dados Desconhecidos) |
| :--- | :---: | :---: |
| **Acurácia** | **99.89%** | **76.89%** |
| **Cenário** | Dados conhecidos (Hold-out 30%) | Ataques Zero-Day (KDDTest+) |
| **Precision (Ataque)** | ~99% | **97%** |

> **Insight de Segurança:** O modelo demonstrou excelente capacidade de bloquear ataques conhecidos. A variação de performance no set de teste (`KDDTest+`) reflete um cenário real de **Zero-Day exploits**, onde o modelo enfrentou assinaturas de ataques que nunca tinha visto antes, mantendo ainda assim uma alta taxa de precisão (baixo falso-positivo).

## 📂 Dataset & Instalação

O projeto utiliza o dataset **NSL-KDD** (University of New Brunswick). Por questões de boas práticas e licenciamento, os dados brutos não estão versionados neste repositório, mas você pode obtê-los facilmente de duas formas:

### Opção A: Download Automático (Recomendado) 🚀

Se você tiver Python instalado, execute o script auxiliar incluído na raiz:

```bash
python baixar_dados.py

```

### Opção B: Download Manual (Fallback) 📦

Caso o script falhe ou você prefira fazer manualmente:

**Nota:** Por questões de tamanho e licenciamento, os dados brutos não estão incluídos neste repositório.

1. **Download dos Dados:**
O projeto utiliza o dataset **NSL-KDD**, uma versão melhorada do KDD'99.
* Fonte Oficial: [Canadian Institute for Cybersecurity (UNB)](https://www.unb.ca/cic/datasets/nsl.html)
* Link Alternativo (Kaggle): [NSL-KDD Network Intrusion Detection](https://www.kaggle.com/datasets/hassan06/nslkdd)


2. **Estrutura de Pastas:**
Para que os notebooks funcionem corretamente, crie uma pasta chamada `Datasets_Cybersecurity` na raiz do projeto e descompacte os arquivos lá, seguindo esta estrutura:

```text
IDS-Machine-Learning-Cybersecurity/
├── Datasets_Cybersecurity/
│   └── NSL-KDD/
│       ├── KDDTrain+.txt
│       └── KDDTest+.txt

```

## 🛠️ Pipeline do Projeto

A solução foi construída seguindo um fluxo lógico de Ciência de Dados aplicada:

* **01_exploracao.ipynb:** Análise estatística do tráfego e identificação de desbalanceamento de classes.
* **02_pre_processamento.ipynb:** Limpeza de dados, One-Hot Encoding (tratamento de protocolos TCP/UDP/ICMP) e Normalização (MinMax).
* **03_modelo.ipynb:** Treinamento do algoritmo Random Forest Classifier e exportação do modelo (.pkl).
* **04_prova_real.ipynb:** Auditoria final simulando produção. Alinhamento de colunas entre treino/teste e avaliação contra o dataset "difícil" (Test+).

## 🚀 Como Executar

Clone o repositório:

```bash
git clone https://github.com/GCardoso-Privacy/IDS-Machine-Learning-Cybersecurity.git

```

Instale as dependências:

```bash
pip install -r requirements.txt

```

Garanta que os dados estão na pasta (via script ou manual).

Execute os notebooks na ordem numérica (01 a 04) ou carregue o modelo pronto da pasta `Modelos/`.

```

---


```