# -*- coding: utf-8 -*-
import datetime
import socket
from urllib.parse import urljoin

from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose
from scrapy.spiders import CrawlSpider, Rule

from properties.items import PropertiesItem


class EasySpider(CrawlSpider):
    name = 'easy'
    allowed_domains = ['zu.fang.com']
    start_urls = ['http://sz.zu.fang.com/']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//*[@id="rentid_D10_01"]/a[7]')),
        Rule(LinkExtractor(
            restrict_xpaths='//*[contains(@class, "title")]'), callback='parse_item')
    )

    def parse_item(self, response):
        """ This function parses a property page.
        @url http://sz.zu.fang.com/chuzu/3_209831006_1.htm?channel=2,2
        @returns items 1
        @scrapes title price description address image_urls
        @scrapes url project spider server date
        """
        # create the loader using the response
        l = ItemLoader(item=PropertiesItem(), response=response)

        # Load fields using Xpath expressions
        l.add_xpath('title', '//h1[1]/text()',
                    MapCompose(str.strip, str.title))
        l.add_xpath('price', '/html/body/div[5]/div[1]/div[2]/div[2]/div/i/text()',
                    MapCompose(lambda i: i.replace(',', ''), float), re='[.0-9]+')
        l.add_xpath('description', '/html/body/div[5]/div[1]/div[2]/div[3]/div[2]/div[1]/text()',
                    MapCompose(str.strip), Join())
        l.add_xpath('address', '/html/body/div[5]/div[1]/div[2]/div[5]/div[3]/div[2]/a/text()',
                    MapCompose(str.strip), Join())
        l.add_xpath('image_urls', '//*[@id="agantzfxq_C02_06"]/div[1]/ul/li[1]/img/@src',
                    MapCompose(lambda i: urljoin(response.url, i)))

        # Housekeekping fields
        l.add_value('url', response.url)
        l.add_value('project', self.settings.get('BOT_NAME'))
        l.add_value('spider', self.name)
        l.add_value('server', socket.gethostname())
        l.add_value('date', datetime.datetime.now())

        return l.load_item()
