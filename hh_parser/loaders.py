from scrapy.loader import ItemLoader
from .items import HhunterItem
from itemloaders.processors import TakeFirst


def join_item(item):
    return "".join(item)

class HhunterLoader(ItemLoader):
    default_item_class = HhunterItem
    vacancys_name_out = TakeFirst()
    url_out = TakeFirst()
    salary_in = join_item
    salary_out = TakeFirst()
    description_in = join_item
    description_out = TakeFirst()
    author_in = join_item
    author_out = TakeFirst()
    company_name_in = join_item
    company_name_out = TakeFirst()
