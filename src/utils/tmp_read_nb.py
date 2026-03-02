import json, sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def read_nb(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        print(f'=== {path} ===')
        for i, cell in enumerate(nb['cells']):
            if cell['cell_type'] == 'code':
                source = "".join(cell.get('source', []))
                keys = ['train_test_split', 'Classifier', 'confusion_matrix', 'KDD', 'accuracy', 'GridSearch']
                if any(k in source for k in keys):
                    print(f'--- Cell {i} ---')
                    print(source)
    except Exception as e:
        print(f'Error reading {path}: {e}')

read_nb('e:\\Estudos_Cybersecurity\\Notebooks\\03_modelo.ipynb')
read_nb('e:\\Estudos_Cybersecurity\\Notebooks\\04_treinamento_modelo.ipynb')
