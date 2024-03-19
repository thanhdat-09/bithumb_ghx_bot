from crawldata.functions import *
from crawldata.items import LastDataItem

class CrawlerSpider(Spider):
    name = 'orderbook'
    custom_settings = {'LOG_FILE': f"{SITE}/log/{name}_{LOG_TIME}.log"}

    def start_requests(self):
        params = {'retry': '0'}
        for token in tokens:
            yield Request(f'https://gw.bithumb.com/observer/orderbook/v1/orderbook/{token}_KRW/1?'+urlencode(params),headers=headers, meta={'params': (params, token)})

    def parse(self, response):
        params, token = response.meta.get('params')
        if response.text:
            data = loads(response.text).get('data')
            if data:
                timestamp = data.get('timestamp')
                params['_'] = timestamp
                yield Request('https://gw.bithumb.com/exchange/v1/comn/exrate?' + urlencode(params), headers=headers, meta={'data': (data.get('bid'), data.get('ask'), timestamp, token)}, callback=self.parse_exchange_rate)
            else:
                self.logger.error("No data returned from the orderbook API")

    def parse_exchange_rate(self, response):
        bids, asks, timestamp, token = response.meta.get('data')
        if response.text:
            exchange_rate_data = loads(response.text).get('data')
            if exchange_rate_data:
                currency_rate_list = exchange_rate_data.get('currencyRateList')
                for currency_data in currency_rate_list:
                    if currency_data.get('currency') == 'USD':
                        exchange_rate_usd = float(currency_data.get('rate'))
                yield Request(f'https://api.bithumb.com/public/ticker/{token}_KRW', meta={'data': (bids, asks, timestamp, exchange_rate_usd, token)}, callback=self.parse_token_info)

            else:
                self.logger.error("No exchange rate data returned from the exchange rate API")

    def parse_token_info(self, response):
        bids, asks, timestamp, exchange_rate_usd, token = response.meta.get('data')
        truncated_timestamp = int(str(timestamp)[:10])
        analysis_results = analyze_orderbook(bids, asks)

        if response.text:
            token_data = loads(response.text).get('data')
            if token_data:
                volume = float(token_data.get('units_traded_24H')) * float(token_data.get('closing_price'))
                price_change = float(token_data.get('fluctate_rate_24H'))
                bigger_side = "bid" if analysis_results['total_tokens_decrease'] > analysis_results['total_tokens_increase'] else "ask"
                current_price = analysis_results['mid']
                status, latest_orderbook = get_latest_orderbook("bithumb", "orderbook", token)

                if status:
                    last_price = latest_orderbook.get('mid_price')
                    last_update = latest_orderbook.get('last_update')
                    price_change_percentage = abs(current_price - last_price) / last_price
                    # print(f"{convert_timestamp_to_datetime(timestamp)} UTC+7 (Vietnam):", price_change_percentage)
                    time_difference_seconds = truncated_timestamp - last_update

                    # Determine the reason for sending the message
                    message_reason = None
                    if price_change_percentage >= 0.01:
                        message_reason = "Price Movement"
                    elif time_difference_seconds >= 3600:
                        message_reason = "Hourly updates"
                    
                    # If there's a valid reason, send the message and yield LastDataItem
                    if message_reason:
                        message = create_message(token, timestamp, analysis_results, exchange_rate_usd, volume, price_change, bigger_side, reason=message_reason)
                        send_telegram_message(TELEGRAM_CHAT_ID, TELEGRAM_TOKEN, message)
                        yield LastDataItem({'token_name': token, 'last_update': truncated_timestamp, 'mid_price': current_price})

                    
                # Run for the first time when there is nothing in the database
                # yield LastDataItem({'token_name': token, 'last_update': truncated_timestamp, 'mid_price': current_price})
            else:
                self.logger.error("No token data returned from the API")
        
