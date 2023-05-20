from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests
import time
import random
import os
import yaml

from pc.parse import parse_job_cards

# 全局变量：目标URL
TARGET_URL = "https://www.zhipin.com/web/geek/job"


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get(f"http://127.0.0.1:5010/delete/?proxy={proxy}")


def handle_flow(flow):
    if TARGET_URL in flow.request.url:
        # Parse job cards from response
        soup = BeautifulSoup(flow.response.content, 'html.parser')
        job_cards = parse_job_cards(soup)
        return job_cards
    return None


def configure_proxy(proxy):
    firefox_user_prefs = {
        "security.cert_pinning.enforcement_level": 0,
        "security.tls.version.min": 1,
        "network.stricttransportsecurity.preloadlist": False,
        "network.proxy.type": 1,
        "network.proxy.http": proxy.split(':')[0],
        "network.proxy.http_port": int(proxy.split(':')[1]),
        "network.proxy.ssl": proxy.split(':')[0],
        "network.proxy.ssl_port": int(proxy.split(':')[1]),
    }
    return firefox_user_prefs


def get_html(city, areaBusiness, browser_type=None):
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'config.yaml')

    # Read the config file
    with open(config_file, encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Read the value of Debug_mod from the config file
    Debug_mod = config.get('Debug_mod', False)

    headless = not Debug_mod
    counter = 1
    last_success_page = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'const', 'last_success_page.txt')
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'config.yaml')

    # 加载配置文件
    with open(config_file, encoding='utf-8') as f:
        config = yaml.safe_load(f)

    jobs = []

    # 获取代理
    proxy = get_proxy().get("proxy")

    with sync_playwright() as p:

        browser = p.firefox.launch(firefox_user_prefs=configure_proxy(proxy),
                                   headless=headless,
                                   slow_mo=5000,
                                   timeout=25000)
        context = browser.new_context()

        for page_number in range(1, 11):
            url = f'https://www.zhipin.com/web/geek/job?city={city}&areaBusiness={areaBusiness}&page={str(page_number)}'
            page = context.new_page()
            page.bring_to_front()
            print("get " + url)
            retry_attempts = 0
            while retry_attempts < config['max_retry_attempts']:
                print("retry_attempts:" + str(retry_attempts))
                try:
                    page.goto(url, timeout=config['retry_timeout'])
                    page.wait_for_selector('.job-card-wrapper', timeout=config['retry_timeout'])
                    break
                except Exception:
                    retry_attempts += 1
                    # time.sleep(random.randint(6, 30))
                    if retry_attempts == config['max_retry_attempts']:
                        browser.close()
                        retry_attempts = 0
                        delete_proxy(proxy)
                        print("开始重启浏览器")
                        # 更新浏览器
                        proxy = get_proxy().get("proxy")
                        browser = p.firefox.launch(firefox_user_prefs=configure_proxy(proxy),
                                                   headless=headless,
                                                   slow_mo=5000,
                                                   timeout=25000)
                        context = browser.new_context()
                        page = context.new_page()
                        page.bring_to_front()
                        # time.sleep(random.randint(600, 3600))
                        continue
            page_content = page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            jobs_cards = parse_job_cards(soup)
            jobs.extend(jobs_cards)
            print("succeed")
            counter += 1
            time.sleep(random.randint(6, 30))
            page.close()

    if os.path.exists(last_success_page):
        os.remove(last_success_page)

    # delete_proxy(proxy)

    return jobs
