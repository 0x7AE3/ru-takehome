import requests, time, json, re, os
from tqdm import tqdm
from tabulate import tabulate
import sqlite3
from markdownify import markdownify as md

db_file = 'blackstone.db'
base_url = 'https://blackstone.wd1.myworkdayjobs.com'

def get_job_urls():
    api_endpoint = '/wday/cxs/blackstone/Blackstone_Campus_Careers/jobs'
    headers = {'content-type': 'application/json'}
    payload = {'appliedFacets': {}, 'searchText': '', 'limit': 20, 'offset': 0}
    job_urls = []
    while True:
        response = requests.post(
            base_url + api_endpoint,
            headers=headers,
            data=str(payload),
        )
        jobs_received = json.loads(response.text)['jobPostings']
        # print(json.dumps(jobs_received, indent=4))
        job_urls += [job['externalPath'] for job in jobs_received]
        if len(jobs_received) != 20: break
        payload['offset'] += 20
    return job_urls
    # return list(map(lambda url: re.search(r"^/job/[^/]+(/.*)$", url).group(1), job_urls))

def setup_db():
    if os.path.exists(db_file):
        print('Database already exists. Exiting...'); exit()
        # print('Database already exists. Deleting...'); os.remove(db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE jobs (
            title TEXT NOT NULL,
            description TEXT,
            location TEXT,
            human_url TEXT,
            api_url TEXT,
            posted_date TEXT,
            start_date TEXT,
            time_type TEXT
        )
    ''')
    return conn, cursor

def main():
    conn, cursor = setup_db()
    job_urls = get_job_urls()
    for job_url in tqdm(job_urls):
        api_endpoint = '/wday/cxs/blackstone/Blackstone_Campus_Careers' + job_url
        response = requests.get(base_url + api_endpoint)
        job_info = json.loads(response.text)['jobPostingInfo']
        cursor.execute('''
            INSERT INTO jobs (title, description, location, human_url, api_url, posted_date, start_date, time_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
            (job_info['title'], md(job_info['jobDescription']), job_info['location'], job_info['externalUrl'],
            base_url + api_endpoint, job_info['postedOn'], job_info['startDate'], job_info['timeType'])
        )
    conn.commit()
    conn.close()

main()
