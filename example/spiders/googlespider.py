from urllib.parse import urljoin, urlparse, parse_qsl
import datetime
import scrapy
# from scrapy.http import Request
# from scrapy.selector import HtmlXPathSelector
# from scrapy.spider import BaseSpider
# from scrapy.utils.response import get_base_url
from scrapy.utils.misc import arg_to_iter
from example.items import GoogleSearchItem
from example.items import JokeItem
from scrapy.loader import ItemLoader

import urllib.parse as urlparse
from urllib.parse import parse_qs
import json

COUNTRIES = {
    'ie': 'countryIE',
    'nl': 'countryNL'
}

"""
A spider to parse the google search result bootstraped from given queries.
"""
class GoogleSearchSpider(scrapy.Spider):
    name = 'googlesearch'
    queries = ('contact us', 'hotel')
    region = 'ie'
    download_delay = 5
    base_url_fmt = 'http://www.google.{region}/search?hl=en&as_q=&as_epq={query}&as_oq=&as_eq=&as_nlo=&as_nhi=&lr=&cr={country}&as_qdr=all&as_sitesearch=&as_occt=any&safe=images&tbs=&as_filetype=&as_rights='
    download_html = False
    limit_country = False

    print('base_url_fmt: ', base_url_fmt)

    def start_requests(self):
        print('self.queries: ', self.queries)
        for query in arg_to_iter(self.queries):
            url = self.make_google_search_request(COUNTRIES[self.region], query)
            print('url: ', url)
            yield scrapy.Request(url=url, meta={'query': query}, callback=self.parse)

    def make_google_search_request(self, country, query):
        if not self.limit_country:
            country = ''
        return self.base_url_fmt.format(country=country, region=self.region, query='+'.join(query.split()).strip('+'))

    def parse(self, response):
        filename = "test.json"
        test = response.xpath('//div[@id="search"]').extract()
        print('test: ', test)

        final_json = {}
        final_json['search_results'] = []
        final_json['related_searches'] = []

        title = ''
        url = ''
        snippet = ''

        # Search results
        for div in response.xpath('//div[@id="main"]//div[@class="ZINbbc xpd O9g5cc uUPGi"]'):
            count = 0
            while count != 2:
                if count % 2 :
                    title = div.xpath('.//div[@class="kCrYT"]//div[@class="BNeawe vvjwJb AP7Wnd"]/text()').extract_first()
                    href = div.xpath('.//div[@class="kCrYT"]/a/@href').extract_first()
                    if href is not None:
                        parsed = urlparse.urlparse(href)
                        url = parse_qs(parsed.query)['q'][0]
                    count += 1
                else:
                    snippet = div.xpath('.//div[@class="kCrYT"]//div[@class="BNeawe s3v9rd AP7Wnd"]/text()').extract_first()
                    count += 1

            # il = ItemLoader(item=GoogleSearchItem(), selector=div)
            # il.add_xpath('title', './/div[@class="BNeawe vvjwJb AP7Wnd"]/text()')
            # il.add_xpath('url' , './a/@href')
            # il.add_xpath('snippet' , './/div[@class="BNeawe s3v9rd AP7Wnd"]/text()')
            # test12 = il.load_item()
            # print('test12', test12)
            temp = {
                'title': title,
                'url' : url,
                'snippet' : snippet,
            }

            if temp['title'] is not None:
                #print('srch_res_temp: ', temp)
                final_json['search_results'].append(temp)
                #print("final_json['search_results']: ", final_json['search_results'])

        # Related searches
        for div in response.xpath('//div[@id="main"]//div[@class="X7NTVe"]'):
            title = div.xpath('.//div[@class="am3QBf"]//div[@class="BNeawe deIvCb AP7Wnd"]/text()').extract_first()
            temp_url = div.xpath('./a/@href').extract_first()
            if temp_url is not None:
                url = 'www.google.com' + temp_url

            temp = {
                'title': title,
                'url' : url,
            } 
            if temp['title'] is not None:
                #print('temp: ', temp)
                final_json['related_searches'].append(temp)
                #print("final_json['related_searches']: ", final_json['related_searches'])           
        # with open(filename, 'ab') as f:
        #     divs = response.xpath("//div[@id='rso']")            
        #     f.write(divs)
        #     for div in divs:
        #         print('xxx: ', div)
        #         f.write(div) #test this
        #         l = ItemLoader(item=JokeItem(), selector=div)
        #         l.add_xpath('joke_text', ".//div[@class='bkWMgd']//span")             
        #         yield l.load_item()
        #             #print('xxx: ', div)
        # filename = "test.html"

        with open(filename, 'w') as f:
            #questions = response.xpath('//div[@id="rso"]//div[@class="bkWMgd"]//span/text()').get().strip()
            #questions = questions[:-12]
            #f.write(questions.encode())        
            json_data = json.dumps(final_json)
            print('json_data: ', json_data)
            json.dump(final_json, f)
