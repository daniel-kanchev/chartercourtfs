import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from chartercourtfs.items import Article


class CharterSpider(scrapy.Spider):
    name = 'charter'
    start_urls = ['https://www.chartercourtfs.co.uk/News/PressReleases']

    def parse(self, response):
        links = response.xpath('//ul[@class="tab-list"]//a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('(//nav[@class="pagination"]//a/@href)[last()]').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//h3/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%d %B %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//section[@class="main-content rte"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
