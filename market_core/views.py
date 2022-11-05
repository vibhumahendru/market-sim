import requests
import json
from django.shortcuts import render
from rest_framework import viewsets
from market_core.serializers import TradeSerializer, PortfolioSerializer
from market_core.models import Trade, Portfolio
from market_core.constants.granularities import GLOBAL_QUOTE
from url_filter.integrations.drf import DjangoFilterBackend
from rich import print
from rest_framework import status
from rest_framework.response import Response
from django.core.mail import send_mail




def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


class TradeViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = TradeSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['sell_date', 'buy_date']

    def get_queryset(self):
        return Trade.objects.all()

class PortfolioViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        return Portfolio.objects.all()

class ComputationViewset(viewsets.ViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    def granularity_fetch(self, granularity, symbol, name):
        if granularity == GLOBAL_QUOTE:
            try:
                print(symbol, name)
                return requests.get(f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=7DT1PQO2OFD52JIA')
            except Exception as e:
                print(e)
                print("error fetching result for ", name)

    def portfolio_pnl(self, request, *args, **kwargs):

        trades = Trade.objects.filter(sell_date__isnull=True, portfolio__id=kwargs['portfolio'])
        result = {}

        init_total = 0
        market_total = 0

        init_dollar = 0
        market_dollar = 0

        for trade in trades:
            quote = self.granularity_fetch(GLOBAL_QUOTE, trade.symbol, trade.stock_name)

            if quote.status_code == 200:
                current_price = float(quote.json()['Global Quote']['05. price'])

                init_total += trade.buy_price
                market_total += current_price

                init_dollar += (trade.buy_price*trade.quantity)
                market_dollar += (current_price*trade.quantity)

        # result["portfolio_percent_change"] = get_change(market_total, init_total)
        result["portfolio_percent_change"] = round(get_change(market_dollar, init_dollar),2)
        result["dollar_amount_change"] = round((market_dollar - init_dollar),2)

        return Response(result, status=status.HTTP_200_OK)

    def crypto_pnl(self, request, *args, **kwargs):
        storeName = ''

        def getIphoneAvailability():

            url = "https://www.apple.com/shop/fulfillment-messages?pl=true&mts.0=regular&cppart=UNLOCKED/US&parts.0=MQ1D3LL/A&location=11211"

            payload={}
            headers = {
            'authority': 'www.apple.com',
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cookie': 's_ppvl=%5B%5BB%5D%5D; s_cc=true; s_ppv=acs%253A%253Aadf%253A%253Amac_os%253A%253Asierra%253A%253Athread-252389003%2520%2528en-us%2529%2C100%2C33%2C2734%2C1920%2C889%2C1920%2C1080%2C2%2CP; geo=IN; at_check=true; dssid2=b182564f-e7f2-4a00-9cae-260404e3fec1; dssf=1; as_tex=~1~|470420:2:1671177540:USA|Sr3HFFMjL8qjLbY+Vr5u9xLM5kCWylpcFtmdAQ5iu0g; as_uct=0; as_loc=eed21c5375c9764576b176fe51124752bf0afcb3cbc5b0c982f3699b62da387ff3aa1e904b24f8970aeff1ae34760875bffde919b9da1171ad27687e5b400910e4f90e4a88fba030a3d87551f54d43f112658ee23a9390ce9073b84ab4e83cfd; as_pcts=jJB+3pC336M_iHRTkxps09mYOfC-e6qCMzK_l1DgJWlon+qRtSULKflKdbFm93rRcPJfXNJ:xUz+O8tQEEYuenp27JAX:iESDAhXSfXJfhVJe_PTXu-P0oX4aE:KIrLShcc5iUGHNtVQchDDUkjLKfm:vWNvlyb99llvrOZW9uuKmcxaGc56GTlf_rY7Snp:4vF; pxro=2; dslang=US-EN; site=USA; as_sfa=Mnx1c3x1c3x8ZW5fVVN8Y29uc3VtZXJ8aW50ZXJuZXR8MHwwfDE; as_cn=~7Uz7j_T81vlthNk0z9pRd3jBRm2mJCRFjLhIgy-QaYI=; myacinfo=DAWTKNV323952cf8084a204fb20ab2508441a07d02d31d53760968d7612fd591df7ffc75cc2cfe7b037bc35be85d02aa8f9fbb8a795db2a89cad3777c35ba0d7d45acc491f24907ad63d0bd8228c1f29f2e46d088fcc2b1067c7e128a3967a761c29bfe449b5a5339a91f91cd9fc2cc7bf3b90056f636eb34d92f3b6ec26cf8cf0beed2e6b5c17ae09580233b6f8d7674ecfcde12dfc45d64003a241c735c5ef0c1a9448b885954845875f2d91f0f525170eddf9143b491895395c16d247ed21e371e4084b36f06011e8715f5ce869fa477dd5591e5f5a72ced7f55791c991c61c40bb2fc52f15613071cc366d457b472ae622a9db967a2d5e9577be393b5ab0ef6691bc63da3a8f3660cb8b3014a9fa5f3aa8eca47d41a99130b4ef48af567cfbabfc59b0d3295629a6a839c6524084bf527792adecab17ded5290721db36b1a25c1f334500b48c26f48cab75df0295ce412b5800625c6778c8be9cfbe2245fb1320acccc8b5857f8b20a8a67b426e4f8384ad085497016512150ba996d7d381b6dff5f1f5f3a8ab3908a84496f81b8735e68bb09f0b8e334f428fd4312799bb6e6d97f3908562b08579810e72f5a9d7a659a973c0897fa29789a15f3eb704d5c1a69a4c863d4582e2342a6f7d22c6174cc7f7e292b6a96046948a57f19d1cf10e6246c7217e5b8208b682692764999e30a68889c9ae786be482ccdeae0730ee6ade05c0a67585a47V3; as_disa=AAAjAAABjkNhDnAPt_K2rObPLxLKwsNRmQUo14Mcb0lgZADA6P4AAgEvNq_r7WDwtUM-FSN4swThnOZOPhL-HUl6DhpZNm7CtA==; as_rec=42ceaac5d1aeca9ecc7b8eb2f7ded20d12874a0949ffbbe13aa59d5654d4842587403e2f0bd64e6e8cd17bf593a8472dd06e239259b2f84890c4cf5c1f44750b3b68383a260e9f8bdb35c1b065158d85; sso-token=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsIng1dCI6Im9TVlY2Q1pnclJ5cl9aMXVZRklRQWlYaWFXTEw2ZHRReHNSY2toQXVyQ0EifQ.eyJpc3MiOiJhb3MiLCJpYXQiOjE2Njc1NDM0NDk1MDQsImF1ZCI6IndwYyIsImFkc2lkIjoiMDAxMDMyLTA1LWJmYWFjMTQ0LTkxYWYtNDA2Zi05Y2UxLTkyNjNlYjkyMDY4NiJ9.ZockZMjxYuh7KwByWuuUcVGtW2b4qL51L18F0jxQloUbOlhLJLk0exbBn0XCJOW6BY1jy6Cj_tR-wfH7RTp4_Q; as_ltn_us=AAQEAMAKAS6vwFHR6OjiCQKF7pzadWAcXWdpl5SvBoaGCfEEyPd6qxJ3-vVO54NxLUv4KChTrxa-ij7mpbtPBUaVKBcDV888WIQ; as_dc=ucp1; s_fid=1C4CF20192041FB8-34E591DE84CC46B7; s_vi=[CS]v1|31B27BFA61744A81-40000CD36320F5E9[CE]; as_atb=1.0|MjAyMi0xMS0wNCAwNDozMTozNA|3d81b94212691be7dc21edcfcaa5ee22c153b648; mbox=session#57fd3910b23a44dda32365a916f65ce6#1667563318|PC#57fd3910b23a44dda32365a916f65ce6.31_0#1667563294; rtsid=%7BUS%3D%7Bt%3Da%3Bi%3DR594%3B%7D%3B%7D; s_sq=applestoreww%3D%2526c.%2526a.%2526activitymap.%2526page%253DAOS%25253A%252520home%25252Fshop_iphone%25252Ffamily%25252Fiphone_14_pro%25252Fselect%2526link%253Diphone%252520availabilitycity%252520or%252520zip%252520resets%252520%252528inner%252520text%252529%252520%25257C%252520no%252520href%252520%25257C%252520body%2526region%253Dbody%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253DAOS%25253A%252520home%25252Fshop_iphone%25252Ffamily%25252Fiphone_14_pro%25252Fselect%2526pidt%253D1%2526oid%253DfunctionVc%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DDIV',
            'dnt': '1',
            'referer': 'https://www.apple.com/shop/buy-iphone/iphone-14-pro/6.1-inch-display-256gb-deep-purple-unlocked',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            # print(response.content)

            res = json.loads(response.text)

            isIphoneAvailable = "Currently unavailable"


            for store in res["body"]["content"]["pickupMessage"]["stores"]:
                
                if store["partsAvailability"]["MQ1D3LL/A"]["pickupSearchQuote"] != "Currently unavailable":
                    print("Iphone also availalble at !!!!!!!!!!!!!!!!!!!!!!!!!!!!", store["storeName"])

                if isIphoneAvailable == "Currently unavailable":
                    if store["storeEmail"] == "williamsburg@apple.com":
                        isIphoneAvailable = store["partsAvailability"]["MQ1D3LL/A"]["pickupSearchQuote"]
                        storeName = store["storeName"]

                    if store["storeEmail"] == "soho@apple.com":
                        isIphoneAvailable = store["partsAvailability"]["MQ1D3LL/A"]["pickupSearchQuote"]
                        storeName = store["storeName"]

                    if store["storeEmail"] == "grandcentral@apple.com":
                        isIphoneAvailable = store["partsAvailability"]["MQ1D3LL/A"]["pickupSearchQuote"]
                        storeName = store["storeName"]

                    if store["storeEmail"] == "fifthavenue@apple.com":
                        isIphoneAvailable = store["partsAvailability"]["MQ1D3LL/A"]["pickupSearchQuote"]
                        storeName = store["storeName"]

            if isIphoneAvailable != "Currently unavailable":
                print("IPHONE AVAILABLE NOW")
                return True
            else:
                print("not available")
                return False


        # open_positions = [
        #     {
        #     'quantity_btc':0.00349,
        #     'inr_invested':9772,
        #     'crypto_type': "BTC"
        #     },
        #     {
        #     'quantity_btc':0.00323,
        #     'inr_invested':9849,
        #     'crypto_type': "BTC"
        #     },
        #     {
        #     'quantity_btc':0.00101,
        #     'inr_invested':2925,
        #     'crypto_type': "BTC"
        #     },
        # ]

        # def get_total_and_quantity(positions):
        #     total = 0
        #     quantity = 0

        #     for p in positions:
        #         total += p['inr_invested']
        #         quantity += p['quantity_btc']
        #     return total, quantity

        # def get_latest_btc_sell_price():
        #     response = requests.get('https://api.wazirx.com/api/v2/tickers')
        #     data = json.loads(response.content)
        #     return float(data['btcinr']['buy'])

        # total_inr_invested, total_btc_quantity_held = get_total_and_quantity(open_positions)

        # total_btc_value_in_inr = total_btc_quantity_held * get_latest_btc_sell_price()

        # percent_change = ((total_btc_value_in_inr - total_inr_invested)/total_inr_invested)*100
        # pnl = total_btc_value_in_inr - total_inr_invested

        result={}

        # result['percent_change'] = round(percent_change, 2)
        # result['pnl'] = round(pnl,2)

        if getIphoneAvailability():
            send_mail(
            f"VIBHU IPHONE AVAILABLE ",
            f"Store Name = {storeName} -> Click here - https://www.apple.com/shop/buy-iphone/iphone-14-pro/6.1-inch-display-256gb-deep-purple-unlocked ",
            "IPHONE AVAILABLE <info@wehelpgive.org>",
            ["vibhumahendru@gmail.com", "pragyamahendru@gmail.com"],
            fail_silently=False,
            )


        # send_mail(
        # f"Percent change: {round(percent_change, 2)}",
        # f"Dollar change: {round(pnl,2)}",
        # "Crypto Update <info@wehelpgive.org>",
        # ["vibhumahendru@gmail.com"],
        # fail_silently=False,
        # )

        return Response(result, status=status.HTTP_200_OK)


        print("_____________________________________________")
        print("percent_change: ", round(percent_change, 2))
        print("pnl: ", round(pnl,2))
        print("_____________________________________________")

        
