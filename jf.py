"""This module is used to get all the articles' information published in Journal of Finance"""

__author__ = 'Devon Ge'
__version__ = 2.0

import os
import time
import urllib.request
from collections import deque

import requests
from bs4 import BeautifulSoup


def get_html_text(url, code='utf-8'):
    '''get html source code'''
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                             ' (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/53.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = code
        return response.text
    except requests.exceptions.RequestException:
        return ''


def get_url(soup):
    '''extract pseudo-urls (for redirection) as a queue from  soup object '''
    pseudo_url = deque()
    for article in soup('a', text='References'):
        pseudo_url.append('http://onlinelibrary.wiley.com'
                          + article.parent.previous_sibling.a['href'])
    return pseudo_url


def download_articles(urls):
    '''use urlretrieve download articles from a given urls and name articles.'''
    i = 1
    while urls:
        soup = BeautifulSoup(get_html_text(urls.popleft()), 'html.parser')
        urltag = soup.find_all('iframe', id='pdfDocument')
        url = urltag[0]['src']
        print(f'\n正在下载:第{i}篇文章')
        start = time.time()
        urllib.request.urlretrieve(url, '{:02}.pdf'.format(i))
        print(f'下载完成，用时: {time.time()-start:.3}秒')
        print('-----------------------------', end='')
        i += 1
        time.sleep(1)


def main():
    '''start here'''
    maindir = r'E:\Programming\Python\Crawl\JF'
    os.chdir(maindir)
    domain = 'http://onlinelibrary.wiley.com'
    homepage = domain + '/journal/10.1111/(ISSN)1540-6261'
    soup = BeautifulSoup(get_html_text(homepage), 'html.parser')
    find_issue = soup('a', id="currentIssueLink")

    while find_issue:
        issue_url = domain + find_issue[0].attrs['href']
        time.sleep(2)
        try:
            soup = BeautifulSoup(get_html_text(issue_url), 'html.parser')
            urlqueue = get_url(soup)
            issue_info = soup('title')
            month = issue_info[0].string.split(' - ')[2]
            volume = issue_info[0].string.split(' - ')[1].split(', ')[0]
            # 根据volume 和issue month 创建文件夹
            if os.path.exists(volume):
                os.chdir(volume)
                if os.path.exists(month):   #说明这一卷下载过了，随便选一个Exception
                    raise ValueError
            else:
                os.mkdir(volume)
                os.chdir(volume)
            os.mkdir(month)
            os.chdir(month)
            download_articles(urlqueue)
        except Exception:
            time.sleep(1)
        finally:
            find_issue = soup('a', id="previousLink")
            os.chdir(maindir)  # 回到主目录


if __name__ == '__main__':
    main()
