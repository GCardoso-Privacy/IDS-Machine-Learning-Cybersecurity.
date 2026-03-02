# 🛡️ AI-Powered IDS Firewall: Uma Evolução em Engenharia de Dados & Threat Intelligence

> **Um Case de Estudo em Cibersegurança Adaptativa:** De datasets estáticos à mineração de inteligência em tempo real com XGBoost, FastAPI e MongoDB.

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange)
![FastAPI](https://img.shields.io/badge/API-FastAPI-green)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED)

## 📖 1. Introdução: O Desafio do IDS Adaptativo

O cenário de ameaças cibernéticas não é estático; ele sofre mutações diárias. Firewalls tradicionais baseados em assinaturas e regras fixas tornam-se obsoletos assim que um novo vetor de ataque (*Zero-Day*) é descoberto. 

O objetivo central deste projeto foi construir um **Next-Generation Intrusion Detection System (IDS)** verdadeiramente adaptável. Mais do que treinar um modelo de Inteligência Artificial para classificar tráfego, este projeto é uma jornada arquitetural: a transição sistemática do uso de bases de dados acadêmicas estáticas para a arquitetura de **Engenharia de Dados em Tempo Real**, criando um organismo digital que "aprende" minerando a própria internet.

---

## ⏳ 2. A Evolução do Pipeline de Dados (Timeline)

A estratégia de dados foi estruturada e desenvolvida ao longo de 3 grandes eras tecnológicas, refletindo desafios reais de maturidade de software:

### 🏛️ Era 1: Fundamentos e Baseline (NSL-KDD)
A jornada do projeto começou com o estudo das fundações da detecção de intrusão usando o clássico dataset acadêmico **NSL-KDD**. Esta fase serviu como laboratório para validar algoritmos classificadores básicos (Random Forest) e compreender a mecânica das *features* de redes TCP/IP (Flags, duração da conexão, taxa de bytes).
* **Limitação:** Os padrões de ataque (como o antigo 'Smurf') não refletiam o tráfego da internet moderna.

### 🌊 Era 2: Big Data, Realismo e Gargalos de Memória (CICDDoS2019 / CICIDS2017)
O salto para a realidade moderna. O modelo foi migrado para datasets contemporâneos contendo a exata topologia de infecções reais em alta escala (DDoS, Botnets, Web Attacks).
* **Desafio de Engenharia:** Lidar com a extração de *PCAPs* convertidos gerou gigantescos CSVs de **8GB+**. Carregá-los diretamente em RAM causava exaustão de memória no sistema.
* **A Solução:** O projeto implementou pipelines de conversão de **CSV para Parquet** (`notebooks/00_etl_conversao.ipynb`) utilizando processamento via *chunking* (PyArrow/Pandas). O tamanho dos dados foi reduzido massivamente, preservando a integridade para o treinamento do modelo **XGBoost Classifier**.

### 🚀 Era 3: Autonomia & Threat Intelligence (Shodan + MongoDB)
O patamar atual. Compreendeu-se que treinar modelos com dados "congelados no tempo" (por mais recentes que fossem os datasets) sempre manteria a defesa um passo atrás dos atacantes. A meta evoluiu para a **Criação de um Dataset Próprio e Dinâmico**.
* **Como funciona:** O foco deixou os *CSV*s e introduziu integrações ativas à API Acadêmica do **Shodan**. Foram desenvolvidas rotinas Python (`src/miner/shodan_continuous_miner.py`) que mineram ininterruptamente a internet em busca de servidores expostos (ex: instâncias MongoDB e portas Telnet vulneráveis).
* **Armazenamento:** Esses *assets* reais, compostos de banners de rede e metadados de vulnerabilidades (CVEs), são agora injetados ao vivo e persistidos estruturalmente no banco **MongoDB** da arquitetura principal.

---

## ⚙️ 3. Justificativa Técnica: Por que o MongoDB?

A adoção do MongoDB (NoSQL) na "Era 3" foi uma decisão de engenharia deliberada e crucial, e não apenas uma escolha estética:

1. **Schema-Less para Banners JSON:** As respostas (banners) da API Shodan são strings ricas em JSON, altamente aninhadas e variáveis de dispositivo para dispositivo. Mapeá-las rigidamente para as tabelas de um banco SQL (PostgreSQL/MySQL) criaria um *overhead* de manutenção insustentável. O formato de documento (BSON) do MongoDB encapsula perfeitamente a volatilidade dessas respostas de rede nativamente.
2. **Resiliência e Microserviços (Docker):** Rodar o banco conteinerizado garante isolamento, deploys automáticos em novos nós e recuperação à falha, imune ao estado do sistema *host*.
3. **Superando Gargalos Reais (O Patch de Sanitização):**  
   Durante a ingestão em tempo real de grandes lotes (upserts massivos), o sistema enfrentou crashes silenciosos na conversão BSON (*BSON 8-byte integer limits exceeded*) e o bloqueio de chaves contendo pontos ou cifrões, herdadas nativamente de bibliotecas de rede em JavaScript reportadas pelo Shodan. 
   **A solução de Engenharia:** O patch implementado atua como um sanitizador recursivo customizado de estruturas de dados logo antes da camada do driver do `pymongo`. Ele substitui proativamente chaves defeituosas e converte dinamicamente tipos gigantes (*integers* fora do limite) para *floats* ou *strings*. Isso mitiga a falha de overflow em inteiros BSON de 64 bits, salvando o fluxo do pipeline em tempo real sem interrupções e sem descartar lotes inteiros de inteligência.

---

## 👁️‍🗨️ 4. Visualização de Inteligência (Insights Ativos)

Através do script `shodan_insights.py`, em vez de armazenar logs passivos, o sistema extrai cenários geopolíticos baseados num algoritmo não-supervisionado (K-Means) de clusterização:

### Geopolítica de Vulnerabilidades IoT
Distribuição em tempo real dos serviços críticos minerados pelo pool base do Shodan.
> ![Top Countries](/reports/figures/top_countries.png)

### Sistemas Operacionais na Linha de Frente
Distribuição de Sistemas Operacionais relatados dos Assets na rede.
> ![OS Distribution](/reports/figures/os_distribution.png)

### Clusters de Risco K-Means (Ameaças x Servidores Seguros)
> ![Cluster K-Means](/reports/figures/shodan_clusters.png)

---

## 🛠️ 5. Deployment & Setup Completo

Abaixo as instruções claras e seqüenciais para compor a arquitetura defensiva e de mineração:

### Passo Zero: Requerimentos Iniciais
1. Ative o Python VENV (`python -m venv venv`)
2. Instale as dependências com `pip install -r requirements.txt`
3. Crie o arquivo `.env` contendo a `SHODAN_API_KEY`.

### 🗄️ Iniciar o Cérebro de Persistência (Docker MongoDB)
Suba o servidor NoSQL do módulo Threat Intelligence. Pode-se utilizar o `docker-compose.yml` da pasta `docker/` ou rodar manualmente:
```bash
docker run -d --name mongo-threat-intel -p 27017:27017 --restart unless-stopped mongo:latest
```

### 📡 Ativar Operações de Threat Intelligence Ao Vivo
Alimente o pipeline minerando dados da borda da internet.
**1. Ativar Minerador (Deploy in Background):**
Busca em janelas de 12 horas por servidores sensíveis e executa os Upserts de forma sanitizada.
```bash
python src/miner/shodan_continuous_miner.py
```

**2. Gerar Insights:**
Compile o estado atual do banco para os gráficos exibidos nesta página.
```bash
python src/miner/shodan_insights.py
```

### 🚦 O Firewall de Produção (XGBoost) e Execução de Testes
Para inicializar o produto principal defensivo (O Sistema IDS):
1. Gere os Modelos (Apenas execute de `notebooks/00` a `04` se for o primeiro deploy) para o XGBoost derivar do treino local de base.
2. Inicie o Next-Gen Firewall em servidor FastAPI na porta `:8000`:
```bash
docker build -t ai-ids-firewall -f docker/Dockerfile .
docker run -v ./data:/app/data -v ./models:/app/models -p 8000:8000 ai-ids-firewall
```
3. Abra um terminal adjacente e teste a proteção real realizando testes de estresse com a simulação de pacotes parquets:
```bash
# Nota: certifique-se de que os utilitários de simulação estejam acessíveis
python src/utils/simulator.py
```
> Receba o feedback em tempo real para verificar se a conexão foi listada como **ALLOW** ou **BLOCK**, balizada pela análise de predição comportamental da IA.

---

### 🧽 Organização do Projeto
Para manter a estrutura de diretórios limpa, organizando dados brutos, processados, cadernos e scripts, execute periodicamente o script padrão de padronização:
```powershell
.\organizar_projeto.ps1
```
