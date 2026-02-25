# 1. Usa uma imagem oficial do Python, versão leve (slim)
FROM python:3.9-slim

# 2. Previne problemas de dependência do XGBoost no Linux
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

# 3. Define a pasta de trabalho dentro do contêiner
WORKDIR /app

# 4. Copia apenas o requirements primeiro (Aproveita o cache do Docker e acelera o build)
COPY requirements.txt .

# 5. Instala as dependências da nossa API
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia o resto do código do projeto para dentro do contêiner
COPY . .

# 7. Expõe a porta 8000 para o mundo exterior
EXPOSE 8000

# 8. O comando que liga o Firewall quando o contêiner iniciar
CMD ["python", "app.py"]
