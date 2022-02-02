import scrapy
import sys

years = [ #year ranges for each award arranged by corresponding prize
    (1901,1967),
    (1901,1967),
    (1901,1954),
    (1901,1967),
    (1901,1968)
    ]
prizes = (1,6) #tuple indicating prize ids

#function builds list of links to iterate through based on year range and prize id number
def make_url_lists(prize, years):
    return [f'https://www.nobelprize.org/nomination/archive/list.php?prize={prize}&year=%d' %(i) for i in range(*years)]

#iterates through the prizes to make lists of corresponding links, then combines all of the lists into a tuple of lists
def call_url_lists(prizes):
    start_urls = []

    for prize in range(*prizes):
        for year_range in years:
            start_urls.append(make_url_lists(prize, year_range))
    return start_urls

start_urls = call_url_lists(prizes)
start_urls = [url for sublist in start_urls for url in sublist] #urwraps 2d list

class NobelCrawler(scrapy.Spider):
    name = "nobel"

    def __init__(self):
        self.start_urls = start_urls

    def start_requests(self):
        for url in start_urls:
            yield scrapy.Request(url=url, callback = self.parse)


    def parse(self, response):
        url_strings = []
        suffixes = response.xpath('//*[@id="main"]/div/table//tr[not(contains(@style, "height: 1px; padding: 0px; border: 0px;"))]/td[3]/a/@href').extract()
        for suffix in suffixes:
            url_string = 'https://www.nobelprize.org/nomination/archive/'+suffix
            with open('url_strings.txt', 'a') as f:
                print(url_string, file=f)
