# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy

class HhParserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class HhunterItem(scrapy.Item):
    _id = scrapy.Field()
    vacancys_name = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    author = scrapy.Field()
    url = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    company_site = scrapy.Field()
    company_description = scrapy.Field()
    active_name = scrapy.Field()

