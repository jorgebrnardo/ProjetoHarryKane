from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd

#Carrega o CSV
df_entrada = pd.read_csv("match_links.csv") 
df_entrada = df_entrada.dropna(subset=["stadium"])

#Inicializa o geolocalizador
geolocator = Nominatim(user_agent="stadium_locator")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

#Função que processa linha por linha
def localizar_linha(row):
    estadio = row["stadium"]
    date = row["date"]
    time = row["time"]
    
    try:
        location = geocode(estadio)
        if location:
            address = location.raw.get("display_name", "")
            components = address.split(", ")
            cidade = components[-4] if len(components) >= 4 else None
            pais = components[-1] if len(components) >= 1 else None

            return {
                "Date": date,
                "Time": time,
                "Estádio": estadio,
                "Cidade": cidade,
                "País": pais,
                "Endereço completo": address
            }
    except:
        pass

    return {
        "Date": date,
        "Time": time,
        "Estádio": estadio,
        "Cidade": None,
        "País": None,
        "Endereço completo": None
    }

#Aplica a função a cada linha
resultados = [localizar_linha(row) for _, row in df_entrada.iterrows()]

#Converte em DataFrame e salva
df_resultados = pd.DataFrame(resultados)
print(df_resultados)
df_resultados.to_csv("localizacao_estadios.csv", index=False)
