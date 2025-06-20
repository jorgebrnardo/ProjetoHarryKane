import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, Normalize
from collections import Counter

# Lê o CSV
csv_path = './AnaliseFinal.csv'
df = pd.read_csv(csv_path)

# Limpeza de dados
df = df.dropna(subset=['Temperatura'])
df['Temperatura'] = pd.to_numeric(df['Temperatura'], errors='coerce')
df = df.dropna(subset=['Temperatura'])

# Agrupamento por temperatura inteira
df['TempInt'] = df['Temperatura'].astype(int)
contagem = df['TempInt'].value_counts().sort_index()

# Intervalo e colormap customizado
temperaturas = contagem.index.to_numpy()
norm = Normalize(vmin=temperaturas.min(), vmax=temperaturas.max())

# Define o degradê: azul claro → amarelo → laranja
custom_cmap = LinearSegmentedColormap.from_list(
    "blue_yellow_orange",
    ["#5DADE2", "#FFE26C", "#E63922"]
)

# Cores aplicadas
colors = custom_cmap(norm(temperaturas))

# Cria figura
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(temperaturas, contagem.values, color=colors, edgecolor='black')

# Títulos
ax.set_title('Quantidade de jogos com gol por temperatura (°C)', fontsize=14)
ax.set_xlabel('Temperatura (°C)', fontsize=12)
ax.set_ylabel('Número de jogos com gol', fontsize=12)
ax.set_xticks(temperaturas)

# Valores no topo
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
            f'{int(height)}', ha='center', va='bottom', fontsize=9)

# Barra de cores
sm = plt.cm.ScalarMappable(cmap=custom_cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
cbar.set_label('Temperatura (°C)', fontsize=11)

# Estética
ax.grid(axis='y', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()


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