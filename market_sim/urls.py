from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from market_core.views import TradeViewSet, ComputationViewset
from rest_framework.routers import DefaultRouter

trade_router = DefaultRouter()
trade_router.register(r'', TradeViewSet, basename='trade')

portfolio_pnl = ComputationViewset.as_view({'get': 'portfolio_pnl'})

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^trade/', include(trade_router.urls)),
    url(r'^portfolio_pnl/', portfolio_pnl, name='portfolio_pnl' ),
]
