import requests
from fake_headers import Headers
import bs4
import re
import json

KEYWORDS = ['Django', 'Flask']

headers = Headers(browser="firefox", os="win")
headers_data = headers.generate()

response = requests.get("https://habr.com/all/", headers=headers_data)


parsed_articles = []

for area in range(1,3):
    link = "https://hh.ru/search/vacancy?text=python&area="+str(area)
    response1 = requests.get(link, headers=headers_data)
    if area == 1:
        city = 'Москва'
    else:
        city = 'Санкт-Петербург'

    main_page_data1 = response1.text
    main_page_soup1 = bs4.BeautifulSoup(main_page_data1, "lxml")
    div_article_list_tag1 = main_page_soup1.find_all('h3', class_='bloko-header-section-3')


    for person in div_article_list_tag1:
        h2_tag = person.find('span')
        if h2_tag == None:
            continue
        title = h2_tag.text
        a_tag = h2_tag.find('a')
        link = f"{a_tag['href']}"

        full_article_html = requests.get(link, headers=headers_data).text
        full_article_soup = bs4.BeautifulSoup(full_article_html, features='lxml')

        full_article_tag = full_article_soup.find('div', id='post-content-body')
        person_data = full_article_soup.find_all('meta')

        tags = full_article_soup.find_all(attrs={f'"href": {link}'})  # все записи с подсайта https://dtf.ru/hard
        #print(tags)
        full_title = full_article_soup.title
        tags = full_article_soup.find_all(attrs={"content": re.compile(r'Зарплата')})  # в атрибуте data-feed-name присутствует "pop"


        allNews = full_article_soup.findAll('div', class_='g-user-content')
        full_title = allNews[0].text


        allNews = full_article_soup.findAll('div', class_='vacancy-company-logo-redesigned')
        for data in allNews:
            if data.find('img') is not None:
                company = data.find('img')['alt']
                #print(company)

        allNews = full_article_soup.findAll('span', class_='bloko-header-section-2 bloko-header-section-2_lite')
        ZP = allNews[0].text

        flag = False

        for word in KEYWORDS:
            if (word in full_title):
                flag = True
                break
        if not flag:
            continue

        parsed_article = {
                    'city': city,
                    'company': company,
                    'link': link,
                    'ZP': ZP
        }


        parsed_articles.append(parsed_article)

print(parsed_articles)

with open("result.json", "w", encoding='utf-8') as outfile:
    for data in parsed_articles:
        json.dump(data, outfile)

