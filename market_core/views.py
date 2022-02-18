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


        open_positions = [
            {
            'quantity_btc':0.00349,
            'inr_invested':9772,
            'crypto_type': "BTC"
            },
            {
            'quantity_btc':0.00323,
            'inr_invested':9849,
            'crypto_type': "BTC"
            },
            {
            'quantity_btc':0.00101,
            'inr_invested':2925,
            'crypto_type': "BTC"
            },
        ]

        def get_total_and_quantity(positions):
            total = 0
            quantity = 0

            for p in positions:
                total += p['inr_invested']
                quantity += p['quantity_btc']
            return total, quantity

        def get_latest_btc_sell_price():
            response = requests.get('https://api.wazirx.com/api/v2/tickers')
            data = json.loads(response.content)
            return float(data['btcinr']['buy'])

        total_inr_invested, total_btc_quantity_held = get_total_and_quantity(open_positions)

        total_btc_value_in_inr = total_btc_quantity_held * get_latest_btc_sell_price()

        percent_change = ((total_btc_value_in_inr - total_inr_invested)/total_inr_invested)*100
        pnl = total_btc_value_in_inr - total_inr_invested

        result={}

        result['percent_change'] = round(percent_change, 2)
        result['pnl'] = round(pnl,2)



        send_mail(
        f"Percent change: {round(percent_change, 2)}",
        f"Dollar change: {round(pnl,2)}",
        "Crypto Update <info@wehelpgive.org>",
        ["vibhumahendru@gmail.com"],
        fail_silently=False,
        )

        return Response(result, status=status.HTTP_200_OK)


        print("_____________________________________________")
        print("percent_change: ", round(percent_change, 2))
        print("pnl: ", round(pnl,2))
        print("_____________________________________________")

        
