import pandas as pd
import math
from collections import Counter

# Caminho para seu CSV
csv_path = './AnaliseFinal.csv'

# Lê o arquivo
df = pd.read_csv(csv_path)

# Remove linhas sem temperatura
df = df.dropna(subset=['Temperatura'])

# Converte para número inteiro (ignorando os decimais)
df['TempInt'] = df['Temperatura'].apply(lambda x: int(float(x)))

# Conta quantas ocorrências por temperatura inteira
contagem = Counter(df['TempInt'])

# Mostra ordenado por temperatura
for temp in sorted(contagem):
    print(f"{temp}°C: {contagem[temp]} jogo(s)")
