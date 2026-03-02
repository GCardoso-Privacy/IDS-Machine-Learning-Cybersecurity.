import os
import shutil

base_dir = '../.."
os.chdir(base_dir)

# 1. Create directories
dirs_to_create = [
    "data/processed",
    "models",
    "notebooks",
    "src/miner",
    "reports/figures",
    "docker"
]

for d in dirs_to_create:
    os.makedirs(d, exist_ok=True)

# 2. Move files
# data/processed/: Mover todos os arquivos .parquet e .csv (antiga Datasets_Cybersecurity)
for src_folder in ["Datasets_Cybersecurity", "."]:
    if os.path.exists(src_folder):
        for file in os.listdir(src_folder):
            if file.endswith(".parquet") or file.endswith(".csv"):
                src_path = os.path.join(src_folder, file)
                if os.path.isfile(src_path):
                    shutil.move(src_path, os.path.join("data/processed", file))

# models/: Mover arquivos .json e .joblib (antiga Modelos)
if os.path.exists("Modelos"):
    for file in os.listdir("Modelos"):
        if file.endswith(".json") or file.endswith(".joblib"):
            src_path = os.path.join("Modelos", file)
            if os.path.isfile(src_path):
                shutil.move(src_path, os.path.join("models", file))

# notebooks/: Mover todos os arquivos .ipynb da raiz e Notebooks para cÃ¡
for src_folder in ["Notebooks", "."]:
    if os.path.exists(src_folder):
        for file in os.listdir(src_folder):
            if file.endswith(".ipynb"):
                src_path = os.path.join(src_folder, file)
                if os.path.isfile(src_path):
                    try:
                        shutil.move(src_path, os.path.join("notebooks", file))
                    except Exception as e:
                        pass # avoid cross-device or same-file errors

# src/miner/: Mover os scripts .py de coleta (antiga scripts).
if os.path.exists("scripts"):
    for file in os.listdir("scripts"):
        if file.endswith(".py"):
            src_path = os.path.join("scripts", file)
            if os.path.isfile(src_path):
                shutil.move(src_path, os.path.join("src", "miner", file))

# reports/figures/: Mover todas as imagens de matrizes de confusÃ£o (.png).
for root, dirs, files in os.walk("."):
    if "Git" in root or ".git" in root or "reports" in root or ".venv" in root:
        continue
    for file in files:
        if file.endswith(".png"):
            src_path = os.path.join(root, file)
            dest_path = os.path.join("reports", "figures", file)
            if not os.path.exists(dest_path):
                shutil.move(src_path, dest_path)

# docker/: Mover Dockerfile e docker-compose.yml
for f in ["Dockerfile", "docker-compose.yml", "Dockerfile.miner", ".dockerignore"]:
    if os.path.exists(f):
        shutil.move(f, os.path.join("docker", f))

# 3. Refactor Paths
replacements_raw = {
    # standard python usages
    r"../data/processed/": "../data/processed/",
    r"../data/processed/": "../data/processed/",
    r"..\Datasets_Cybersecurity": "../data/processed",
    r"../data/processed/": "../data/processed/",
    r"../data/processed/": "../data/processed/",
    r"..\\Datasets_Cybersecurity": "../data/processed",
    
    # JSON escapes inside IPYNB
    r"..\\\\Datasets_Cybersecurity\\\\": "../data/processed/",
    r"..\\\\Datasets_Cybersecurity": "../data/processed",
    
    r"data/processed/": "data/processed/",
    r"Datasets_Cybersecurity\\": "data/processed/",
    r"Datasets_Cybersecurity": "data/processed",

    r"../models/": "../models/",
    r"../models/": "../models/",
    r"..\Modelos": "../models",
    r"../models/": "../models/",
    r"../models/": "../models/",
    r"..\\Modelos": "../models",
    
    # JSON escapes inside IPYNB
    r"..\\\\Modelos\\\\": "../models/",
    r"..\\\\Modelos": "../models",
    
    r"models/": "models/",
    r"Modelos\\": "models/",
    r"Modelos": "models",

    r"src/miner/": "src/miner/",
    r"scripts\\": "src/miner/",
    # r"scripts" without slash might be too generic and replace normal words, so use it carefully
    # The prompt explicitly asked for specific ones:
}

files_to_check = []
for root, dirs, files in os.walk("."):
    if "Git" in root or ".git" in root or "venv" in root or ".gemini" in root:
        continue
    for file in files:
        if file.endswith(".py") or file.endswith(".ipynb"):
            files_to_check.append(os.path.join(root, file))

for fp in files_to_check:
    try:
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_content = content
        # Exact requested by user:
        new_content = new_content.replace(r"../data/processed/", "../data/processed/")
        new_content = new_content.replace(r"../data/processed/", "../data/processed/")
        # For ipynb json escapes:
        new_content = new_content.replace(r"../data/processed/", "../data/processed/")
        new_content = new_content.replace(r"../data/processed/", "../data/processed/")
        new_content = new_content.replace(r"data/processed/", "data/processed/")
        
        new_content = new_content.replace(r"../models/", "../models/")
        new_content = new_content.replace(r"../models/", "../models/")
        new_content = new_content.replace(r"../models/", "../models/")
        new_content = new_content.replace(r"../models/", "../models/")
        new_content = new_content.replace(r"models/", "models/")
        
        new_content = new_content.replace(r"src/miner/", "src/miner/")
        # json escape inside ipynb
        new_content = new_content.replace(r"src/miner/", "src/miner/")

        if new_content != content:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_content)
    except Exception as e:
        print(f"Error on {fp}: {e}")

# 4. Cleanup Empty Directories
for p in ["scripts", "Datasets_Cybersecurity", "Modelos", "Notebooks"]:
    if os.path.exists(p) and os.path.isdir(p):
        try:
            os.rmdir(p)
        except OSError:
            print(f"Directory {p} not empty, skipping rmdir")

# Remova pastas vazias e caches (__pycache__, .ipynb_checkpoints).
for root, dirs, files in os.walk(".", topdown=False):
    for name in dirs:
        if name in ["__pycache__", ".ipynb_checkpoints"]:
            try:
                shutil.rmtree(os.path.join(root, name), ignore_errors=True)
            except Exception:
                pass

print("Refactoring complete.")
