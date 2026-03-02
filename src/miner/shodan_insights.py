import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient

# Força saída em UTF-8 para evitar erros com emojis no console do Windows
sys.stdout.reconfigure(encoding='utf-8')

# Conexão com MongoDB
MONGO_URI = "mongodb://admin:admin123@localhost:27017/"
DB_NAME = "threat_intel"
COLLECTION_NAME = "shodan_assets"

print("🔌 Conectando ao MongoDB...")
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    # Test connection
    client.server_info()
    print("✅ Conexão bem-sucedida.")
except Exception as e:
    print(f"❌ Falha ao conectar no MongoDB: {e}")
    exit(1)

print("📥 Carregando dados do MongoDB...")
cursor = collection.find({})
data_list = []

for doc in cursor:
    shodan_data = doc.get('data', {})
    location = shodan_data.get('location', {})
    
    country_name = location.get('country_name')
    if not country_name:
        country_name = 'Unknown'
        
    os_name = shodan_data.get('os')
    if not os_name:
        os_name = shodan_data.get('product')
    if not os_name:
        os_name = 'Unknown'
        
    ip = doc.get('ip')
    port = doc.get('port')
    
    data_list.append({
        'ip': ip,
        'port': port,
        'country_name': country_name,
        'os': os_name
    })

df = pd.DataFrame(data_list)
if df.empty:
    print("⚠️ Nenhum dado encontrado no MongoDB. Execute o minerador primeiro.")
    exit(0)

print("🧹 Limpeza de dados em andamento...")
# Tratamento de dados (preenchendo vazios com 'Unknown')
df['country_name'] = df['country_name'].fillna('Unknown')
df['os'] = df['os'].fillna('Unknown')

# Criar diretório Modelos se não existir
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'Modelos'), exist_ok=True)
modelos_dir = os.path.join(os.path.dirname(__file__), '..', 'Modelos')

print("📊 Gerando gráficos...")
# 1. Top 10 Países
plt.figure(figsize=(10, 6))
top_countries = df['country_name'].value_counts().head(10)
top_countries.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Top 10 Países com Ativos Vulneráveis')
plt.xlabel('Nome do País')
plt.ylabel('Quantidade de Ativos')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(modelos_dir, 'top_countries.png'))
plt.close()

# 2. Distribuição de Sistemas Operacionais
plt.figure(figsize=(10, 6))
os_distribution = df['os'].value_counts().head(10) 
os_distribution.plot(kind='pie', autopct='%1.1f%%', startangle=140, colormap='Set3')
plt.title('Distribuição de Sistemas Operacionais (Top 10)')
plt.ylabel('')
plt.tight_layout()
plt.savefig(os.path.join(modelos_dir, 'os_distribution.png'))
plt.close()

# Resumo Estatístico Final
total_ips = len(df['ip'].unique())
total_records = len(df)
# Ignora 'Unknown' se possível, mas se for o único, usa 'Unknown'
most_frequent_country = top_countries.index[0] if not top_countries.empty else "N/A"
if len(top_countries) > 1 and most_frequent_country == 'Unknown':
    most_frequent_country = top_countries.index[1]

most_frequent_os = os_distribution.index[0] if not os_distribution.empty else "N/A"
if len(os_distribution) > 1 and most_frequent_os == 'Unknown':
    most_frequent_os = os_distribution.index[1]

print("\n" + "="*40)
print("=== RESUMO ESTATÍSTICO ===")
print("="*40)
print(f"Total de registros: {total_records}")
print(f"Total analisado: {total_ips} IPs distintos.")
print(f"País mais frequente mapeado: {most_frequent_country}")
print(f"SO mais comum sinalizado: {most_frequent_os}")
print("="*40)
print("✅ Os gráficos 'top_countries.png' e 'os_distribution.png' foram salvos na pasta 'Modelos/'.\n")
