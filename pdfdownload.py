"""This file is used to web-crawl *sec.gov* for proxy statement def 14a and save to pdf files"""

__version__ = 2.0

import pdfkit
import scrapy

__author__ = 'Devon Ge'
__email__ = '1701213756@sz.pku.edu.cn'

config = pdfkit.configuration(
    wkhtmltopdf=r'D:\wkhtmltopdf\bin\wkhtmltopdf.exe')


class Sec(scrapy.Spider):
    """ web crawling on sec.gov of """
    name = 'sec'
    # allowed_domain = ['sec.gov']
    with open(r'E:\Programming\Scrapy\sec\sec\spiders\sorteds.txt', 'r') as f:
        start_urls = [
            'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s\
            &type=DEF 14A&dateb=&owner=exclude&count=40' % cik for cik in f.readlines()
        ]

    def parse(self, response):
        """parse the list of def 14 htmls """
        for url in response.xpath('//*[@id="documentsbutton"]'):
            yield response.follow(url, callback=self.parse_article)

    def parse_article(self, response):
        """parse a give def 14 files and covert the html into pdf"""
        options = {'quiet': ''}  # Do not show the prompts
        filename = response.url.split(
            '/')[6] + '_' + response.css('div.info::text').extract_first()
        url = response.css('a::attr(href)').re(r'/Ar.*[(html?)|(txt)]')[0]
        yield pdfkit.from_url('http://www.sec.gov'+url, '%s.pdf' %
                        filename, configuration=config, options=options)
        self.log('Saved file %s' % filename)
