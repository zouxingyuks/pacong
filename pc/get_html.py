from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
import random
import os
import yaml

from pc.parse import parse_job_cards

Debug_mod = True


def get_html(city, areaBusiness, browser_type=None):
    headless = not Debug_mod
    counter = 1
    last_success_page = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'const', 'last_success_page.txt')
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'config.yaml')

    # 读取最后一次成功的行号
    if os.path.exists(last_success_page):
        with open(last_success_page, 'r') as f:
            last_failed_page = int(f.read())
    else:
        last_failed_page = 0

    # 加载配置文件
    with open(config_file, encoding='utf-8') as f:
        config = yaml.safe_load(f)

    jobs = []
    with sync_playwright() as p:
        if not browser_type:
            browser_type = random.choice(['chromium', 'firefox', 'webkit'])
        if browser_type == 'chromium':
            browser = p.chromium.launch(headless=headless)
        elif browser_type == 'firefox':
            browser = p.firefox.launch(headless=headless)
        else:
            browser = p.webkit.launch(headless=headless)
        context = browser.new_context()
        # 从最后一次成功之后开始
        for page_number in range(last_failed_page + 1, 11):
            url = f'https://www.zhipin.com/web/geek/job?city={city}&areaBusiness={areaBusiness}&page={str(page_number)}'
            page = context.new_page()
            page.bring_to_front()

            # 超时重试机制
            retry_attempts = 0
            while retry_attempts < config['max_retry_attempts']:
                try:
                    page.goto(url, timeout=config['retry_timeout'])
                    page.wait_for_selector('.job-card-wrapper', timeout=config['retry_timeout'])
                    break
                except Exception:
                    retry_attempts += 1
                    if retry_attempts == config['max_retry_attempts']:
                        browser.close()
                        time.sleep(random.randint(600, 3600))
                        continue

            page_content = page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            jobs_cards = parse_job_cards(soup)
            jobs.extend(jobs_cards)
            # 测试用命令
            # print(jobs)
            counter += 1
            time.sleep(random.randint(60, 120))
            # 保存失败位置到文件
            with open(last_success_page, 'w') as f:
                f.write(str(page_number))

            page.close()
    if os.path.exists(last_success_page):
        os.remove(last_success_page)
    return jobs
