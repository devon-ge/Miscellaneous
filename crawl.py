import os

import requests
from bs4 import BeautifulSoup

HOME = r'http://www.hikvision.com/cn/'
START = r'http://www.hikvision.com/cn/prlb_1608.html'


def html_text(url, code='utf-8'):
    """get html source code"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = code
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException:
        return None


def camera(url=None):
    result = []
    soup = html_text(url)
    cameras = soup.find('ul', class_='clearfix')
    titles = cameras.find_all('li')
    # issue ------------------------------------
    for title in titles:
        result.append(HOME + title.find('a').[href])
    return result
    # -----------------------------------------------
    # find **sources**


sources = camera(START)


def write_results(source):
    """ write a txt.file """
    soup = html_text(source)
    # find list
    lists = soup.find('li', class_='prdlli')
    chi = lists.find_all('div')
    urls = [HOME + ch.a['href'] for ch in chi]
    # print(url)
    with open('results.txt', 'w') as f:
        for url in urls:
            # find products mix
            soup2 = get_html_text(url)
            product = soup2.find('div', class_='pagelist5 clearfix')
            # # single product
            results = product.find_all('div', class_='jjfajsh1')
            for result in results:
                f.write(result.find('div', 'jjfajshh3').string + '\n')
