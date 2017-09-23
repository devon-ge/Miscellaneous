# 爬取豆瓣250
import requests
from bs4 import BeautifulSoup

HOMEPAGE = 'https://movie.douban.com/top250'


def get_html_text(url, code='utf-8'):
    """get html source code"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
               '(KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = code
        return response.text
    except requests.exceptions.RequestException:
        return ''


def main(page):
    homepage = HOMEPAGE + min(1, page) * f'?start={page*25}&filter='
    soup = BeautifulSoup(get_html_text(homepage), 'html.parser')
    movielist = soup('ol')[0]
    for movie in movielist('li'):
        title = movie('span', class_='title')[0].string
        try:
            rating = movie('span', class_='rating_num')[0].string
        except IndexError:
            rating = '无评分'
        try:
            comments = movie('span', class_='inq')[0].string
        except IndexError:
            comments = '无评论'
        with open('douban2500.txt', 'a', encoding='utf-8') as f:
            f.write(f'{title:8}\t{rating:2}\t{comments}\n')


if __name__ == '__main__':
    for i in range(9):
        main(i)