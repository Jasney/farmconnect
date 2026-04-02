from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import MarketPrice

class MarketPriceListView(ListView):
    model = MarketPrice
    template_name = 'market/market_prices.html'
    context_object_name = 'market_prices'
    paginate_by = 20

    def get_queryset(self):
        queryset = MarketPrice.objects.all().order_by('-updated_at')
        crop_name = self.request.GET.get('crop_name')
        location = self.request.GET.get('location')
        if crop_name:
            queryset = queryset.filter(crop_name__icontains=crop_name)
        if location:
            queryset = queryset.filter(location__icontains=location)
        return queryset

class MarketPriceCreateView(CreateView):
    model = MarketPrice
    fields = ['crop_name', 'price', 'unit', 'location']
    template_name = 'market/market_price_form.html'
    success_url = reverse_lazy('market_prices')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

class MarketPriceUpdateView(UpdateView):
    model = MarketPrice
    fields = ['crop_name', 'price', 'unit', 'location']
    template_name = 'market/market_price_form.html'
    success_url = reverse_lazy('market_prices')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

class MarketPriceDeleteView(DeleteView):
    model = MarketPrice
    template_name = 'market/market_price_confirm_delete.html'
    success_url = reverse_lazy('market_prices')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)
