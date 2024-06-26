import sqlite3
from src.database import NewsFeature
import csv
from bs4 import BeautifulSoup
import requests
from src.utility_functions import resource_path_gp
def update_single_news_row(name, data, index):
    conn = sqlite3.connect('src/database/news.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE articles SET {name} = ? WHERE url = ?', (data, index))
    conn.commit()
    conn.close()

def companies_of_interest():
    companies = []
    coi_path= resource_path_gp('res/companies_of_interest.csv')
    with open(coi_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > 0:
                companies.append(row[0])
    return companies

def contains_any(string, string_list):
    return any(s in string for s in string_list)

def find_all(string, string_list):
    list= [s for s in string_list if s in string]
    return list

def scrape_content(url):
    try:
        page = requests.get(url)
    except:
        return ''
    soup = BeautifulSoup(page.content, 'html.parser')
    content = soup.find_all('p')
    data = ''
    for i in content:
        data += i.text
    return data

def update_all_news():
    conn = sqlite3.connect('src/database/news.db')
    cursor = conn.cursor()
    table_name = 'articles'
    query = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(query)
    result = cursor.fetchone()
    row_count = result[0]
    companies_of_interest_list = companies_of_interest()
    for i in range(1, row_count+1):
        curr_news= NewsFeature.NewsFeature(i)
        row = curr_news.row
        url = curr_news.url
        if('chars' in curr_news.content):
            data = scrape_content(url)
            update_single_news_row('content', data, url)
        if(curr_news.companies == ''):
            companies = ''.join(find_all(row[7], companies_of_interest_list))
            if(companies == ''):
                cursor.execute('UPDATE articles SET companies = ? WHERE id = ?', (companies, row[0]))
        conn.commit()
    conn.close()
def update_single_news(id):
    conn = sqlite3.connect('src/database/news.db')
    cursor = conn.cursor()
    curr_news= NewsFeature.NewsFeature(id)
    row = curr_news.row
    url = curr_news.url
    if('chars' in curr_news.content):
        data = scrape_content(url)
        update_single_news_row('content', data, url)
    if(curr_news.companies == ''):
        companies = ''.join(find_all(row[7], companies_of_interest()))
        if(companies == ''):
            cursor.execute('UPDATE articles SET companies = ? WHERE id = ?', (companies, row[0]))
    conn.commit()
    conn.close()