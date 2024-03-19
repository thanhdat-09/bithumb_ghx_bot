# import cx_Oracle
from ast import literal_eval
from configparser import ConfigParser
from datetime import datetime, timezone, timedelta, date
from dateutil import parser
from dateutil.relativedelta import relativedelta
from fake_useragent import VERSION, UserAgent
from json import load, loads, dump, dumps
from hashlib import md5
from pathlib import Path
from pymongo import MongoClient, DESCENDING
from unicodedata import normalize
from urllib.parse import urlencode, quote_plus
from random import choice, randint
from re import sub, findall, search
from requests import get, post, Session
from scrapy import Spider, Request, FormRequest
from scrapy.exceptions import CloseSpider
from scrapy.http import JsonRequest
from scrapy.selector import Selector
from shutil import copy
from itertools import product
from calendar import monthrange

NOW = datetime.now()
UNIXTIME = str(datetime.timestamp(NOW)*1000).split('.')[0]
CRAWL_DATE = NOW.strftime('%Y-%m-%d')
LOG_TIME = NOW.strftime('%d%m%Y')
CURRENT_PATH = Path(__file__).resolve().parent


def load_info(user="OBJECTROCKET", account_path="Mongo_path") -> dict:
    config = ConfigParser()
    config.read(account_path)
    try:
        return config[user]
    except:
        print("User not found!")
        exit(0)


def random_user_agent():
    ua_loc = f'{CURRENT_PATH}/fake_useragent{VERSION}.json' 
    ua = UserAgent(use_external_data=True, cache_path=ua_loc)
    return ua.random

def rand_timeout(min: int = 7, max: int = 9) -> int:
    return 100*randint(min, max)

def get_time(days: str = None, isfuzzy: bool = False, have_hour: bool=False) -> str:
    hour = ' %H:%M' if have_hour else ''
    return parser.parse(days, fuzzy=isfuzzy).strftime(f'%Y-%m-%d{hour}') if days else ""

def get_unixtime(timestamp: str = None, divide: int = 1000, have_hour: bool=False) -> str:
    hour = ' %H:%M' if have_hour else ''
    return datetime.fromtimestamp(int(timestamp)/divide).strftime(f'%Y-%m-%d{hour}') if timestamp else ""

def get_tztime(delta: int = 0):
    tz_time = datetime.now(timezone.utc) + timedelta(delta)
    return tz_time.replace(tzinfo=None).isoformat(timespec="seconds") + 'Z'

def check_dirs(folder: str = None):
    if not Path(folder).exists():
        Path(folder).mkdir(parents=True, exist_ok=True)

def fill_quote(string: str = None, base: str = 'https://www.fxstreet.com/macroeconomics/central-banks/{}') -> str:
    return base.format(string) if string else ""

def get_num(string: str = None, filter_:str = r"([^0-9.])") -> str:
    return sub(filter_, "", str(string).strip()) if string else ""

def checknull(string: str = None) -> str:
    return string if string else ""

def clean_str(string: str = None) -> str:
    return string.replace('“', '').replace('”', '').strip() if string else ""

def clean_lst(lst: list = None, unwanted: str = 'Also read:') -> list:
    lst = [clean_str(normalize('NFKD', ''.join(item))) for item in lst if unwanted not in ''.join(item)]
    return list(filter(None, lst))

def flatten_lst_dct(lst: list = None):
    return {k: v for d in lst for k, v in d.items()}

def sort_dict(dct: dict = None) -> dict:
    return {k: v for k, v in sorted(dct.items(), key=lambda item: item[1], reverse=True)}

def clear_dict(dct: dict = None) -> dict:
    return {k: v for k, v in dct.items() if v}

def lst_to_dict(items: list = None) -> dict:
    return {item[0]: item[1] for item in items}

def flatten(l):
    return [item for sublist in l for item in sublist]

# def connect_db(jsonfile: str = None) -> object:
#     with open(jsonfile, 'r', encoding='utf-8') as file:
#         account = load(file)
#     for row in account:
#         try:
#             oracle_connect = cx_Oracle.connect(row['CONNECT'], encoding="UTF-8", nencoding="UTF-8")
#             if oracle_connect:
#                 print(f"{row['NAME']} SUCCESS")
#                 return oracle_connect
#         except:
#             print("CAN NOT", row['NAME'])
#             continue

def should_abort_request(request):
    IGNORES = (
        'google', 
        # 'education',
        'sbcharts', 
        'forexpros', 
        'ad-score', 
        'krxd',
        'doubleclick',
    )
    if any(item in request.url for item in IGNORES):
        return True
    if request.resource_type in ("image", "media", "other"):
        return True
    # if request.resource_type == "script":
    #     return True
    # if request.resource_type == "xhr":    # need
    #     return True
    # if request.resource_type == "stylesheet": # slow
    #     return True
    # if request.method.lower() == 'post':
    #     # logging.log(logging.INFO, f"Ignoring {request.method} {request.url} ")
    #     return True
    return False


# make a copy of the invoice to work with
def backup_file(src="invoice.pdf", dst="copied_invoice.pdf"):
    copy(src,dst)


def gen_productwo(tup_one, tup_two, start=1):
    return {i: item for i, item in enumerate(list(product(tup_one, tup_two)), start=start)}


def get_lday(time_: datetime = None):
    return monthrange(time_.year, time_.month)[1]