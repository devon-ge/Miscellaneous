# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose
from scrapy.spiders import CrawlSpider, Rule

from movies.items import MoviesItem


class DoubanSpider(CrawlSpider):
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['https://movie.douban.com/top250']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//*[contains(@rel, "next")]')),
        Rule(LinkExtractor(
            restrict_xpaths='//*[contains(@class, "pic")]'), callback='parse_item')
    )

    def parse_item(self, response):
        """ This function parses a property page.
        @url https://movie.douban.com/top250
        @returns items 1
        @scrapes name score category url year
        """
        # create the loader using the response
        l = ItemLoader(item=MoviesItem(), response=response)

        # Load fields using Xpath expressions
        l.add_xpath('name', '//h1[1]/span[1]/text()',
                    MapCompose(str.strip, str.title))
        l.add_xpath('score', '//*[contains(@class, "ll rating_num")]//text()',
                    MapCompose(lambda i: i.replace(',', ''), float), re='[.0-9]+')
        l.add_xpath('category', '//*[contains(@property, "v:genre")]//text()',
                    MapCompose(str.strip), Join())
        l.add_xpath('year', '//*[@id="content"]/h1/span[2]/text()', MapCompose(int), re='[0-9]+')
        l.add_value('url', response.url)

        return l.load_item()
