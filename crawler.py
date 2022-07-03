import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re
import time
import pandas as pd

headers = {}

# page_url = r'https://movie.douban.com/j/new_search_subjects?sort=U&tags=%E7%94%B5%E5%BD%B1&start={}&year_range=1990,1999' # 90s
page_url = r'https://movie.douban.com/j/new_search_subjects?sort=U&tags=%E7%94%B5%E5%BD%B1&start={}&year_range=2019,2019' # 2019

# get all names & ids from a node of person-a-hrefs
def get_all_person_info(persons):
    ids = []
    names = []
    for person in persons.find_all('a'):
        ids.append(person['href'][-8:-1])
        names.append(person.string)
    return names, ids

try:
    data = pd.read_csv('data.csv', index_col=0)
except:
    data = pd.DataFrame(columns=['id', 'title', 'cover',
                                 'director_names', 'scriptor_names', 'actor_names',
                                 'director_ids', 'scriptor_ids','actor_ids',
                                 'genre', 'language', 'made_in', 'date', 'length',
                                 'summary', 'average_rating', 'num_votes',
                                 'rating_percentage', 'type', 'related'], )

for start in range(len(data), 2000, 20):
    page = requests.get(page_url.format(start), headers=headers).json()['data']
    print(start, page)
    for movie in page:
        info = {}
        info['id'] = movie['id']
        info['title'] = movie['title']
        info['cover'] = movie['cover']
        info['type'] = '电影'

        time.sleep(6)
        details = BeautifulSoup(requests.get(movie['url'], headers=headers).text,
                                'html.parser')

        info_content = details.find(id='info').contents

        info['genre'] = []
        for idx, item in enumerate(info_content):
            item_txt = item.get_text()
            if '导演: ' in item_txt:
                info['director_names'], info['director_ids'] = \
                    get_all_person_info(item)
            elif '编剧: ' in item_txt:
                info['scriptor_names'], info['scriptor_ids'] = \
                    get_all_person_info(item)
            elif '主演: ' in item_txt:
                info['actor_names'], info['actor_ids'] = \
                    get_all_person_info(item)
            elif '制片国家/地区' in item_txt:
                info['made_in'] = info_content[idx + 1].string
            elif '语言' in item_txt:
                info['language'] = info_content[idx + 1].string
            elif '上映日期' in item_txt:
                info['date'] = info_content[idx + 2].string
            elif '片长' in item_txt:
                info['length'] = info_content[idx + 2].string

            if isinstance(item, Tag) and item.get('property', None) == 'v:genre':
                info['genre'].append(item.string)
            pass

        if details.find(property='v:summary'):
            info['summary'] = ''.join(details.find(property='v:summary').stripped_strings)

        if details.find(property='v:average'):
            info['average_rating'] = details.find(property='v:average').string
        if details.find(property='v:votes'):
            info['num_votes'] = details.find(property='v:votes').string

        info['rating_percentage'] = []
        # 'class' is keyword of Python
        star_items = details.find_all(attrs={'class':'rating_per'})
        for item in star_items:
            info['rating_percentage'].append(item.string)

        info['related'] = []
        related = details.find(attrs={'class': 'recommendations-bd'})
        if related:
            for dt in related.find_all('dt'):
                info['related'].append(dt.a['href'][-26:-19])

        data = data.append(info, ignore_index=True)
        print('.', end='')
        pass
    print('done:', start)
    data.to_csv('data.csv')

        


