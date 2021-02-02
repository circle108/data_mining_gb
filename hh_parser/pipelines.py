# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import pymongo

class HhParserPipeline:

    def process_item(self, item, spider):
        return item

class MongoSavePipeline:

    def __init__(self):
        self.db = pymongo.MongoClient(os.getenv('DATABASE'))

    def process_item(self, item, spider):
        db = self.db['HH_020221']
        collection = db[spider.name]
        collection.insert_one(item)
        return item
