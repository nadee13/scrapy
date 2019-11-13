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
    base_url_fmt = 'http://www.google.{region}/search?hl=en&tbm=nws&as_q=&as_epq={query}&as_oq=&as_eq=&as_nlo=&as_nhi=&lr=&cr={country}&as_qdr=all&as_sitesearch=&as_occt=any&safe=images&tbs=&as_filetype=&as_rights='
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
        test = response.xpath('//div/@id')
        print('test: ', test)

        final_json = {}
        final_json['search_results'] = {}
        final_json['related_searches'] = {}

        # Search results
        for div in response.xpath('//div[@id="main"]//div[@class="kCrYT"]'):
            srch_res_temp = yield {
                'srch_res_title': div.xpath('.//div[@class="BNeawe vvjwJb AP7Wnd"]/text()').extract_first(),
                'srch_res_url' : div.xpath('./a/@href').extract_first(),
                'srch_res_snippet' : div.xpath('.//div[@class="BNeawe s3v9rd AP7Wnd"]/text()').extract_first(),
            }
            print('srch_res_temp: ', srch_res_temp)
            final_json['search_results'].update(srch_res_temp)

        # Related searches
        for div in response.xpath('//div[@id="main"]//div[@class="X7NTVe"]'):
            rel_srch_temp = {
                'rel_srch_title': div.xpath('.//div[@class="am3QBf"]//div[@class="BNeawe deIvCb AP7Wnd"]/text()').extract_first(),
                'rel_srch_url' : div.xpath('./a/@href').extract_first(),
            }            
            final_json['related_searches'].update(rel_srch_temp)

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
