import json

fpath = "E:\\Estudos_Cyber_Oficial\\notebooks\\04_treinamento_modelo.ipynb"

with open(fpath, 'r', encoding='utf-8') as f:
    data = json.load(f)

changed = False
for cell in data['cells']:
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        trigger = 'print(f"✅ Dados Carregados: {df.shape[0]} linhas x {df.shape[1]} colunas")'
        if trigger in src and 'invalid_classes' not in src:
            new_src = src.replace(trigger, trigger + '\n\nclass_counts = df["Label"].value_counts()\ninvalid_classes = class_counts[class_counts < 2].index\nif len(invalid_classes) > 0:\n    print(f"⚠️ Removendo classes raras para evitar crash no stratify: {list(invalid_classes)}")\n    df = df[~df["Label"].isin(invalid_classes)]')
            cell['source'] = [line + '\n' for line in new_src.split('\n')]
            cell['source'][-1] = cell['source'][-1].rstrip('\n')
            changed = True

if changed:
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1)
    print("Notebook fixed.")
else:
    print("Notebook already fixed or trigger not found.")
