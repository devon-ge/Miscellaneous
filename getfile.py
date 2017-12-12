"""This module is used to get all the articles' in some websites"""

import os
import sys
import time
import urllib.request
from collections import deque
import re

import requests
from bs4 import BeautifulSoup

__author__ = 'Devon Ge'
__version__ = 3.0

DOMAIN = 'http://www.siilu.com/news/guide/'

os.chdir('E:\PHBS\datapro\contents\SiLuWang\SiLuShangDao\FuWuZiXun')


def get_html_text(url, code='gbk'):
    """get html source code"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      ' (KHTML, like Gecko) Chrome/60.0.3163.91 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = code
        return response.text
    except requests.exceptions.RequestException:
        return ''


def get_article_list(nav, article_tag):
    """输入二级目录的网址*nav*，根据*article_tag*识别本页面所有文章链接，并返回"""
    article_list = []
    soup = BeautifulSoup(get_html_text(nav), 'html.parser')
    articles = soup.find_all(article_tag)
    for article in articles:
        article_list.append(article.a['href'])
    return article_list


def get_article(article_list):
    """根据输入的特定文章网址，输出文章的标题"""
    soup = BeautifulSoup(get_html_text(article_list), 'html.parser')
    # bullshit = soup.find_all('h1')
    # title = bullshit[0].string
    # sss = soup.find_all('div', cl.ass_='titsle_zouo')
    filename = os.path.basename(article_list).split('.')[0]
    paras = soup.find_all('p', class_='newtext')
    with open(filename + '.txt', 'w', encoding='utf-8') as f:
        for par in paras[1:-1]:
            if par.string:
                f.write(par.string + '\n\n')


def main(page=1):
    """爬虫从这里开始"""
    article_list = get_article_list(DOMAIN + str(page) + '.html', 'h3')
    for article in article_list:
        get_article(article)


if __name__ == '__main__':
    from multiprocessing.pool import Pool
    with Pool(4) as p:
        for i in range(1, 53):
            p.map(main, [4 * i - 3, 4 * i - 2, 4 * i - 1, 4 * i])
