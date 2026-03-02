import os
import shodan
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

if not SHODAN_API_KEY:
    raise ValueError("Missing SHODAN_API_KEY from environment variables")

api = shodan.Shodan(SHODAN_API_KEY)

# Query parameters: targeting IoT (Telnet port 23) and exposed DBs (MongoDB)
QUERIES = ['port:23', 'product:"MongoDB"']
LIMIT_PER_QUERY = 1500  # Total around 3000

print(f"Starting data mining for queries: {QUERIES} (Target per query: {LIMIT_PER_QUERY} records)")

extracted_data = []

for query in QUERIES:
    count = 0
    print(f"\nRunning query: {query}")
    try:
        # Use search_cursor for Academic API access without pagination limits
        for banner in api.search_cursor(query):
            # Extract required features
            ip_str = banner.get('ip_str', 'Unknown')
            port = banner.get('port', 0)
            org = banner.get('org', 'Unknown')
            os_name = banner.get('os', 'Unknown')
            
            # Extract CVEs (keys of the 'vulns' dictionary)
            vulns_dict = banner.get('vulns', {})
            vulns = list(vulns_dict.keys()) if isinstance(vulns_dict, dict) else []
            
            # Extract location and tags
            location = banner.get('location', {})
            country_code = location.get('country_code', 'Unknown')
            tags = banner.get('tags', [])
            
            extracted_data.append({
                'ip_str': ip_str,
                'port': port,
                'org': org,
                'os': os_name,
                'vulns': vulns,
                'location.country_code': country_code,
                'tags': tags
            })
            
            count += 1
            if count % 500 == 0:
                print(f"Extracted {count}/{LIMIT_PER_QUERY} records from {query}...")
                
            if count >= LIMIT_PER_QUERY:
                print(f"Reached limit of {LIMIT_PER_QUERY} for {query}. Proceeding to next.")
                break
                
    except shodan.APIError as e:
        print(f"API Error on query '{query}': {e}")
    except Exception as e:
        print(f"Unexpected Error on query '{query}': {e}")

# Save to CSV
if extracted_data:
    df = pd.DataFrame(extracted_data)
    # Ensure the Datasets_Cybersecurity directory exists
    os.makedirs('Datasets_Cybersecurity', exist_ok=True)
    output_path = 'Datasets_Cybersecurity/shodan_raw_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Successfully saved {len(df)} records to {output_path}")
else:
    print("No data was extracted.")
