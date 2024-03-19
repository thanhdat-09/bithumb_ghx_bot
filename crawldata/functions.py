from pathlib import Path
from sys import path
from time import mktime

SITE = Path(__file__).resolve().parent.parent
PROJECT = SITE.parent
GRAND_PROJECT = PROJECT.parent
path.append(str(PROJECT.absolute()))
from helpers import *

USING_LOCALHOST = True
TELEGRAM_TOKEN = '7196607848:AAE3sfsuunQ9oehxP3R7543OMzdf1vifykA'
# TELEGRAM_CHAT_ID = '-1002109682038'
TELEGRAM_CHAT_ID = '-4122308269'
tokens = ('GHX',)
headers = {
    'User-Agent': random_user_agent(),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    }


check_dirs(f"{SITE}/log/")


def get_current_unixtime(current_datetime):
    return int(mktime(current_datetime.timetuple()))

def analyze_orderbook(bids, asks, price_change=0.1):
    best_ask = float(min(asks, key=lambda x: float(x['p']))['p'])
    best_bid = float(max(bids, key=lambda x: float(x['p']))['p'])

    mid = (best_ask + best_bid) / 2

    # Calculate target_increase and target_decrease based on best bid and best ask
    target_increase = best_ask * (1 + price_change)
    target_decrease = best_bid * (1 - price_change)

    total_increase = sum(float(ask['p']) * float(ask['q']) for ask in asks if float(ask['p']) <= target_increase)
    total_decrease = sum(float(bid['p']) * float(bid['q']) for bid in bids if float(bid['p']) > target_decrease)

    total_tokens_increase = sum(float(ask['q']) for ask in asks if float(ask['p']) <= target_increase)
    total_tokens_decrease = sum(float(bid['q']) for bid in bids if float(bid['p']) > target_decrease)

    spread_percentage = ((best_ask - best_bid) / best_ask) * 100

    percentage_difference = (max(total_tokens_increase, total_tokens_decrease) / min(total_tokens_increase, total_tokens_decrease)) * 100

    bid_ask_price_sum = total_increase + total_decrease
    bid_ask_quantity_sum = total_tokens_increase + total_tokens_decrease

    percentage_change = price_change * 100

    return {
        'best_bid': best_bid,
        'best_ask': best_ask,
        'mid': mid,
        'spread_percentage': spread_percentage,
        'percentage_difference': percentage_difference,
        'total_increase': total_increase,
        'total_decrease': total_decrease,
        'total_tokens_increase': total_tokens_increase,
        'total_tokens_decrease': total_tokens_decrease,
        'bid_ask_price_sum': bid_ask_price_sum,
        'bid_ask_quantity_sum': bid_ask_quantity_sum,
        'percentage_change': percentage_change
    }

def convert_timestamp_to_datetime(timestamp):
    truncated_timestamp = int(str(timestamp)[:10])

    # Convert the truncated timestamp to datetime format
    datetime_obj = datetime.fromtimestamp(truncated_timestamp)

    # Format the datetime as a specific format
    datetime_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

    return datetime_str

def get_latest_orderbook(database_name, collection_name, token, mongo_uri="mongodb+srv://thanhdat021293:Datbaby123@cluster0.firhris.mongodb.net"):
# def get_latest_orderbook(database_name, collection_name, token, mongo_uri="mongodb://127.0.0.1:27017"):
    client = MongoClient(mongo_uri)
    try:
        db = client[database_name]
        collection = db[collection_name]
        latest_transaction = collection.find_one({"token_name": token})
        if latest_transaction:
            return True, latest_transaction
        else:
            return False, None
    finally:
        client.close()

# def get_latest_orderbook(database_name, collection_name, token, mongo_uri="mongodb://127.0.0.1:27017"):
#     client = MongoClient(mongo_uri)
#     try:
#         db = client[database_name]
#         collection = db[collection_name]
#         latest_transaction = collection.find_one({"name": token}, sort=[("last_update", DESCENDING)], projection={"_id": False})
#         if latest_transaction:
#             return True, latest_transaction
#         else:
#             return False, None
#     finally:
#         client.close()


# def insert_unique_document(collection, new_record, unique_fields):
#     query = {field: new_record[field] for field in unique_fields}
#     existing_document = collection.find_one(query)
#     if existing_document:
#         print("Document already exists:", existing_document.get('last_update'))
#     else:
#         collection.insert_one(new_record)
#         print("Inserted document:", new_record)

def create_message(token,timestamp, analysis_results, exchange_rate_usd, volume, price_change, bigger_side, reason):
    return (
        f"<b>Bithumb</b>\n"
        f"<b>{reason}</b>\n"
        f"{token}-USD Orderbook at <b>{convert_timestamp_to_datetime(timestamp)} UTC+7 (Vietnam)</b>\n"
        f"Capital required to move {token}-USD price by ±{analysis_results['percentage_change']:,.0f}%:\n"
        f"- Up => Ask ${analysis_results['total_increase'] / exchange_rate_usd:,.2f} worth {token} | {analysis_results['total_tokens_increase']:,.2f} {token}\n"
        f"- Down => Ask ${analysis_results['total_decrease'] / exchange_rate_usd:,.2f} worth {token} | {analysis_results['total_tokens_decrease']:,.2f} {token}\n"
        f"- Bid + Ask: ${analysis_results['bid_ask_price_sum'] / exchange_rate_usd:,.2f} | {analysis_results['bid_ask_quantity_sum']:,.2f} {token}\n"
        f"- Best Bid: {analysis_results['best_bid'] / exchange_rate_usd:,.4f} | Best Ask: {analysis_results['best_ask'] / exchange_rate_usd:,.4f} | Mid: {analysis_results['mid'] / exchange_rate_usd:,.4f}\n"
        f"- Spread: {analysis_results['spread_percentage']:,.4f}%\n"
        f"- The {bigger_side} side is bigger by {analysis_results['percentage_difference']:,.2f}%\n"
        f"- 24h-Chg: {price_change:,.2f}% | Vol-24h: ${volume / exchange_rate_usd:,.2f}\n"
    )

def send_telegram_message(chat_id, token, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        # "reply_to_message_id":903,
        "reply_to_message_id":311,
        "parse_mode": "HTML"  # Add this line
    }
    post(url, data=data)