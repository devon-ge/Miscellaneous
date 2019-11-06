"""auto login github.com"""
import os
import re

import requests
from bs4 import BeautifulSoup

CLASSROOM = r'https://github.com/login?return_to=%2FPHBS-2017-ASP-Classroom?page=4'
USERNAME = 'youremail'
PASSWORD = 'yourpassword'


class Github:
    """auto login github"""

    def __init__(self, homework, login_url=CLASSROOM, session_url=r'https://github.com/session'):
        self.headers = {
            'Host': 'github.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0)'
                          'Gecko/20100101 Firefox/56.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://github.com/',
            'Connection': 'keep-alive',
        }
        self.homework = homework
        self.ses = requests.Session()
        self.login_url = login_url
        self.session_url = session_url
        self.replist = []

    def html_text(self, code='utf-8'):
        """get html source code"""
        try:
            response = self.ses.get(self.login_url, headers=self.headers)
            response.raise_for_status()
            response.encoding = code
            return response.text
        except requests.exceptions.RequestException:
            return ''

    def get_token(self):
        ''' get token to login github.com '''
        html = self.html_text()
        pattern = re.compile(
            r'<input name="authenticity_token" type="hidden" value="(.*)" />')
        token = pattern.findall(html)[0]
        return token

    def login(self):
        ''' login in github.com and return the html code '''
        token = self.get_token()
        login_data = {
            'commit': 'Sign in',
            'utf8': '%E2%9C%93',
            'authenticity_token': token,
            'login': USERNAME,
            'password': PASSWORD
        }
        resp = self.ses.post(
            self.session_url, headers=self.headers, data=login_data)
        return resp.text

    def repository(self):
        ''' get the repository of homework '''
        soup = BeautifulSoup(self.login(), 'html.parser')
        tags = soup.find_all('h3')
        for tag in tags:
            if self.homework in tag.a['href']:
                self.replist.append(tag.a['href'])
        return self.replist

    def clone(self):
        ''' clone students' homeworks to my local disk '''
        lists = self.repository()
        os.chdir('.')
        for rep in lists:
            command = f'git clone https://github.com{rep}.git'
            os.system(command)


if __name__ == '__main__':
    Login = Github('hw2')
    Login.clone()
