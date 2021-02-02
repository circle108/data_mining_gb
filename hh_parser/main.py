from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hh_parser.spiders.headhunter import HeadhunterSpider
from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv('.env')
    crawler_settings = Settings()
    crawler_settings.setmodule('hh_parser.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HeadhunterSpider)
    crawler_process.start()