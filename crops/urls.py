from django.urls import path
from . import views

urlpatterns = [
    # Crops listing and detail
    path('', views.CropListView.as_view(), name='crop_list'),
    path('crop/<int:pk>/', views.CropDetailView.as_view(), name='crop_detail'),
    path('add/', views.CropCreateView.as_view(), name='crop_create'),
    path('<int:pk>/edit/', views.CropUpdateView.as_view(), name='crop_update'),
    path('<int:pk>/delete/', views.CropDeleteView.as_view(), name='crop_delete'),
    
    # Listings
    path('my-listings/', views.my_listings, name='my_listings'),
    path('saved-listings/', views.saved_listings, name='saved_listings'),
    path('<int:pk>/toggle-save/', views.toggle_save, name='toggle_save'),
    
    # Purchase requests
    path('crop/<int:pk>/request/', views.send_purchase_request, name='send_purchase_request'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/<int:pk>/update/', views.update_purchase_request, name='update_purchase_request'),
    
    # Reviews and ratings
    path('review/<int:purchase_request_id>/', views.post_review, name='post_review'),
    path('farmer/<int:farmer_id>/reviews/', views.farmer_reviews, name='farmer_reviews'),
    path('review/<int:review_id>/flag/', views.flag_review, name='flag_review'),
    
    # Farmer rankings
    path('farmer-rankings/', views.FarmerRankingView.as_view(), name='farmer_rankings'),
]

