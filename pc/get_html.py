from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def docipProxy():
    url = 'https://proxy.seofangfa.com/'
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector('table')
        html = page.content()

        soup = BeautifulSoup(html, 'html.parser')
        proxy_table = soup.find('table', class_='table')
        for tr in proxy_table.find_all('tr'):
            td = tr.find('td')
            if td is not None:
                ip = td.text
                port = tr.find_all('td')[1].text
                yield f'{ip}:{port}'

        browser.close()


for proxy in docipProxy():
    print(proxy)
