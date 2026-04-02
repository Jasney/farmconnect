from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import Crop, SavedListing, PurchaseRequest, Review, CropCategory
from .forms import CropForm, PurchaseRequestForm, ReviewForm
from messaging.models import Notification
from admin_panel.models import AdminActionLog
from accounts.models import FarmerProfile

class CropListView(ListView):
    model = Crop
    template_name = 'crops/list.html'
    context_object_name = 'crops'
    paginate_by = 12

    def get_queryset(self):
        queryset = Crop.objects.filter(
            is_active=True, 
            farmer__farmer_verification_status='verified'
        ).select_related('farmer', 'category')
        query = self.request.GET.get('q')
        crop_type = self.request.GET.get('type')
        category = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        is_organic = self.request.GET.get('organic')
        sort_by = self.request.GET.get('sort', '-created_at')
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query) | Q(origin__icontains=query)
            )
        if crop_type:
            queryset = queryset.filter(type=crop_type)
        if category:
            queryset = queryset.filter(category__slug=category)
        if min_price:
            queryset = queryset.filter(price_per_unit__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_unit__lte=max_price)
        if is_organic:
            queryset = queryset.filter(is_organic=True)
        
        # Sorting options
        if sort_by == 'price_low':
            queryset = queryset.order_by('price_per_unit')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price_per_unit')
        elif sort_by == 'best_rated':
            # Annotate with average rating
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        
        return queryset.order_by(sort_by) if sort_by not in ['price_low', 'price_high', 'best_rated'] else queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['crop_types'] = Crop.CROP_TYPES
        context['categories'] = CropCategory.objects.all()
        
        if self.request.user.is_authenticated:
            context['saved_crops'] = SavedListing.objects.filter(user=self.request.user).values_list('crop', flat=True)
        else:
            context['saved_crops'] = []
        
        return context

class CropDetailView(DetailView):
    model = Crop
    template_name = 'crops/detail.html'
    context_object_name = 'crop'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        crop = self.get_object()
        
        # Reviews and ratings
        context['reviews'] = crop.reviews.filter(is_approved=True).order_by('-created_at')
        context['average_rating'] = crop.get_average_rating()
        context['review_count'] = crop.get_review_count()
        
        # Farmer info
        context['farmer_reviews'] = Review.objects.filter(farmer=crop.farmer, is_approved=True).count()
        context['farmer_rating'] = crop.farmer.get_rating()
        context['farmer_trust_score'] = getattr(crop.farmer.farmer_profile, 'trust_score', 0)
        context['farmer_risk_level'] = getattr(crop.farmer.farmer_profile, 'risk_level', 'moderate')
        
        # Farmer's other products
        context['farmer_products'] = Crop.objects.filter(farmer=crop.farmer, is_active=True).exclude(id=crop.id)[:5]
        
        # Check if user saved this crop
        if self.request.user.is_authenticated:
            context['is_saved'] = SavedListing.objects.filter(user=self.request.user, crop=crop).exists()
        
        return context

class CropCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Crop
    form_class = CropForm
    template_name = 'crops/form.html'
    success_url = reverse_lazy('my_listings')

    def test_func(self):
        return (
            self.request.user.role == 'farmer' and 
            self.request.user.farmer_verification_status == 'verified' and
            self.request.user.account_status == 'active'
        )

    def handle_no_permission(self):
        messages.error(self.request, 'Only verified farmers can post new crops. Complete verification to access this feature.')
        return redirect('accounts:dashboard')

    def form_valid(self, form):
        form.instance.farmer = self.request.user
        return super().form_valid(form)

class CropUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Crop
    form_class = CropForm
    template_name = 'crops/form.html'

    def test_func(self):
        return (
            self.request.user.role == 'farmer' and
            self.request.user == self.get_object().farmer and
            self.request.user.farmer_verification_status == 'verified'
        )

    def handle_no_permission(self):
        messages.error(self.request, 'Only verified farmers can edit crop listings.')
        return redirect('accounts:dashboard')

    def get_success_url(self):
        return reverse_lazy('crop_detail', kwargs={'pk': self.object.pk})

class CropDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Crop
    success_url = reverse_lazy('my_listings')

    def test_func(self):
        return (
            self.request.user.role == 'farmer' and
            self.request.user == self.get_object().farmer and
            self.request.user.farmer_verification_status == 'verified'
        )

    def handle_no_permission(self):
        messages.error(self.request, 'Only verified farmers can delete crop listings.')
        return redirect('accounts:dashboard')

@login_required
def my_listings(request):
    crops = Crop.objects.filter(farmer=request.user).order_by('-created_at')
    context = {
        'crops': crops,
        'total_products': crops.count(),
        'active_products': crops.filter(is_active=True).count(),
    }
    return render(request, 'crops/my_listings.html', context)

@login_required
def saved_listings(request):
    saved_entries = SavedListing.objects.filter(user=request.user).select_related('crop')
    return render(request, 'crops/saved_listings.html', {'saved_entries': saved_entries})

@login_required
def toggle_save(request, pk):
    crop = get_object_or_404(Crop, pk=pk)
    saved, created = SavedListing.objects.get_or_create(user=request.user, crop=crop)
    if not created:
        saved.delete()
    return redirect('crop_detail', pk=pk)


