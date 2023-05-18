import os
import random
import time

from dao.init import save_jobs_to_mysql
from pc.get_html import get_html

csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'const', 'code.csv')
last_success_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'const', 'last_success.txt')
last_success_city_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'const', 'last_success_city.txt')

last_success_line = 0
last_success_city = ''

# 读取最后一次成功的行号和城市
if os.path.exists(last_success_file) and os.path.exists(last_success_city_file):
    with open(last_success_file, 'r') as f:
        last_success_line = int(f.read())
    with open(last_success_city_file, 'r') as f:
        last_success_city = f.read()

try:
    with open(csv_file, encoding='UTF-8') as f:
        lines = f.readlines()

        for line_number, line in enumerate(lines, 1):
            if line_number <= last_success_line:
                continue
            code, _ = line.strip().split(',')
            if code.isdigit() and len(code) == 9:
                city = {
                    'id': code
                }
            else:
                area = {
                    'id': code
                }
                if 'city' not in locals():
                    city = {
                        'id': last_success_city
                    }
                if city and area:
                    # 做一些更新 city 和 area 的操作
                    try:
                        jobs = get_html(city["id"], area["id"])
                        # 测试用代码
                        # print(city["id"], area["id"])
                        # print(jobs)
                        save_jobs_to_mysql(jobs)
                        last_success_line = line_number
                        last_success_city = city
                        # 保存最后一次成功的行号和城市到文件
                        with open(last_success_file, 'w') as file:
                            file.write(str(last_success_line))
                        with open(last_success_city_file, 'w') as file:
                            file.write(last_success_city)
                        print(f"Successfully imported jobs for city '{last_success_city}' and area '{area['id']}'")
                    except Exception as e:
                        print(f"Failed to import jobs for city '{last_success_city}' and area '{area['id']}': {str(e)}")
                        break  # 终止循环，避免继续处理下一行数据
                    time.sleep(random.randint(120, 600))


except FileNotFoundError as e:
    print(f"File not found: {str(e)}")
