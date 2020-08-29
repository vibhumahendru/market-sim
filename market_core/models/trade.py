from django.db import models

class Trade(models.Model):
    stock_name = models.CharField(max_length=300, null=False)
    symbol = models.CharField(max_length=300, null=False)
    buy_price = models.FloatField(null=True)
    sell_price = models.FloatField(null=True)
    buy_date = models.DateTimeField(default=None, null=True)
    sell_date = models.DateTimeField(default=None, null=True)
    quantity = models.IntegerField(default=0, null=False)
