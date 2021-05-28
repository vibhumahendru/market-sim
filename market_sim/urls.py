from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from market_core.views import TradeViewSet, ComputationViewset, PortfolioViewSet
from rest_framework.routers import DefaultRouter

trade_router = DefaultRouter()
trade_router.register(r'', TradeViewSet, basename='trade')

portfolio_router = DefaultRouter()
portfolio_router.register(r'', PortfolioViewSet, basename='portfolio')

portfolio_pnl = ComputationViewset.as_view({'get': 'portfolio_pnl'})

crypto_pnl = ComputationViewset.as_view({'get': 'crypto_pnl'})

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^trade/', include(trade_router.urls)),
    url(r'^portfolio/', include(portfolio_router.urls)),
    path('portfolio_pnl/<int:portfolio>/', portfolio_pnl, name='portfolio_pnl' ),
    path('crypto_pnl', crypto_pnl, name='crypto_pnl' ),
]
