from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hh_parser.spiders.headhunter import HeadhunterSpider
from dotenv import load_dotenv
from hh_parser.spiders.instagram import InstagramSpider
from hh_parser.spiders.zillow import ZillowSpider
import os



if __name__ == '__main__':
    load_dotenv('.env')
    crawler_settings = Settings()
    crawler_settings.setmodule('hh_parser.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(InstagramSpider, login=os.getenv('LOGIN'), password=os.getenv('ENC_PASSWORD'))
    # crawler_process.crawl(ZillowSpider)
    crawler_process.start()