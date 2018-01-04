"""this file is used to text web crawling of www.programmableweb.com"""
import requests
from bs4 import BeautifulSoup

__author__ = 'Devon Ge'
__version__ = 4.0

HOME = r'https://www.programmableweb.com'


def html_code(url):
    """get html source code"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'}
    response = requests.get(url, headers)
    try:
        response.raise_for_status()
        response.encoding = 'utf-8'
        html = response.text
    except requests.exceptions.RequestException:
        html = ''
    return BeautifulSoup(html, 'html.parser') if html else None


class Api:
    """Class for web crawling on *programmablewebsite.com* """

    def __init__(self, page):
        """ Initialize an instance based on the page number of api list page"""
        self.url = f'https://www.programmableweb.com/category/all/apis?page={page}'
        self.name = ''
        self.submitted = ''
        self.suburl = ''
        self.links = ''
        self.category = ''
        self.lists = ''
        self.page = page

    def find_api_list(self):
        """ Get the api list (soup-like) of homepage """
        soup = html_code(self.url)
        body = soup.find('tr', class_='odd views-row-first').parent
        self.lists = body('tr')

    def analyze_api_list(self):
        """ Given an api, get its *name*, *category* and *submitted*
        and save its link for further analysis """
        api = self.lists.pop(0)
        attrs = api('td')
        self.name = attrs[0].a.string
        try:
            self.category = attrs[2].a.string.strip()
        except AttributeError:
            self.category = '-'
        self.submitted = attrs[3].string.strip()
        self.suburl = HOME + attrs[0].find('a')['href']

    def find_sdk_or_library(self, subca, flag):
        """ According to the flag, visit the sdk/library page of a given
        api, and get all the sdks'/libraries' links list
        flag=1 -> sdk; flag=0 -> library """
        if flag:
            soup = html_code(self.suburl + '/sdks')
        else:
            soup = html_code(self.suburl + '/libraries')
        sdlys = soup.find('table', class_='views-table cols-3 table')
        try:
            self.links = [HOME + api['href'] for api in sdlys('a')]
        except TypeError:
            with open(f'api{self.page}.txt', 'a', encoding='utf-8') as apifile:
                apifile.write(
                    f'{self.name}\t{self.submitted}\t{self.category}\tNo {subca}\n')

    def analyze_sdk_or_library(self, subca):
        """collect the specific sdk/library's information based on *self.links*,
        subcategory is a binary variable: SDK and Library"""
        soup = html_code(self.links.pop(0))
        title_generator = soup.find('h1')
        title = ''.join(title_generator.stripped_strings)
        spec = soup.find('div', class_='section specs')
        try:
            added = spec.find(
                'label', text='Added').next_sibling.next_sibling.string
        except AttributeError:
            added = '1900/01/01'
        try:
            category2 = spec.find(
                'label', text='Categories').next_sibling.next_sibling
            categories = ''.join(category2.stripped_strings)
        except AttributeError:
            categories = '-'
        try:
            provider = spec.find(
                'label', text=f'{subca} Provider').next_sibling.next_sibling.string
        except AttributeError:
            provider = '-'
        with open(f'api{self.page}.txt', 'a', encoding='utf-8') as apifile:
            apifile.write(f'{self.name}\t{self.submitted}\t{self.category}\
                \t{subca}\t{title}\t{provider}\t{added}\t{categories}\n')


def main(page):
    """ start the crawling here for all apis of the specific *page* """
    test = Api(page)
    test.find_api_list()
    while test.lists:
        test.analyze_api_list()
        loop = [('SDK', 1), ('Library', 0)]
        for (key, value) in loop:
            test.find_sdk_or_library(key, value)
            while test.links:
                test.analyze_sdk_or_library(key)


if __name__ == '__main__':
    from multiprocessing.pool import Pool
    with Pool(processes=4) as pool:
        pool.map(main, range(363, 0, -1))
