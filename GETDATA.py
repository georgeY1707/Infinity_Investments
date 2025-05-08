import requests
from bs4 import BeautifulSoup


def get_data(name):
    url = f"https://alfabank.ru/make-money/investments/catalog/akcii/t/{name}/"
    headers = {
        "User-Agent": "Mozilla/4.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Получаем все цены
        prices = soup.find_all('span', class_="aAXzba")
        invest_up = str(prices[0]).replace('<span class="aAXzba bAXzba" data-test-id="profitability-renderer">', '').replace('</span>', '')
        price = str(prices[1]).replace('<span class="aAXzba">', '').replace('</span>', '')

        # 2. Получаем логотип (более надежный способ)
        logo = ''
        logo_div = soup.find("div", class_="icon-view__component_wydeg")
        logo_div = str(logo_div).split('><')
        for elem in logo_div:
            if elem.startswith('image'):
                logo = (f'<{elem}>'.replace('<image height="100%" href="', '')
                        .replace('" preserveaspectratio="xMidYMid slice" width="100%"/>', ''))

        return price, invest_up, logo
    else:
        print(f"Ошибка запроса: {response.status_code}")

print(get_data('GAZP'))