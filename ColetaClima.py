import pandas as pd
from meteostat import Stations, Daily
from geopy.geocoders import Nominatim
from datetime import datetime
import warnings

# Ignorar warnings do meteostat
warnings.filterwarnings("ignore")

# Inicializa geolocator
geolocator = Nominatim(user_agent="busca_clima")

# Ler arquivo CSV original
arquivo_csv = "AnaliseFinal.csv"
df = pd.read_csv(arquivo_csv)

# Adicionar colunas para armazenar resultado
df['lat'] = None
df['lon'] = None
df['temp_avg_C'] = None

# Processar linha por linha
for idx, row in df.iterrows():
    try:
        # Geocodificação
        location = geolocator.geocode(f"{row['Cidade']}, {row['País']}")
        if location is None:
            print(f"Local não encontrado: {row['Cidade']}, {row['País']}")
            continue
        lat, lon = location.latitude, location.longitude
        df.at[idx, 'lat'] = lat
        df.at[idx, 'lon'] = lon
    except Exception as e:
        print(f"Erro na geocodificação: {e}")
        continue

    # Extrair a data do campo Horario_Local
    try:
        data_str = row['Horario_Local'].split(' ')[0]  # "2011-01-22"
        data_dt = datetime.strptime(data_str, '%Y-%m-%d')
    except Exception as e:
        print(f"Erro ao converter data: {e}")
        continue

    # Buscar estações próximas
    try:
        stations = Stations().nearby(lat, lon).fetch(5)
        temp_found = None
        for station_id in stations.index:
            data = Daily(station_id, data_dt, data_dt).fetch()
            if not data.empty and not pd.isna(data['tavg'].values[0]):
                temp_found = data['tavg'].values[0]
                print(f"{row['Cidade']} {data_str}: {temp_found} °C (Estação {station_id})")
                break
        df.at[idx, 'temp_avg_C'] = temp_found
        if temp_found is None:
            print(f"Sem dados climáticos para {row['Cidade']} em {data_str}")
    except Exception as e:
        print(f"Erro ao buscar dados climáticos: {e}")

# Salvar resultado
df.to_csv("Analise_Final_Clima.csv", index=False)
print("\n Arquivo salvo como 'Analise_Final_Clima.csv'")
