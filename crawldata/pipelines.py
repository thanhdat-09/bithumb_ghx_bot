from crawldata.functions import *


class CrawldataPipeline:
    collection = ""

    def __init__(self, mongodb_uri, mongodb_db):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        if not self.mongodb_uri: exit("You need to provide a Connection String.")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get('MONGODB_URI'),
            mongodb_db=crawler.settings.get('MONGODB_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # self.collection = spider.name
        # self.db[self.collection].insert_one(dict(item))
        # return item

        # Check if the document already exists in the database
        existing_document = self.db[spider.name].find_one({'token_name': item['token_name']})
        
        if existing_document:
            # If the document exists, update the 'last_update' and 'mid_price' fields
            self.db[spider.name].update_one(
                {'token_name': item['token_name']},
                {'$set': {'last_update': item['last_update'], 'mid_price': item['mid_price']}}
            )
            # print("Updated document:", item)
        else:
            # If the document doesn't exist, insert a new one
            self.db[spider.name].insert_one(dict(item))
            # print("Inserted document:", item)
            
        return item

