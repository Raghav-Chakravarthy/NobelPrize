## Nobel Prize Scraper
import scrapy
from scrapy.item import Item
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, Join
from collections import defaultdict
from operator import itemgetter
import re
import sys

class NobelPrizeItems(Item):
    fields = defaultdict(scrapy.Field)

    def __setitem__(self, key, value):
        self._values[key] = value

# class NobelPrizeNominees(Item):
#     fields = defaultdict(scrapy.Field)

#     def __setitem__(self, key, value):
#         self._values[key] = value
 
class CustomItemLoader(ItemLoader):
    default_input_processor = MapCompose(lambda i: i.replace(':', ''), 
        lambda i: i.replace(',', ''),
        lambda i: i.replace(r'[0-9]+', ''))
    default_output_processor = Join()

class NobelDataScraper(scrapy.Spider):
    name = "nobel_data"
    # custom_settings = {
    # 'FEED_EXPORT_FIELDS' : fields_to_export
    #  }


    f = open("url_strings.txt",'r')
    start_urls = [url.strip() for url in f.readlines()]
    f.close()


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback = self.parse)

    def parse(self, response):
        item_line_cutoffs = []
        item_desc = []
        table = response.xpath('//*[@id="main"]/div/table')
        trs = len(response.xpath('//*[@id="main"]/div/table//tr').extract()) + 1
        for tr in range(5, trs):                                                                                  
            fieldname = table.xpath(f'//tr[{tr}]/td[1]//text()').extract()
            field = MapCompose(lambda i: i.replace(':',''), lambda i: re.sub(r'[0-9]+', '', i), str.strip)(fieldname)                                                                                                     
            field = Join()(field)
            isIdentifier = (field == "Nominee") or (field == "Nominator")
            isBlank = field == "" 

            if isIdentifier:
                item_desc.append(field)
                start = tr + 1
            elif isBlank:
                end = tr
                item_line_cutoffs.append((start, end))
        d = {}
        for start, end in item_line_cutoffs:
            if start not in d:
                d[start] = end
        item_line_cutoffs = list(d.items())

        self.logger.info('item_line_cutoffs', item_line_cutoffs)

        # def getItem(line_range, field):
        #     item = NobelPrizeItems()
        #     l = CustomItemLoader(item=item, response=response)
        #     l.add_value(role, field)


        #         nominee_item = NobelPrizeNominees()
        #         nominee_l = CustomItemLoader(item=nominee_item, response=response)

        #         nominee_l.add_value('url', response.url)
        #         nominee_l.add_value('category', table.xpath('//tr[1]/td//text()')[0].extract())
        #         nominee_l.add_value('year', table.xpath('//tr[2]/td[2]//text()')[0].extract())

        #         for i in range(line_range[0], line_range[1]):
        #             fieldname = table.xpath(f'//tr[{tr}]/td[1]//text()').extract()
        #             field = MapCompose(lambda i: i.replace(':',''), lambda i: re.sub(r'[0-9]+', '', i), str.strip)(fieldname)                                                                                                     
        #             field = Join()(field)
        #             value = table.xpath(f'//tr[{tr}]/td[2]//text()')[0].extract()
        #             nominee_l.add_value(key, value)
        #         yield nominee_l.load_item()
            
        #     else:
        #         nominator_item = NobelPrizeNominators()
        #         nominator_l = CustomItemLoader(item=nominator_item, response=response)
        #         nominator_l.add_value('url', response.url)
        #         nominator_l.add_value('category', table.xpath('//tr[1]/td//text()')[0].extract())
        #         nominator_l.add_value('year', table.xpath('//tr[2]/td[2]//text()')[0].extract())

        #         for i in range(line_range[0], line_range[1]):
        #             fieldname = table.xpath(f'//tr[{tr}]/td[1]//text()').extract()
        #             field = MapCompose(lambda i: i.replace(':',''), lambda i: re.sub(r'[0-9]+', '', i), str.strip)(fieldname)                                                                                                     
        #             field = Join()(field)
        #             value = table.xpath(f'//tr[{tr}]/td[2]//text()')[0].extract()
        #             nominator_l.add_value(field, value)
        #         yield nominator_l.load_item()

        item_loaders = []


        for _, val in enumerate(zip(item_line_cutoffs, item_desc)):
            item = NobelPrizeItems()
            l = CustomItemLoader(item=item, response=response)
            l.add_value('url', response.url)
            self.logger.info('url %s', response.url)
            l.add_value('category', table.xpath('//tr[1]/td//text()')[0].extract())
            l.add_value('year', table.xpath('//tr[2]/td[2]//text()')[0].extract())
            l.add_value('role', val[1])

            for tr in range(val[0][0], val[0][1]):
                fieldname = table.xpath(f'//tr[{tr}]/td[1]//text()').extract()
                field = MapCompose(lambda i: i.replace(':',''), lambda i: re.sub(r'[0-9]+', '', i), str.strip)(fieldname)                                                                                                     
                field = Join()(field)
                self.logger.info('tr %d', tr)
                if not field:
                    continue 
                if field.startswith("Awarded"):
                    l.add_value('prize_status', field)
                else:
                    value = table.xpath(f'//tr[{tr}]/td[2]//text()')[0].extract()
                    l.add_value(field, value)
            item_loaders.append(l)


        for item_loader in item_loaders:
            yield item_loader.load_item()


           




            # for i in range(line_range):
            #     fieldname = table.xpath(f'//tr[{tr}]/td[1]//text()').extract()
            #     field = MapCompose(lambda i: i.replace(':',''), lambda i: re.sub(r'[0-9]+', '', i), str.strip)(fieldname)                                                                                                     
            #     field = Join()(field)
            #     if field 



         # nominees = NobelPrizeNominees()
        # nominators = NobelPrizeNominators()
        # nominee_l = CustomItemLoader(item=nominees, response=response)
        # nominator_l = CustomItemLoader(item = nominators, response = response)
        
        # table = response.xpath('//*[@id="main"]/div/table')
        # trs = len(response.xpath('//*[@id="main"]/div/table//tr').extract()) + 1
        
        # nominee_l.add_value('url', response.url)
        # nominee_l.add_value('category', table.xpath('//tr[1]/td//text()')[0].extract())
        # nominee_l.add_value('year', table.xpath('//tr[2]/td[2]//text()')[0].extract())

        # nominator_l.add_value('url', response.url)
        # nominator_l.add_value('category', table.xpath('//tr[1]/td//text()')[0].extract())
        # nominator_l.add_value('year', table.xpath('//tr[2]/td[2]//text()')[0].extract())

        # def isIdentifier(line):
        #     if line[0].startswith("Nominee"):
        #         return True
        #     elif line[0].startswith("Nominator"):
        #         return True
        #     else:
        #         return False

        # def isWinner(line):
        #      if line[0].startswith("Awarded"):
        #          return True

        # def isField(line):
        #     if (len(line[0]) == 0) or (line[0].startswith("\xa0")) or (isWinner(line)):
        #         return False
        #     else:
        #         return True
        
        # def getIdentifier(line):
        #   return line[0].split(' ')

        # def getVal(tr):
        #     return table.xpath(f'//tr[{tr}]/td[2]//text()')[0].extract()

        # def isField(line):
        #     if (len(line[0]) == 0) or (line[0].startswith("\xa0")) or (isWinner(line)):
        #         return False
        #     else:
        #         return True

        # def getKey(identifier, field):
        #     return identifier, '_', field
                


            # else if isNominee:
            #     nominee.fields[fieldname] = Field()
            #     nominee_l.add_value(fieldname, table.xpath(f'//tr[{tr}]/td[2]//text()')[0].extract())
            # else if isNominator:
            #     nominator_l.fields[fieldname] = Field()
            #     nominator_l.add_value(fieldname, table.xpath(f'//tr[{tr}]/td[2]//text()')[0].extract())

                



    
            


        	# if isIdentifier(fieldname):
        	# 	identifier = fieldname
        	
        	# elif isField(line):
         #        key = getKey(identifier, )




