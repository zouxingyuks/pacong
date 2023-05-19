import mysql
import psycopg2

from dao.init import get_mysql_config

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

conn = mysql.connector.connect(
    host=config['host'],
    port=config['port'],
    user=config['user'],
    password=config['password'],
    database=config['database']
)
cursor = conn.cursor()

# 创建jobs表
cursor.execute('''
    CREATE TABLE jobs (
        id SERIAL PRIMARY KEY, 
        job_link VARCHAR(255),
        job_name VARCHAR(255),
        location VARCHAR(255), 
        salary VARCHAR(255),
        job_tags VARCHAR(255),
        company VARCHAR(255)
    )
''')

# 创建字段注释
cursor.execute('''
    COMMENT ON COLUMN 
        jobs.job_link IS '岗位链接';
    COMMENT ON COLUMN  
        jobs.job_name IS '岗位名称';
    COMMENT ON COLUMN  
        jobs.location IS '工作地点';
    COMMENT ON COLUMN
        jobs.salary IS '薪资';  
    COMMENT ON COLUMN 
        jobs.job_tags IS '工作标签';
    COMMENT ON COLUMN  
        jobs.company IS '公司名称';       
''')

conn.commit()
cursor.close()
conn.close()
