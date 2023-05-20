import mysql.connector
import os
import yaml

config = {}

config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'config.yaml')
try:
    with open(config_file, encoding='utf-8') as f:
        config = yaml.safe_load(f)
except IOError:
    print('文件不存在，新建 config/config.yaml 文件... 请配置好数据库后再执行setup')
    config = {
        'mysql': {
            'host': '',
            'port': '',
            'user': '',
            'password': '.',
            'database': ''
        },
        'retry_timeout': '',
        'max_retry_attempts': '',
        'Debug_mod': True,
        'proxy_server': {
            'server': '',
            'username': '',
            'password': ''
        }
    }
    with open(config_file, 'w') as f:
        yaml.dump(config, f)
    exit()
config_mysql = config['mysql']
conn = mysql.connector.connect(
    host=config_mysql['host'],
    port=config_mysql['port'],
    user=config_mysql['user'],
    password=config_mysql['password'],
    database=config_mysql['database']
)
cursor = conn.cursor()

# 创建jobs表
cursor.execute('''
    CREATE TABLE jobs (
        id SERIAL PRIMARY KEY, 
        job_link TEXT,
        job_name VARCHAR(255),
        location VARCHAR(255), 
        salary VARCHAR(255),
        job_tags VARCHAR(255),
        company VARCHAR(255)
    )
''')

# 修改列定义并添加注释
cursor.execute('''
    ALTER TABLE jobs
    MODIFY COLUMN job_link TEXT COMMENT '岗位链接',
    MODIFY COLUMN job_name VARCHAR(255) COMMENT '岗位名称',
    MODIFY COLUMN location VARCHAR(255) COMMENT '工作地点',
    MODIFY COLUMN salary VARCHAR(255) COMMENT '薪资',
    MODIFY COLUMN job_tags VARCHAR(255) COMMENT '工作标签',
    MODIFY COLUMN company VARCHAR(255) COMMENT '公司名称'
''')

conn.commit()
cursor.close()
conn.close()