@login_required
def send_purchase_request(request, pk):
    if request.user.role != 'buyer':
        messages.error(request, 'Only buyers may send purchase requests.')
        return redirect('crop_detail', pk=pk)

    crop = get_object_or_404(Crop, pk=pk, is_active=True)

    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid():
            quantity_requested = form.cleaned_data['quantity_requested']
            if quantity_requested > crop.quantity_available:
                form.add_error('quantity_requested', 'Requested quantity exceeds available stock.')
            else:
                purchase_request = form.save(commit=False)
                purchase_request.buyer = request.user
                purchase_request.crop = crop
                purchase_request.agreed_price = crop.price_per_unit
                purchase_request.save()

                # Notification for farmer
                Notification.objects.create(
                    user=crop.farmer,
                    notification_type='purchase',
                    title='New Purchase Request',
                    message=f'{request.user.username} requested {quantity_requested} {crop.unit} of {crop.name}',
                    related_object_id=purchase_request.id,
                    related_object_type='PurchaseRequest'
                )

                messages.success(request, 'Purchase request sent successfully!')
                return redirect('request_list')
    else:
        form = PurchaseRequestForm()

    return render(request, 'crops/request_form.html', {'form': form, 'crop': crop})


@login_required
def request_list(request):
    if request.user.role == 'buyer':
        purchase_requests = PurchaseRequest.objects.filter(buyer=request.user).select_related('crop').order_by('-created_at')
    elif request.user.role == 'farmer':
        purchase_requests = PurchaseRequest.objects.filter(crop__farmer=request.user).select_related('crop', 'buyer').order_by('-created_at')
    else:
        purchase_requests = PurchaseRequest.objects.none()

    return render(request, 'crops/request_list.html', {'purchase_requests': purchase_requests})


@login_required
def update_purchase_request(request, pk):
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk, crop__farmer=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['accepted', 'declined', 'completed', 'cancelled']:
            purchase_request.status = action
            if action == 'completed':
                purchase_request.completed_at = timezone.now()
            purchase_request.save()

            # Notification to buyer
            Notification.objects.create(
                user=purchase_request.buyer,
                notification_type='purchase',
                title=f'Purchase Request {action.title()}',
                message=f'Your purchase request for {purchase_request.crop.name} has been {action}',
                related_object_id=purchase_request.id,
                related_object_type='PurchaseRequest'
            )

            messages.success(request, f'Purchase request {action}.')
            return redirect('request_list')

    return render(request, 'crops/update_request.html', {'purchase_request': purchase_request})


@login_required
def post_review(request, purchase_request_id):
    """Post a review for a completed purchase"""
    purchase_request = get_object_or_404(PurchaseRequest, id=purchase_request_id, buyer=request.user)
    
    # Only allow reviews for completed purchases
    if purchase_request.status != 'completed':
        messages.error(request, 'You can only review completed purchases.')
        return redirect('request_list')
    
    # Check if review already exists
    existing_review = Review.objects.filter(
        buyer=request.user,
        farmer=purchase_request.crop.farmer,
        crop=purchase_request.crop
    ).exists()
    
    if existing_review:
        messages.error(request, 'You have already reviewed this product.')
        return redirect('request_list')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.buyer = request.user
            review.farmer = purchase_request.crop.farmer
            review.crop = purchase_request.crop
            review.purchase_request = purchase_request
            review.verified_purchase = True
            review.save()
            
            # Update farmer rating
            update_farmer_rating(purchase_request.crop.farmer)
            
            # Notification to farmer
            Notification.objects.create(
                user=purchase_request.crop.farmer,
                notification_type='review',
                title='New Review',
                message=f'{request.user.username} reviewed your product: {review.title}',
                related_object_id=review.id,
                related_object_type='Review'
            )
            
            messages.success(request, 'Review posted successfully!')
            return redirect('request_list')
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'purchase_request': purchase_request,
        'crop': purchase_request.crop,
    }
    
    return render(request, 'crops/post_review.html', context)


@login_required
def farmer_reviews(request, farmer_id):
    """View all reviews for a farmer"""
    from accounts.models import CustomUser
    farmer = get_object_or_404(CustomUser, id=farmer_id, role='farmer')
    
    reviews = Review.objects.filter(farmer=farmer, is_approved=True).order_by('-created_at')
    avg_rating = farmer.get_rating()
    
    context = {
        'farmer': farmer,
        'reviews': reviews,
        'average_rating': avg_rating,
        'total_reviews': reviews.count(),
    }
    
    return render(request, 'crops/farmer_reviews.html', context)


def update_farmer_rating(farmer):
    """Update farmer's average rating from reviews"""
    from accounts.models import FarmerProfile
    
    reviews = Review.objects.filter(farmer=farmer, is_approved=True)
    if reviews.exists():
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        
        profile, created = FarmerProfile.objects.get_or_create(user=farmer)
        profile.rating_score = avg_rating
        profile.total_reviews = reviews.count()
        profile.save()
        
        # Update trust score (simplified)
        farmer.last_activity = timezone.now()
        farmer.save()


@login_required
def flag_review(request, review_id):
    """Flag a review for inappropriate content"""
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Inappropriate content')
        review.is_flagged = True
        review.flag_reason = reason
        review.save()
        
        messages.success(request, 'Review flagged for admin review.')
        return redirect(request.META.get('HTTP_REFERER', 'crop_detail'))
    
    return render(request, 'crops/flag_review.html', {'review': review})


class FarmerRankingView(ListView):
    """Display ranked list of farmers based on ratings and performance"""
    model = FarmerProfile
    template_name = 'crops/farmer_rankings.html'
    context_object_name = 'farmers'
    paginate_by = 20
    
    def get_queryset(self):
        return FarmerProfile.objects.filter(
            user__role='farmer',
            user__account_status='active'
        ).order_by('-rating_score', '-successful_transactions', '-total_reviews')

