import os
import sys
import time
import requests
import schedule
from pymongo import MongoClient
from dotenv import load_dotenv

# Força saída em UTF-8 para evitar erros com emojis
sys.stdout.reconfigure(encoding='utf-8')

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Carrega Variáveis de Ambiente
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
ALIENVAULT_API_KEY = os.getenv("ALIENVAULT_API_KEY")

if not ALIENVAULT_API_KEY:
    print(f"{Colors.WARNING}⚠️ AVISO: Chave ALIENVAULT_API_KEY não encontrada no .env! O script requer uma API Key Gratuita gerada em otx.alienvault.com.{Colors.ENDC}")
    # Não sai do script, apenas avisa (ou sai, se quisermos ser restritivos)
    exit(1)

# Conexão MongoDB
if os.path.exists('/.dockerenv'):
    MONGO_URI = "mongodb://admin:admin123@mongodb:27017/"
else:
    MONGO_URI = "mongodb://admin:admin123@localhost:27017/"
DB_NAME = "threat_intel"
COLLECTION_NAME = "alienvault_assets"

print(f"{Colors.OKCYAN}🔌 Conectando ao MongoDB ({COLLECTION_NAME})...{Colors.ENDC}")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Índice para Upsert rápido
collection.create_index([("ip", 1)], background=True, unique=True)
print(f"{Colors.OKGREEN}✅ Banco OTX AlienVault pronto!{Colors.ENDC}")

# Headers da API AlienVault
headers = {
    "X-OTX-API-KEY": ALIENVAULT_API_KEY
}

def job_otx_miner():
    print(f"\n{Colors.HEADER}🛸 Iniciando Mineração da AlienVault OTX (Threat Pulses)...{Colors.ENDC}")
    print(f"{Colors.WARNING}⏰ Início: {time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    
    # Endpoint de Pulses Modificados Recentemente
    url = "https://otx.alienvault.com/api/v1/pulses/subscribed?limit=50"
    
    total_saved = 0
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            pulses = data.get('results', [])
            print(f"{Colors.OKCYAN}📊 AlienVault retornou {len(pulses)} Campanhas (Pulses) Recentes.{Colors.ENDC}")
            
            for pulse in pulses:
                pulse_name = pulse.get('name', 'Unknown Threat')
                pulse_author = pulse.get('author_name', 'Unknown')
                pulse_tags = pulse.get('tags', [])
                indicators = pulse.get('indicators', [])
                
                # Vamos filtrar apenas os indicadores do tipo IPv4 para o Firewall
                ips = [ind for ind in indicators if ind.get('type') == 'IPv4']
                
                if not ips:
                    continue
                    
                print(f"{Colors.OKBLUE}🔍 Processando Campanha: {pulse_name} | {len(ips)} IPs nocivos identificados.{Colors.ENDC}")
                count = 0
                for indicator in ips:
                    ip_str = indicator.get('indicator')
                    title = indicator.get('title', '')
                    
                    doc = {
                        'ip': ip_str,
                        'source': 'AlienVault OTX',
                        'pulse_name': pulse_name,
                        'author': pulse_author,
                        'tags': pulse_tags,
                        'indicator_title': title,
                        'timestamp': time.time()
                    }
                    
                    # Salva no Banco de Dados CTI (Era 3)
                    collection.update_one(
                        {'ip': ip_str},
                        {'$set': doc},
                        upsert=True
                    )
                    count += 1
                total_saved += count
                
            print(f"{Colors.OKGREEN}✅ Sucesso absoluto! {total_saved} novos IPs nocivos do AlienVault adicionados ao arsenal.{Colors.ENDC}")
            
        elif response.status_code == 403:
            print(f"{Colors.FAIL}❌ Erro 403: Sua Chave do AlienVault OTX pode estar inválida.{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ Erro na API AlienVault: HTTP {response.status_code}{Colors.ENDC}")
            
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}❌ Falha de Rede ao acessar AlienVault: {e}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Erro inesperado: {e}{Colors.ENDC}")

    print(f"\n{Colors.HEADER}🏁 Mineração finalizada! Aguardando o ciclo noturno (24 horas)...{Colors.ENDC}")

if __name__ == "__main__":
    job_otx_miner()
    
    # Agendamento para coletar indicadores novos uma vez por dia (CTI não precisa ser por minuto)
    schedule.every(24).hours.do(job_otx_miner)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
