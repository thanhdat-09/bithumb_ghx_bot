from crawldata.functions import CURRENT_PATH, random_user_agent
# USER_AGENT = random_user_agent()

BOT_NAME = 'crawldata'
SPIDER_MODULES = ('crawldata.spiders',)
NEWSPIDER_MODULE = 'crawldata.spiders'

URLLENGTH_LIMIT = 50000
ROBOTSTXT_OBEY = False
HTTPERROR_ALLOW_ALL = True

CONCURRENT_REQUESTS = 32
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
TELNETCONSOLE_ENABLED = False

# pip install scrapy-rotating-proxies
# ROTATING_PROXY_LIST_PATH = '/mnt/HUNGMOUNT/home49/proxies.txt'
# ROTATING_PROXY_LIST_PATH = '/home/proxies.txt'
# ROTATING_PROXY_LIST_PATH = '/home/thanhdat/proxies.txt'

ROTATING_PROXY_LIST_PATH = f"{CURRENT_PATH}/proxies.txt"
ROTATING_PROXY_PAGE_RETRY_TIMES=200
CONCURRENT_REQUESTS_PER_IP = 5
DOWNLOADER_MIDDLEWARES = {'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,'rotating_proxies.middlewares.BanDetectionMiddleware': 620,}
ITEM_PIPELINES = {'crawldata.pipelines.CrawldataPipeline': 300,}

LOG_ENABLED = True
LOG_LEVEL = 'ERROR'
LOG_FORMAT = '%(levelname)s: %(message)s'

REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
FEED_EXPORT_ENCODING = 'utf-8'
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'
MONGODB_URI = "mongodb+srv://thanhdat021293:Datbaby123@cluster0.firhris.mongodb.net/"
# MONGODB_URI = "mongodb://127.0.0.1:27017"
MONGODB_DATABASE = "bithumb"