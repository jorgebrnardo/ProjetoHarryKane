from bs4 import BeautifulSoup
import pandas as pd

# Caminho do HTML salvo
html_path = r"./partidas.html"

# Lê o HTML
with open(html_path, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Seleciona todos os <a> com a classe "ergebnis-link"
links = soup.find_all('a', class_='ergebnis-link')

# Extrai os hrefs e monta os links completos
base_url = "https://www.transfermarkt.com.br"
full_links = [base_url + link['href'] for link in links if link.get('href')]

# Salva em CSV
df = pd.DataFrame(full_links, columns=["match_link"])
df.to_csv(r"./match_links.csv", index=False)

print("Links salvos com sucesso!")
