import scrapy
import json
import re

# Regex expression compile
fullTitleRe = re.compile('(.+): ?(.+)')

class OrbSpider(scrapy.Spider):
    name = 'orbspider'
    # Declare how much departments we want to scrape in a list
    start_urls = ['http://orb.essex.ac.uk/ce/', 'http://orb.essex.ac.uk/ma/', 'http://orb.essex.ac.uk/ec/', 'http://orb.essex.ac.uk/hu/', 'http://orb.essex.ac.uk/ps/']

    def parse(self, response):
        # Scraper intial for function for looping thrugh orb website and binding data to fields
        for module in response.css('div.download > ul > li'):
            examPapersUrl = module.css('a[href*=exampapers]::attr(href)').extract_first(default='')
            # Checking if there is exam papers
            if (examPapersUrl == ''):
                continue
            examPapersUrl = 'http://orb.essex.ac.uk' + examPapersUrl
            fullTitle = module.css('h4 ::text').extract_first()
            match = fullTitleRe.match(fullTitle)
            moduleId = match.group(1)
            title = match.group(2)
            outlineUrl = module.xpath("//*[contains(text(), 'module directory')]").css('::attr(href)').extract_first()
            item = {
                'id' : moduleId,
                'title': title,
                'outlineUrl': outlineUrl,
                'papersUrl': examPapersUrl
            }
            yield scrapy.Request(
                response.urljoin(examPapersUrl),
                meta={'item': item},
                dont_filter=True,
                callback=self.parse_details
            )
    # Web crawling function to crawl to each of exam papers page, and collect exam papers URL, exam name and year
    def parse_details(self, response):
        # meta used to get variables between two functions
        item = response.meta.get('item', {})
        item['exams'] = []
        for li in response.css('#divContent > ul > li'):
            item['exams'].append({
                'year': li.css('a ::text').extract_first(),
                'url': li.css('a ::attr(href)').extract_first()
            })
        yield item


