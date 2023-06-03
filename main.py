"""
8. Стоимость = 10 баллов. Использование API. Требуется, используя, API В Контакте (или Facebook, yandex) получить информацию и вывести ее в удобочитаемом виде. Например, вывести
список друзей указанного пользователя, вывести названия фотоальбомов указанного пользователя и т. п.
"""

import csv
import requests

with open('token.txt', 'r') as file:
    token = file.read()
domain = 'sigmabbg'
owner_id = '501223642'


def take_100_posts():
    version = 5.92
    count = 10
    offset = 0
    all_posts = []
    while offset < 100:
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={
                                    'access_token': token,
                                    'v': version,
                                    'domain': domain,
                                    'count': count,
                                    'offset': offset
                                })

        data = response.json()['response']['items']
        offset += 10
        all_posts.extend(data)
    return all_posts


def get_friends():
    count = 10000
    version = 5.126
    field = 'sex'
    order = 'name'
    response = requests.get('https://api.vk.com/method/friends.get',
                            params={
                                'access_token': token,
                                'count': count,
                                'user_id': owner_id,
                                'order': order,
                                'v': version,
                                'fields': field
                            })
    friends = response.json()['response']['items']
    return friends


def file_friends(all_friends):
    with open('friends.csv', 'w', encoding='utf-8') as file:
        f = csv.writer(file)
        f.writerow(('sex', 'first_name', 'last_name'))
        for friend in all_friends:
            if friend['sex'] == 1:
                sex = 'girlboss'
            else:
                sex = 'malewife'
            f.writerow((sex, friend['first_name'], friend['last_name']))


def file_posts(all_posts):
    image_url = 'no pics 4u bbg'
    text = ''
    with open('posts.csv', 'w', encoding="utf-8") as file:
        f = csv.writer(file)
        f.writerow(('likes', 'body', 'url'))
        for post in all_posts:
            try:
                if post['copy_history'][0]['attachments'][0]['type']:
                    image_url = post['copy_history'][0]['attachments'][0]['photo']['sizes'][-1]['url']
            except:
                pass
            try:
                if post['copy_history'][0]['text']:
                    text = post['text'] + '\n' + post['copy_history'][0]['text']
            except:
                text = 'sorry bbg no tea 4u'
            f.writerow((post['likes']['count'], text, image_url))


file_posts(take_100_posts())
file_friends(get_friends())
print(1)
