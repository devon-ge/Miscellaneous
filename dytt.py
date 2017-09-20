# dyytt.py
# -*- coding: utf-8 -*-
import re, requests
from bs4 import BeautifulSoup
from collections import deque
        
def getHTMLText(url, code='utf-8'):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return ''

def getMoiveInfoUrl(movie_queue, Url):
    '''返回值是一个链接，对应电影的介绍页面'''
    html = getHTMLText(Url)
    soup = BeautifulSoup(html, 'html.parser')
    a = soup.find_all('a')
    for i in a:
        try:
            href = i.attrs['href']
            movie_queue.append(re.findall(r'http://.+?/\d{8}/\d{4,5}\.html', href)[0])
        except:
            continue

def getDownloadUrl(MoviePage):
    '''MoviePage 是电影介绍的网页地址，返回值是ftp下载链接, 如无匹配链接，返回空字符'''
    pattern = re.compile(r'ftp://.+?\.rmvb|ftp://.+?\.mkv')
    html = getHTMLText(MoviePage, 'gb2312')
    match = re.findall(pattern, html)
    if bool(match):
        return match[0]
    else:
        return 'Error' 

def getMovieName(downloadLink):
    '''输入ftp链接，使用正则表达式分析文本，返回电影名字'''
    name_patten = re.compile(r'\](?!/)\.?(.+?)\.[a-z]{3,4}$')   #结果是xxx.rmvb 或xxx.mkv
    name_match = re.findall(name_patten, downloadLink)
    if bool(name_match):
        return name_match[0].split('.')[0]
    else:
        return 'None'        

def main():
    movie_start_url = 'http://www.dytt8.net/html/gndy/jddy/20160320/50523' # score: imdb 8.0+
    links_output_file = 'links.txt'
    Movie_queue = deque([])
    Download_queue = deque([])
    getMoiveInfoUrl(Movie_queue, movie_start_url + '.html')
    for page in range(2, 5):
        getMoiveInfoUrl(Movie_queue, movie_start_url + '_' + str(page) + '.html')
    j = 1
    #=========================暂时的处理方式=========================
    while Movie_queue:
        downloadLink = getDownloadUrl(Movie_queue.popleft())
        name = getMovieName(downloadLink)
        if name != 'None':
            Download_queue.append(str(j) +'\t' + name + '\t' + downloadLink)
            j += 1
    #==========================================================================
    with open(links_output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(Download_queue))
if __name__ == '__main__':
    main()
