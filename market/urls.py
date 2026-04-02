from django.urls import path
from . import views

urlpatterns = [
    path('', views.MarketPriceListView.as_view(), name='market_prices'),
    path('add/', views.MarketPriceCreateView.as_view(), name='market_price_add'),
    path('<int:pk>/edit/', views.MarketPriceUpdateView.as_view(), name='market_price_edit'),
    path('<int:pk>/delete/', views.MarketPriceDeleteView.as_view(), name='market_price_delete'),
]
