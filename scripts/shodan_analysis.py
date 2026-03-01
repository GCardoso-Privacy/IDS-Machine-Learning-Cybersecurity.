import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import ast

def load_data(filepath):
    print(f"Loading data from {filepath}...")
    try:
        df = pd.read_csv(filepath)
        print(f"Loaded {len(df)} records.")
        return df
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None

def clean_and_engineer_features(df):
    print("Cleaning data and engineering features...")
    # Fill missing values
    df['os'] = df['os'].fillna('Unknown')
    df['org'] = df['org'].fillna('Unknown')
    df['location.country_code'] = df['location.country_code'].fillna('Unknown')
    
    # Process vulnerabilities
    def count_vulns(vulns_str):
        if pd.isna(vulns_str):
            return 0
        try:
            # Safely evaluate string representation of list
            vulns_list = ast.literal_eval(vulns_str)
            return len(vulns_list)
        except:
            return 0

    df['num_vulns'] = df['vulns'].apply(count_vulns)
    df['has_cve'] = (df['num_vulns'] > 0).astype(int)
    
    # Process tags to determine if it's a cloud service
    def is_cloud(tags_str):
        if pd.isna(tags_str):
            return 0
        try:
            tags_list = ast.literal_eval(tags_str)
            return 1 if 'cloud' in [str(t).lower() for t in tags_list] else 0
        except:
            return 0
            
    df['is_cloud'] = df['tags'].apply(is_cloud)
    
    # Encode categorical features: port, org, os, country_code
    le = LabelEncoder()
    # We copy the dataframe for numeric features used by K-Means
    features_df = pd.DataFrame()
    features_df['port_encoded'] = le.fit_transform(df['port'].astype(str))
    features_df['org_encoded'] = le.fit_transform(df['org'])
    features_df['os_encoded'] = le.fit_transform(df['os'])
    features_df['country_encoded'] = le.fit_transform(df['location.country_code'])
    features_df['num_vulns'] = df['num_vulns']
    features_df['has_cve'] = df['has_cve']
    features_df['is_cloud'] = df['is_cloud']
    
    return df, features_df

def apply_kmeans(features_df, k=2):
    print(f"Applying K-Means clustering with k={k}...")
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(features_df)
    
    # Analyze the clusters to assign Cluster 0 (Botnet risk) vs Cluster 1 (Secure Server)
    # We expect the vulnerable cluster to have higher 'num_vulns' on average
    cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=features_df.columns)
    vuln_cluster_idx = cluster_centers['num_vulns'].idxmax()
    
    # Re-map so 0 is vulnerable and 1 is secure
    if vuln_cluster_idx == 1:
        clusters = 1 - clusters 
        
    return clusters

def visualize_clusters(df, clusters, output_path):
    print("Generating visualizations...")
    df['Cluster'] = clusters
    df['Cluster_Label'] = df['Cluster'].map({0: 'Vulnerable / Botnet Risk', 1: 'Secure Server'})
    
    plt.figure(figsize=(10, 6))
    
    # We will plot num_vulns vs 'port', using jitter for better visibility on port
    # Since ports are categorical-like numbers, we'll plot port vs num_vulns
    # Jittering port
    jittered_port = df['port'] + np.random.normal(0, 0.5, size=len(df))
    jittered_vulns = df['num_vulns'] + np.random.normal(0, 0.5, size=len(df))
    
    sns.scatterplot(
        x=jittered_port, 
        y=jittered_vulns, 
        hue=df['Cluster_Label'], 
        palette={
            'Vulnerable / Botnet Risk': '#e74c3c', # Red
            'Secure Server': '#2ecc71'             # Green
        },
        alpha=0.6
    )
    
    plt.title('Shodan IoT Devices: Risk Clustering (K-Means)')
    plt.xlabel('Port')
    plt.ylabel('Number of Vulnerabilities (CVEs)')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Make sure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved cluster visualization to {output_path}")

def main():
    input_file = "Datasets_Cybersecurity/shodan_raw_data.csv"
    output_image = "Modelos/shodan_clusters.png"
    
    df = load_data(input_file)
    if df is None or len(df) == 0:
        print("No data to process. Exiting.")
        return
        
    df, features_df = clean_and_engineer_features(df)
    
    clusters = apply_kmeans(features_df)
    
    visualize_clusters(df, clusters, output_image)
    
    print("Analysis complete.")

if __name__ == "__main__":
    main()
