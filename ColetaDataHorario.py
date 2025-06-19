import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

# Caminhos
csv_path = r"./match_links.csv"
output_path = r"./match_links.csv"

# Carrega todos os links
df_links = pd.read_csv(csv_path)

# Cria coluna de link completo
df_links["full_link"] = df_links["match_link"].apply(
    lambda x: "https://www.transfermarkt.com.br" + x if x.startswith("/") else x
)

# Filtra apenas linhas com valores faltantes
to_scrape = df_links[
    (df_links['date'].isna()) |
    (df_links['time'].isna()) |
    (df_links['stadium'].isna()) |
    (df_links['date'] == "") |
    (df_links['time'] == "") |
    (df_links['stadium'] == "")
].copy().head(5)

if to_scrape.empty:
    print("✅ Nada a fazer. Nenhuma linha pendente.")
    exit()

# Configuração do Chrome
options = uc.ChromeOptions()
options.headless = True
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0")

driver = uc.Chrome(options=options)

def simulate_user_behavior(driver):
    try:
        actions = ActionChains(driver)
        actions.move_by_offset(100, 100).perform()
        time.sleep(0.5)
        actions.move_by_offset(50, 0).perform()
        time.sleep(0.5)
        actions.send_keys(Keys.F1).perform()
        time.sleep(0.5)
    except Exception as e:
        print(f"⚠️ Erro simulando comportamento do usuário: {e}")

def get_page_with_retry(driver, url, retries=5):
    for attempt in range(retries):
        try:
            driver.get(url)
            time.sleep(random.uniform(2, 6))
            simulate_user_behavior(driver)
            return driver.page_source
        except Exception as e:
            print(f"⚠️ Retry {attempt+1}: {url} - {e}")
            time.sleep(10 * (attempt + 1))
    return None

# Coleta os dados
for i, row in to_scrape.iterrows():
    link = row["full_link"]
    try:
        html = get_page_with_retry(driver, link)
        if html is None:
            raise Exception("❌ Falha ao carregar a página.")

        soup = BeautifulSoup(html, 'html.parser')
        game_data = soup.find('div', class_='sb-spieldaten')

        date_text, time_text, stadium = "", "", ""

        if game_data:
            date_p = game_data.find('p', class_='sb-datum hide-for-small')
            if date_p:
                for a in date_p.find_all('a'):
                    if '/datum/' in a.get('href', ''):
                        date_text = a.text.strip()
                        break
                parts = date_p.get_text(separator="|").split("|")
                for part in parts:
                    if ":" in part:
                        time_text = part.strip()
                        break

            extra_info = game_data.find('p', class_='sb-zusatzinfos')
            if extra_info:
                stadium_link = extra_info.find('a')
                if stadium_link:
                    stadium = stadium_link.text.strip()

        df_links.loc[df_links["full_link"] == link, ["date", "time", "stadium"]] = [date_text, time_text, stadium]

        print(f"✅ Atualizado: {link}")

    except Exception as e:
        print(f"❌ Erro ao processar {link} - {e}")

    time.sleep(random.uniform(2, 5))

# Remove coluna auxiliar e salva
df_links.drop(columns=["full_link"], inplace=True)
df_links.to_csv(output_path, index=False)
print("📥 CSV atualizado com novos dados.")
