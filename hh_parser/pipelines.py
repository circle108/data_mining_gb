# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import pymongo
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline

class HhParserPipeline:

    def process_item(self, item, spider):
        return item

class MongoSavePipeline:

    def __init__(self):
        self.db = pymongo.MongoClient(os.getenv('DATABASE'))

    def process_item(self, item, spider):
        db = self.db['Instagram']
        collection = db[type(item).__name__]
        collection.insert_one(item)
        return item

class InsImages(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield Request(item.get('images'))
    #
    # def item_completed(self, results, item, info):
    #     item = [itm[1] for itm in results]
    #     return item
