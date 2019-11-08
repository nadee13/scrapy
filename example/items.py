# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags
from scrapy.item import Item, Field


class ExampleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def remove_whitespace(value):
    return value.strip()

class JokeItem(scrapy.Item):
    joke_text = scrapy.Field(
        input_processor= MapCompose(remove_tags, remove_whitespace),
        output_processor= TakeFirst()
    )

class GoogleSearchItem(Item):
    name = Field()
    region = Field()
    url = Field()
    html = Field()
    query = Field()
    crawled = Field()