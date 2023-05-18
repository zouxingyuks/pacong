import os
import signal
from dao.init import save_jobs_to_mysql
from pc.get_html import get_html

city = None
area = None

csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'const', 'code.csv')
failed_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'const', 'failed.txt')

# 读取失败位置
if os.path.exists(failed_file):
    with open(failed_file, 'r') as f:
        last_failed_line = int(f.read())
else:
    last_failed_line = 0


# 设置信号处理函数
def handle_signal(signum, frame):
    with open(failed_file, 'w') as f:
        f.write(str(last_failed_line))
    exit(0)


# 注册终止信号处理函数
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

try:
    with open(csv_file, encoding='UTF-8') as f:
        # 跳过失败位置之前的行
        for _ in range(last_failed_line):
            next(f)

        line_number = last_failed_line + 1
        for line in f:
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
                    print(city["id"], area["id"])
                    print(jobs)
                    save_jobs_to_mysql(jobs)
                except Exception as e:
                    print(f"Failed to import jobs for city '{city['name']}' and area '{area['name']}': {str(e)}")
                    # 保存失败位置到文件
                    with open(failed_file, 'w') as f:
                        f.write(str(line_number))
                    break  # 终止循环，避免继续处理下一行数据
            line_number += 1
            # time.sleep(random.randint(120, 600))

    # 处理完成后，删除保存失败位置的文件
    if os.path.exists(failed_file):
        os.remove(failed_file)
except FileNotFoundError as e:
    print(f"File not found: {str(e)}")
