import pandas as pd
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

# Carregar o CSV
df = pd.read_csv('localizacao_estadios.csv') 

# Inicializadores
geolocator = Nominatim(user_agent="timezone_converter")
tf = TimezoneFinder()
br_tz = pytz.timezone('America/Sao_Paulo')

# Função para converter horário
def converter_para_fuso_local(row):
    try:
        # Geocodificação
        location = geolocator.geocode(row['Endereço completo'])
        if not location:
            print(f"Endereço não encontrado: {row['Endereço completo']}")
            return None

        # Encontrar o fuso horário
        timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        if not timezone_str:
            print(f"Fuso horário não encontrado: {row['Endereço completo']}")
            return None

        local_tz = pytz.timezone(timezone_str)

        # Parse da data e hora no fuso do Brasil
        data_str = row['Date'].split(',')[1].strip()  # Ex: "22/01/11"
        hora_str = row['Time']  # Ex: "13:00"
        dt_br = datetime.strptime(data_str + ' ' + hora_str, "%d/%m/%y %H:%M")
        dt_br = br_tz.localize(dt_br)

        # Converter para o fuso local
        dt_local = dt_br.astimezone(local_tz)
        return dt_local.strftime("%Y-%m-%d %H:%M (%Z)")
    
    except Exception as e:
        print(f"Erro em {row['Endereço completo']}: {e}")
        return None

# Aplicar conversão
df['Horario_Local'] = df.apply(converter_para_fuso_local, axis=1)

# Salvar resultado
df.to_csv('saida_convertida.csv', index=False)

print("Conversão concluída e salva em 'saida_convertida.csv'")
