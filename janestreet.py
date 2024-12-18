import requests, time, json, re, os
from tqdm import tqdm
from tabulate import tabulate
import sqlite3
from markdownify import markdownify as md

db_file = 'janestreet.db'
base_url = 'https://www.janestreet.com/'
all_jobs_url = base_url + 'jobs/main.json'
student_and_newgrad_url = base_url + 'jobs/internships.json'
job_query_url = base_url + 'join-jane-street/position/'

city_conversion = {
    'NYC': 'New York', 'LDN': 'London', 'HKG': 'Hong Kong', 'AMS': 'Amsterdam',
    'CHI': 'Chicago', 'SGP': 'Singapore', 'MUM': 'Mumbai', 'SHA': 'Shanghai',
    'PHL': 'Philadelphia', 'SF': 'San Francisco', 'NYC/HKG': 'New York/Hong Kong',
    'All Locations': 'All Locations'
}

def setup_db():
    if os.path.exists(db_file):
        print('Database already exists. Exiting...'); exit()
        # print('Database already exists. Deleting...'); os.remove(db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE jobs (
            position TEXT NOT NULL,
            category TEXT,
            availability TEXT,
            city TEXT,
            url TEXT,
            overview TEXT,
            team TEXT,
            min_salary TEXT,
            max_salary TEXT
        )
    ''')
    return conn, cursor

def main():
    conn, cursor = setup_db()
    jobs = requests.get(all_jobs_url).json()
    # jobs = requests.get(student_and_newgrad_url).json()
    for job in jobs:
        cursor.execute('''
            INSERT INTO jobs (position, category, availability, city, url, overview, team, min_salary, max_salary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (job['position'], job['category'], job['availability'], city_conversion[job['city']],
            job_query_url + job['position'], md(job['overview']), job['team'], job['min_salary'], job['max_salary'])
        )
    conn.commit()
    conn.close()

main()
