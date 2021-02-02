import scrapy
from ..loaders import HhunterLoader


class HeadhunterSpider(scrapy.Spider):
    name = 'headhunter'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    xpath = {
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
        'vacancy': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    }
    xpath_vacancy = {
        'vacancys_name': '//h1[@data-qa="vacancy-title"]/text()',
        'salary': '//p[@class="vacancy-salary"]//text()',
        'description': '//div[@data-qa="vacancy-description"]//text()',
        'skills': '//div[@class="bloko-tag-list"]//text()',
        'author': '//a[@data-qa="vacancy-company-name"]//text()',
        'company_url': '//a[@data-qa="vacancy-company-name"]/@href',
    }

    xpath_company = {
        'company_url': '//h1[@data-qa="bloko-header-1"]//text()',
        'company_site': '//a[contains(@data-qa, "sidebar-company-site")]/@href',
        'company_description': '//div[@class="g-user-content"]//text()',
    }

    xpath_active_vac = {
        'company_url':'//a[contains(@data-qa,"employer-page")]/@href',
        'active_name': '//a[contains(@data-qa,"vacancy-serp__vacancy-title")]//text()',
        'active_url': '/a[contains(@data-qa,"employer-page")]/@href',
    }

    def parse(self, response, **kwargs):
        pagination_list = response.xpath(self.xpath['pagination'])
        for pag in pagination_list:
            yield response.follow(pag, callback=self.parse)
        vacancy_list = response.xpath(self.xpath['vacancy'])
        for vacancy in vacancy_list:
            yield response.follow(vacancy, callback=self.vacancy_parser)

    def vacancy_parser(self, response):
        loader = HhunterLoader(response=response)
        loader.add_value('url', response.url)
        for key, value in self.xpath_vacancy.items():
            loader.add_xpath(key, value)
        item = loader.load_item()
        yield item
        yield response.follow(
                response.xpath(self.xpath_vacancy["company_url"]).get(), callback=self.company_parser
            )

    def company_parser(self, response, **kwargs):
        loader = HhunterLoader(response=response)
        for key, value in self.xpath_company.items():
            loader.add_value(key, value)
        item = loader.load_item()
        yield item
        yield from self.active_vacancy(response)

    def active_vacancy(self, response):
        loader = HhunterLoader(response=response)
        for key, value in self.xpath_company.items():
            loader.add_xpath(key, value)
        item = loader.load_item()
        yield item
