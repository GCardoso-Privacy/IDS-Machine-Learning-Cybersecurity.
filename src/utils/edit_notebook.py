import json
import os

notebook_path = '../../notebooks/04_treinamento_modelo.ipynb"
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        # modify source array
        source = cell.get('source', [])
        for i, line in enumerate(source):
            if line.startswith('AMOSTRA_TREINO ='):
                source[i] = 'AMOSTRA_TREINO = 0.2 \n'
            elif line.startswith('    scoring='):
                source[i] = "    scoring='recall_macro', # Foco em Falsos Negativos\n"
        cell['source'] = source

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook updated successfully.")
