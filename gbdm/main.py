from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gbdm import settings
from gbdm.spiders.avito import AvitoSpider
from gbdm.spiders.youla import YoulaSpider
from pathlib import Path


if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)

    crawl_proc = CrawlerProcess(settings=crawl_settings)


    #crawl_proc.crawl(AvitoSpider)
    crawl_proc.crawl(YoulaSpider)


    crawl_proc.start()
