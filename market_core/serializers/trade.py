from rest_framework import serializers
from market_core.models import Trade

class TradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trade
        fields = '__all__'
