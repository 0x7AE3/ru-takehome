import requests, time, json, re, os
from tqdm import tqdm
from tabulate import tabulate
import sqlite3

db_file = 'janestreet.db'
base_url = 'https://blackstone.wd1.myworkdayjobs.com'
