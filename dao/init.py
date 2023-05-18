import os

import mysql.connector
import yaml


def get_mysql_config():
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'config.yaml')
    try:
        with open(config_file, encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config['mysql']
    except IOError:
        print('文件不存在,新建 config/config.yaml 文件...')
        config = {'mysql': {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'password',
            'database': 'jobs'
        }}
        with open('config/config.yaml', 'w') as f:
            yaml.dump(config, f)
        return config['mysql']


def save_jobs_to_mysql(jobs):
    config = get_mysql_config()
    conn = mysql.connector.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    cursor = conn.cursor()

    for job in jobs:
        cursor.execute('''
            INSERT INTO jobs (job_link, job_name, location, salary, job_tags, company) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (job['job_link'], job['job_name'], job['location'], job['salary'],
              job['job_tags'], job['company']))
    conn.commit()
    cursor.close()
    conn.close()
