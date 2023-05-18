import os
from dao.init import save_jobs_to_mysql
from pc.get_html import get_html

csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'const', 'code.csv')
last_success_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'const', 'last_success.txt')

last_success_line = 0

# 读取最后一次成功的行号
if os.path.exists(last_success_file):
    with open(last_success_file, 'r') as f:
        last_success_line = int(f.read())

try:
    with open(csv_file, encoding='UTF-8') as f:
        line_number = 1
        for line in f:
            if line_number <= last_success_line:
                line_number += 1
                continue

            code, name = line.strip().split(',')
            if code.isdigit() and len(code) == 9:
                city = {
                    'id': code,
                    'name': name
                }
            else:
                area = {
                    'id': code,
                    'name': name
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
                        # 保存最后一次成功的行号到文件
                        with open(last_success_file, 'w') as f:
                            f.write(str(last_success_line))
                    except Exception as e:
                        print(f"Failed to import jobs for city '{city['name']}' and area '{area['name']}': {str(e)}")
                        break  # 终止循环，避免继续处理下一行数据

            line_number += 1

except FileNotFoundError as e:
    print(f"File not found: {str(e)}")
