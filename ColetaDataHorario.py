from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# Caminho do CSV com os links
csv_path = r"./match_links.csv"
df = pd.read_csv(csv_path)

results = []

# Configuração do Selenium (modo invisível e rápido)
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1080")
options.add_argument('--no-sandbox')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0")
options.add_argument("--log-level=3")  # Reduz logs

driver = webdriver.Chrome(options=options)

# VARREDURA DOS LINKS
for link in df['match_link']:
    try:
        full_link = "https://www.transfermarkt.com.br" + link if link.startswith("/") else link
        driver.get(full_link)
        time.sleep(1.5)  # tempo mínimo necessário para o conteúdo carregar

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        game_data = soup.find('div', class_='sb-spieldaten')

        date_text, time_text, stadium = "", "", ""

        if game_data:
            date_p = game_data.find('p', class_='sb-datum hide-for-small')
            if date_p:
                for a in date_p.find_all('a'):
                    href = a.get('href', '')
                    if '/datum/' in href:
                        date_text = a.text.strip()
                        break
                parts = date_p.get_text(separator="|").split("|")
                if parts:
                    possible_time = parts[-1].strip()
                    if ":" in possible_time:
                        time_text = possible_time

            extra_info = game_data.find('p', class_='sb-zusatzinfos')
            if extra_info:
                stadium_link = extra_info.find('a')
                if stadium_link:
                    stadium = stadium_link.text.strip()

        results.append({
            "link": full_link,
            "date": date_text,
            "time": time_text,
            "stadium": stadium
        })

        print(f"✅ {full_link}")

    except Exception as e:
        print(f"❌ {link} - erro: {str(e)}")
        results.append({
            "link": link,
            "date": "",
            "time": "",
            "stadium": ""
        })

driver.quit()

# Salva o CSV
csv_output = r"./match_details.csv"
results_df = pd.DataFrame(results)
results_df.to_csv(csv_output, index=False)
print("📁 CSV salvo com sucesso.")

# VARREDURA FINAL DE VALORES VAZIOS
empty_rows = results_df[
    (results_df['date'] == "") |
    (results_df['time'] == "") |
    (results_df['stadium'] == "")
]

if empty_rows.empty:
    print("✅ Todos os registros foram extraídos com sucesso.")
else:
    print(f"⚠️ {len(empty_rows)} registros com campos vazios encontrados:")
    print(empty_rows[['link', 'date', 'time', 'stadium']])
