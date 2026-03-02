import json

def extract_notebook(path, out_path):
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    with open(out_path, 'w', encoding='utf-8') as f_out:
        f_out.write(f'=== {path} ===\n')
        for i, cell in enumerate(nb['cells']):
            if cell['cell_type'] == 'code':
                source = "".join(cell.get('source', []))
                f_out.write(f'--- Cell {i} ---\n')
                f_out.write(source + '\n')

extract_notebook('../../notebooks/03_modelo.ipynb', '../../out_03.txt')
extract_notebook('../../notebooks/04_treinamento_modelo.ipynb', '../../out_04.txt')
