import os
import sys
import time
import schedule
import shodan
from pymongo import MongoClient
from dotenv import load_dotenv

# Força saída em UTF-8 para evitar erros com emojis no console do Windows
sys.stdout.reconfigure(encoding='utf-8')

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Carrega as variáveis do .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

if not SHODAN_API_KEY:
    # Caso o Load Dotenv falhe em um nível específico, tenta pegar da variável de ambiente ambiente diretamente
    print(f"{Colors.FAIL}❌ Erro: SHODAN_API_KEY não encontrada no arquivo .env!{Colors.ENDC}")
    exit(1)

# Conexão com MongoDB
if os.path.exists('/.dockerenv'):
    MONGO_URI = "mongodb://admin:admin123@mongodb:27017/"
else:
    MONGO_URI = "mongodb://admin:admin123@localhost:27017/"
DB_NAME = "threat_intel"
COLLECTION_NAME = "shodan_assets"

print(f"{Colors.OKCYAN}🔌 Iniciando conexão com o MongoDB...{Colors.ENDC}")
max_retries = 6
for attempt in range(max_retries):
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Testa a conexão
        client.server_info()
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        print(f"{Colors.OKGREEN}✅ Conectado ao MongoDB com sucesso no banco '{DB_NAME}'!{Colors.ENDC}")
        break  # Sai do loop se conectar com sucesso
    except Exception as e:
        print(f"{Colors.WARNING}⚠️ Tentativa {attempt + 1}/{max_retries} falhou. Banco não está pronto ainda. Aguardando 5s...{Colors.ENDC}")
        time.sleep(5)
else:
    print(f"{Colors.FAIL}❌ Falha fatal: Não foi possível conectar ao MongoDB após {max_retries} tentativas.{Colors.ENDC}")
    exit(1)

api = shodan.Shodan(SHODAN_API_KEY)

def sanitize_dict(obj):
    if isinstance(obj, dict):
        return {k: sanitize_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_dict(v) for v in obj]
    elif isinstance(obj, int):
        if obj > 9223372036854775807 or obj < -9223372036854775808:
            return str(obj)
        return obj
    else:
        return obj

def job_mineracao():
    print(f"\n{Colors.HEADER}🚀 Iniciando mineração contínua no Shodan...{Colors.ENDC}")
    print(f"{Colors.WARNING}⏰ Horário de início: {time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    
    # Lista de queries separadas baseadas nas tecnologias
    queries = [
        'port:23',
        'product:"MongoDB"',
        'os:"Windows Server"'
    ]
    
    total_saved = 0
    limit_per_query = 200
    
    for query in queries:
        print(f"\n{Colors.OKBLUE}🔍 Buscando por: {query}{Colors.ENDC}")
        try:
            results = api.search(query)
            matches = results.get('matches', [])
            total_matches = results.get('total', 0)
            
            print(f"{Colors.OKCYAN}📊 Shodan reportou {total_matches} dispositivos totais.{Colors.ENDC}")
            
            count = 0
            for result in matches:
                ip_str = result.get('ip_str')
                port = result.get('port')
                if not ip_str or not port:
                    continue
                
                # Documento completo a ser inserido
                doc = {
                    'ip': ip_str,
                    'port': port,
                    'query_source': query,
                    'data': sanitize_dict(result),
                    'timestamp': time.time()
                }
                
                # Upsert usando IP + Porta como chave única de identificação
                collection.update_one(
                    {'ip': ip_str, 'port': port},
                    {'$set': doc},
                    upsert=True
                )
                
                count += 1
                # Limite de registros por query, para maximizar coleta
                if count >= limit_per_query:
                    break
                    
            total_saved += count
            print(f"{Colors.OKGREEN}✅ {count} registros salvos/atualizados para '{query}'.{Colors.ENDC}")
            
        except shodan.APIError as e:
            print(f"{Colors.FAIL}❌ Erro na API do Shodan ao buscar '{query}': {e}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Erro inesperado ao processar '{query}': {e}{Colors.ENDC}")
            
    print(f"\n{Colors.HEADER}🏁 Mineração finalizada! Total processado nesta rodada: {total_saved}{Colors.ENDC}")
    print(f"{Colors.WARNING}⏳ Aguardando próximo ciclo (12 horas)...{Colors.ENDC}")

if __name__ == "__main__":
    print(f"{Colors.WARNING}🔰 Executando rotina imediata para validação inicial...{Colors.ENDC}")
    job_mineracao()
    
    # Agendamento para a cada 12 horas
    schedule.every(12).hours.do(job_mineracao)
    
    # Loop contínuo
    while True:
        schedule.run_pending()
        time.sleep(60)
