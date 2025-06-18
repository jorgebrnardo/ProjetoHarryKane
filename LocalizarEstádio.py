from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd

# Lista de nomes dos estádios
estadios = [
    "Maracanã",
    "Estádio do Morumbi",
    "Camp Nou",
    "Old Trafford",
    "Wembley Stadium",
    "Allianz Arena",
    "San Siro",
    "Estádio da Luz",
    "Estadio Monumental",
    "Estadio Azteca"
]

# Inicializa o geocodificador com identificador
geolocator = Nominatim(user_agent="stadium_locator")
# Adiciona delay automático
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Função para buscar localização


def localizar(estadio):
    try:
        location = geocode(estadio)
        if location:
            # Extrair cidade e país
            address = location.raw.get("display_name", "")
            components = address.split(", ")
            cidade = components[-4] if len(components) >= 4 else None
            pais = components[-1] if len(components) >= 1 else None

            return {
                "Estádio": estadio,
                "Latitude": location.latitude,
                "Longitude": location.longitude,
                "Cidade": cidade,
                "País": pais,
                "Endereço completo": address
            }
    except:
        pass

    return {
        "Estádio": estadio,
        "Latitude": None,
        "Longitude": None,
        "Cidade": None,
        "País": None,
        "Endereço completo": None
    }


# Processa cada estádio
resultados = [localizar(nome) for nome in estadios]

# Converte em DataFrame e exibe
df = pd.DataFrame(resultados)
print(df)

# Salva em CSV (opcional)
df.to_csv("localizacao_estadios.csv", index=False)
