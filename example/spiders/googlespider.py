from urllib.parse import urljoin, urlparse, parse_qsl
import datetime
import scrapy
#from scrapy.http import Request
# from scrapy.selector import HtmlXPathSelector
# from scrapy.spider import BaseSpider
# from scrapy.utils.response import get_base_url
from scrapy.utils.misc import arg_to_iter
from example.items import GoogleSearchItem

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
        filename = "test.html"

        with open(filename, 'w') as f:
            for h3 in response.xpath('//div[@id="ires"]//li[@class="g"]//h3[@class="r"]').getall():
                print('xxx: ', h3)
                f.write(h3)
        # filename = "test.html"

        # with open(filename, 'wb') as f:
        #     questions = response.xpath('//div[@id="ires"]//li[@class="g"]//h3[@class="r"]').get().strip()
            #questions = questions[:-12]
            #f.write(questions.encode())
            #f.write(response.body)