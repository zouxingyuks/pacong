# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import json
import requests
from time import sleep
from bs4 import BeautifulSoup
from util.webRequest import WebRequest
from playwright.sync_api import sync_playwright


class ProxyFetcher(object):
    """
    proxy getter
    """
    @staticmethod
    def docipProxy():
        url = 'https://www.docip.net/'
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            # 等待页面加载
            page.wait_for_timeout(5000)

            # 等待 free_list 表格出现
            page.wait_for_selector('tbody[field="free_list"]')

            # 获取页面HTML
            html = page.content()

            # 获取总页数,例如 Page.showFree(5) 就是 5 页
            page_count = 4

            for i in range(page_count):
                # 调用 JS 函数翻页,如 Page.showFree(2)
                page.evaluate('Page.showFree(%d)' % (i + 1))

                # 重新获取页面 HTML
                html = page.content()

                # 解析页面,提取代理
                soup = BeautifulSoup(html, 'html.parser')
                proxy_table = soup.find('tbody', attrs={'field': 'free_list'})
                for tr in proxy_table.find_all('tr'):
                    ip = tr.find('td').text
                    port = tr.find_all('td')[1].text
                    yield f'{ip}:{port}'
            # 关闭浏览器
            browser.close()
    @staticmethod
    def seofangfaProxy():
        url = 'https://proxy.seofangfa.com/'
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
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
    @staticmethod
    def ip3366Proxy():
        base_url = 'http://www.ip3366.net/?stype=1&page='
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()

            for current_page in range(1, 8):
                url = base_url + str(current_page)
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
if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.freeProxy06():
        print(_)

# http://nntime.com/proxy-list-01.htm
