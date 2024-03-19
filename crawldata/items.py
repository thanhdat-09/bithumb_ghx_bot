from scrapy import Item, Field


class LastDataItem(Item):
    token_name = Field()
    last_update = Field()
    mid_price = Field()