import subprocess
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
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def handle_flow(flow):
    if TARGET_URL in flow.request.url:
        # Parse job cards from response
        soup = BeautifulSoup(flow.response.content, 'html.parser')
        job_cards = parse_job_cards(soup)
        return job_cards
    return None


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

    # Start mitmdump subprocess
    mitmdump_cmd = [
        'mitmdump',
        '-s', __file__,
        '--set', f'target_url={TARGET_URL}',
        '--set', f'city={city}',
        '--set', f'areaBusiness={areaBusiness}',
    ]
    subprocess.Popen(mitmdump_cmd)

    with sync_playwright() as p:
        if not browser_type:
            # browser_type = random.choice(['firefox', 'chromium', 'webkit'])
            browser_type = random.choice(['firefox'])
        if browser_type == 'chromium':
            browser = p.chromium.launch(headless=headless)
        elif browser_type == 'firefox':
            browser = p.firefox.launch(headless=headless)
        else:
            browser = p.webkit.launch(headless=headless)

        # Create a new context
        context = browser.new_context()

        # 从最后一次成功之后开始
        for page_number in range(1, 11):
            url = f'https://www.zhipin.com/web/geek/job?city={city}&areaBusiness={areaBusiness}&page={str(page_number)}'
            page = context.new_page()
            page.bring_to_front()
            print("get " + url)
            # 超时重试机制
            retry_attempts = 0
            while retry_attempts < config['max_retry_attempts']:
                print("retry_attempts:" + str(retry_attempts))
                try:
                    proxy = get_proxy().get("proxy")
                    print(f"Using proxy: {proxy}")
                    page.set_extra_http_headers({"Proxy": "http://{}".format(proxy)})
                    page.goto(url, timeout=config['retry_timeout'])
                    page.wait_for_selector('.job-card-wrapper', timeout=config['retry_timeout'])
                    break
                except Exception:
                    retry_attempts += 1
                    time.sleep(random.randint(6, 60))
                    if retry_attempts == config['max_retry_attempts']:
                        browser.close()
                        retry_attempts = 0
                        delete_proxy(proxy)
                        time.sleep(random.randint(600, 3600))
                        continue
            page_content = page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            jobs_cards = parse_job_cards(soup)
            jobs.extend(jobs_cards)
            # 测试用命令
            print("succeed")
            counter += 1
            time.sleep(random.randint(6, 30))
            page.close()

            # 删除代理
            delete_proxy(proxy)

    if os.path.exists(last_success_page):
        os.remove(last_success_page)

    # Stop mitmdump subprocess
    subprocess.call(["pkill", "-f", "mitmdump"])

    return jobs
