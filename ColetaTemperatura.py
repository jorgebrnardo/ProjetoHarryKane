import pandas as pd
import requests
import urllib.parse
from datetime import datetime
import re

# Configurações da API
API_KEY = 'SuaChaveAqui'
BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'

# Carregar o CSV original
df = pd.read_csv('./AnaliseFinal.csv')

# Garante que a coluna 'Temperatura' existe
if 'Temperatura' not in df.columns:
    df['Temperatura'] = None

# Função auxiliar para converter 'HH:MM:SS' em minutos
def minutes_from_str(hhmmss):
    dt = datetime.strptime(hhmmss, '%H:%M:%S')
    return dt.hour * 60 + dt.minute

# Cache para evitar chamadas repetidas à API
api_cache = {}

# Contador de erros consecutivos
consecutive_errors = 0
MAX_ERRORS = 20

# Função principal para buscar temperatura
def get_temperature(row):
    global consecutive_errors

    # Pula se já existe valor
    if pd.notnull(row['Temperatura']):
        print(f"⏭️ Pulando {row['Endereço completo']} - Temperatura já presente.")
        return row['Temperatura']

    address = row['Endereço completo']
    raw_datetime = re.sub(r'\s+\(?[A-Z+\-0-9]{2,5}\)?$', '', row['Horario_Local']).strip()
    datetime_obj = pd.to_datetime(raw_datetime)
    date = datetime_obj.strftime('%Y-%m-%d')
    target_minutes = datetime_obj.hour * 60 + datetime_obj.minute

    # Cache key
    cache_key = (address, date)

    if cache_key in api_cache:
        hours_data = api_cache[cache_key]
    else:
        # Montar URL
        url_address = urllib.parse.quote(address)
        url = (
            f"{BASE_URL}{url_address}/{date}"
            f"?key={API_KEY}&unitGroup=metric&include=hours&timezone=GMT"
        )

        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
            hours_data = data['days'][0]['hours']
            api_cache[cache_key] = hours_data
            consecutive_errors = 0  # Resetar após sucesso
        except Exception as e:
            print(f"❌ Erro ao buscar temperatura para {address} em {date}: {e}")
            consecutive_errors += 1

            if consecutive_errors >= MAX_ERRORS:
                print(f"\n🚨 Atingido o limite de {MAX_ERRORS} erros consecutivos. Salvando e encerrando...")
                df.to_csv('./AnaliseFinal.csv', index=False)
                exit(1)

            return None

    # Filtrar horário mais próximo (±2h)
    filtered = [
        h for h in hours_data
        if abs(minutes_from_str(h['datetime']) - target_minutes) <= 120
    ]

    if filtered:
        closest = min(filtered, key=lambda h: abs(minutes_from_str(h['datetime']) - target_minutes))
        print(f"✅ {address} {date} {datetime_obj.strftime('%H:%M')} → {closest['temp']}°C")
        return closest['temp']
    else:
        print(f"⚠️ Sem dados próximos para {address} em {datetime_obj.strftime('%H:%M')}")
        return None

# Aplicar função
df['Temperatura'] = df.apply(get_temperature, axis=1)

# Salvar ao final (caso não tenha havido erro suficiente para sair antes)
df.to_csv('./AnaliseFinal.csv', index=False)
print("\n✅ Arquivo 'AnaliseFinal.csv' atualizado com novas temperaturas.")
