from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg, Count, Q
from django.utils import timezone
from .forms import RegisterForm, LoginForm, ContactForm, FarmerVerificationForm
from .models import CustomUser
from crops.models import Crop, SavedListing, PurchaseRequest
from crops.insights import build_assistant_response, get_price_insight_cards
from market.models import MarketPrice
from messaging.models import Message
from admin_panel.models import UserReport, AdminActionLog, AccountAppeal


def register_view(request):
    """Registration page - farmers enter pending verification state"""
    from .models import FarmerProfile

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Ensure pending farmer verification for farmer role
            if user.role == 'farmer':
                user.farmer_verification_status = 'pending'
                user.account_status = 'active'
            user.save()

            if user.role == 'farmer':
                FarmerProfile.objects.get_or_create(user=user)

            login(request, user)
            messages.success(request, f'Welcome to Farm Connect, {user.username}!')
            return redirect('accounts:dashboard')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Login page"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            # support username or email login
            user_obj = None
            if '@' in identifier:
                user_obj = CustomUser.objects.filter(email__iexact=identifier).first()
            else:
                user_obj = CustomUser.objects.filter(username__iexact=identifier).first()

            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
            else:
                user = authenticate(request, username=identifier, password=password)

            if user:
                # account status checks
                if not user.is_active or user.account_status == 'suspended':
                    messages.error(request, 'Your account is inactive or suspended. Please contact support.')
                    return render(request, 'accounts/login.html', {'form': LoginForm()})

                if user.account_status == 'blocked' and user.role != 'farmer':
                    messages.error(request, 'Your account is blocked. Please contact admin for help.')
                    return render(request, 'accounts/login.html', {'form': LoginForm()})

                # Farmer verification state handling
                if user.role == 'farmer':
                    if user.farmer_verification_status in ['rejected']:
                        messages.error(request, 'Your farmer account has been rejected. Please contact admin.')
                        return render(request, 'accounts/login.html', {'form': LoginForm()})
                    elif user.farmer_verification_status in ['pending', 'under_review']:
                        messages.warning(request, 'Your farmer account is pending verification. You may browse, but posting and messaging are restricted.')
                    
                    if user.account_status == 'blocked':
                        messages.warning(request, 'Your farmer account is blocked. You may appeal once logged in.')

                # update last activity timestamp
                user.last_activity = timezone.now()
                user.save(update_fields=['last_activity'])

                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')

                if user.role == 'admin':
                    return redirect('admin_panel:dashboard')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Invalid username/email or password.')
                form = LoginForm()
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('landing')


@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return redirect('admin_panel:dashboard')

    context = {
        'user': request.user,
    }

    if request.user.role == 'farmer':
        # Ensure FarmerProfile exists
        from .models import FarmerProfile
        FarmerProfile.objects.get_or_create(user=request.user)
        my_listings = Crop.objects.filter(farmer=request.user).order_by('-created_at')

        is_blocked = request.user.account_status == 'blocked'

        dashboard_data = {
            'farmer_status': request.user.farmer_verification_status,
            'verification_form': None,
            'is_blocked': is_blocked,
            'assistant_prompts': [
                'Who are the best buyers for my latest crop?',
                'What price should I compare against today?',
                'Which crop listing needs a pricing review?',
            ],
        }

        if not is_blocked:
            dashboard_data.update({
                'my_listings': my_listings,
                'total_listings': my_listings.count(),
                'new_messages': Message.objects.filter(conversation__participants=request.user, is_read=False).exclude(sender=request.user).count(),
                'incoming_requests': PurchaseRequest.objects.filter(crop__farmer=request.user, status='pending'),
                'price_insight_cards': get_price_insight_cards(my_listings, limit=3),
            })
        else:
            dashboard_data.update({
                'my_listings': Crop.objects.none(),
                'total_listings': 0,
                'new_messages': 0,
                'incoming_requests': PurchaseRequest.objects.none(),
                'price_insight_cards': [],
            })

        context.update(dashboard_data)
    elif request.user.role == 'buyer':
        saved_listings = SavedListing.objects.filter(user=request.user).select_related('crop', 'crop__farmer')
        context.update({
            'saved_listings': saved_listings,
            'new_messages': Message.objects.filter(conversation__participants=request.user, is_read=False).exclude(sender=request.user).count(),
            'pending_requests': PurchaseRequest.objects.filter(buyer=request.user).order_by('-created_at'),
            'price_insight_cards': get_price_insight_cards([entry.crop for entry in saved_listings], limit=3),
            'assistant_prompts': [
                'What is the current price of maize?',
                'Which saved listing looks best today?',
                'Where is the best market for tomatoes?',
            ],
        })

    # Use shared user dashboard template for farmers/buyers
    return render(request, 'dashboard.html', context)


@login_required
def ai_assistant(request):
    question = ''
    assistant_result = build_assistant_response(request.user, '')

    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        assistant_result = build_assistant_response(request.user, question)

    context = {
        'question': question,
        'assistant_result': assistant_result,
        'starter_prompts': [
            'What is the price of maize?',
            'Who are the best buyers for my crop?',
            'Which market is paying the most for beans?',
        ],
    }
    return render(request, 'accounts/ai_assistant.html', context)


@login_required
def farmer_rankings(request):
    """Display top-performing farmers ranked by ratings and transactions"""
    farmers = CustomUser.objects.filter(
        role='farmer', 
        farmer_verification_status='verified'
    ).annotate(
        avg_rating=Avg('farmer_reviews__rating'),
        total_reviews=Count('farmer_reviews'),
        successful_transactions=Count(
            'crops__purchase_requests', 
            filter=Q(crops__purchase_requests__status='completed')
        )
    ).order_by('-avg_rating', '-successful_transactions', '-total_reviews')

    return render(request, 'accounts/farmer_rankings.html', {'farmers': farmers})


@login_required
def admin_dashboard(request):
    """Admin dashboard with platform statistics and management links"""
    context = {
        'user_count': CustomUser.objects.count(),
        'farmer_count': CustomUser.objects.filter(role='farmer').count(),
        'buyer_count': CustomUser.objects.filter(role='buyer').count(),
        'crop_count': Crop.objects.count(),
        'active_crops': Crop.objects.filter(is_active=True).count(),
        'price_count': MarketPrice.objects.count(),
        'active_messages': Message.objects.count(),
        'unread_messages': Message.objects.filter(is_read=False).count(),
        'recent_crops': Crop.objects.all().order_by('-created_at')[:5],
        'recent_users': CustomUser.objects.all().order_by('-date_joined')[:5],
    }
    return render(request, 'admin/dashboard.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']

            send_mail(
                f"Farm Connect Support: {subject}",
                f"From: {name} <{email}>\n\n{message_body}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(request, 'Your message has been received. Support will contact you soon.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'accounts/contact.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    is_farmer = user.role == 'farmer'

    # Farmer verification form handling now lives on profile page
    if request.method == 'POST' and is_farmer and user.account_status == 'blocked' and request.POST.get('form_type') == 'appeal':
        from .forms import AppealForm
        appeal_form = AppealForm(request.POST)
        if appeal_form.is_valid():
            AccountAppeal.objects.create(
                farmer=user,
                issue_summary=appeal_form.cleaned_data['issue_summary'],
                message=appeal_form.cleaned_data['message'],
                status='pending',
            )
            messages.success(request, 'Appeal submitted successfully. Admin will review your request soon.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please provide valid appeal information.')

    if request.method == 'POST' and is_farmer and user.farmer_verification_status != 'verified' and request.POST.get('form_type') == 'verification':
        verification_form = FarmerVerificationForm(request.POST, request.FILES, instance=user)
        if verification_form.is_valid():
            verification_form.save()
            user.farmer_verification_status = 'under_review'
            user.save(update_fields=['farmer_verification_status'])
            messages.success(request, 'Verification details submitted successfully. Your account is under review.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the highlighted verification fields.')
    elif request.method == 'POST':
        user.phone = request.POST.get('phone', user.phone)
        user.location = request.POST.get('location', user.location)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.bio = request.POST.get('bio', user.bio)
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')

    # Determine form instance for GET and keep for invalid POST
    verification_form = None
    appeal_form = None

    if is_farmer and user.farmer_verification_status != 'verified':
        # Keep form with posted data on validation errors or initial instance
        verification_form = FarmerVerificationForm(request.POST or None, request.FILES or None, instance=user)

    if is_farmer and user.account_status == 'blocked':
        from .forms import AppealForm
        appeal_form = AppealForm(request.POST or None)

    context = {
        'user': user,
        'farmer_status': user.farmer_verification_status if is_farmer else None,
        'verification_form': verification_form,
        'is_blocked': user.account_status == 'blocked',
        'appeal_form': appeal_form,
    }

    return render(request, 'accounts/profile.html', context)

@login_required
def report_farmer(request, farmer_id):
    farmer = get_object_or_404(CustomUser, id=farmer_id, role='farmer')

    if request.method == 'POST':
        report_type = request.POST.get('report_type', 'other')
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        if title and description:
            report = UserReport.objects.create(
                reported_user=farmer,
                reporter=request.user,
                report_type=report_type,
                title=title,
                description=description,
                status='pending',
                severity='medium',
            )

            # Update farmer report handling and auto-flag/block when needed
            farmer.report_count = (farmer.report_count or 0) + 1
            farmer.is_reported = True

            admin_action_type = 'other'
            if farmer.report_count >= 5 and farmer.account_status in ['active', 'flagged']:
                farmer.account_status = 'blocked'
                admin_action_type = 'user_blocked'
            elif farmer.report_count >= 3 and farmer.account_status == 'active':
                farmer.account_status = 'flagged'
                admin_action_type = 'user_flagged'

            farmer.save(update_fields=['report_count', 'is_reported', 'account_status'])

            # Auto-notify reporter and capture in audit log
            AdminActionLog.objects.create(
                admin=request.user if request.user.role == 'admin' else None,
                action_type=admin_action_type,
                target_user=farmer,
                description=f'{request.user.username} reported {farmer.username}: {report.title}',
                related_report=report
            )

            messages.success(request, 'Report submitted successfully. Admin will review it soon.')
            return redirect('accounts:dashboard')

        messages.error(request, 'Please provide title and description for the report.')

    return render(request, 'accounts/report_farmer.html', {'farmer': farmer})


@login_required
def report_farmer_list(request):
    # List of farmers to pick for reporting
    farmers = CustomUser.objects.filter(role='farmer', account_status='active').exclude(id=request.user.id)
    return render(request, 'accounts/report_farmer_list.html', {'farmers': farmers})


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def user_management(request):
    users = CustomUser.objects.all().order_by('role', 'username')
    return render(request, 'accounts/admin_user_management.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def listing_moderation(request):
    crops = Crop.objects.all().order_by('-created_at')
    if request.method == 'POST':
        crop_id = request.POST.get('crop_id')
        action = request.POST.get('action')
        crop = get_object_or_404(Crop, pk=crop_id)
        if action == 'deactivate':
            crop.is_active = False
            crop.save()
            messages.success(request, 'Listing deactivated.')
        elif action == 'activate':
            crop.is_active = True
            crop.save()
            messages.success(request, 'Listing activated.')
        elif action == 'remove':
            crop.delete()
            messages.success(request, 'Listing removed.')
        return redirect('listing_moderation')
    return render(request, 'accounts/admin_listing_moderation.html', {'crops': crops})

@login_required
def farmer_verification(request):
    """Farmer verification page - submit ID and details"""
    if request.user.role != 'farmer':
        messages.error(request, 'This page is only for farmers.')
        return redirect('accounts:dashboard')
    
    if request.user.farmer_verification_status == 'verified':
        messages.info(request, 'Your account is already verified.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        # Handle document upload and details
        id_document = request.FILES.get('id_document')
        business_permit = request.FILES.get('business_permit')
        land_certificate = request.FILES.get('land_certificate')
        phone = request.POST.get('phone', '').strip()
        location = request.POST.get('location', '').strip()
        farm_size = request.POST.get('farm_size', '').strip()
        experience_years = request.POST.get('experience_years', '').strip()
        
        if not (id_document and phone and location):
            messages.error(request, 'Please provide ID document, phone, and location.')
        else:
            # Create verification documents
            from .models import VerificationDocument
            if id_document:
                VerificationDocument.objects.create(
                    farmer=request.user,
                    document_type='national_id',
                    document_file=id_document,
                    status='pending'
                )
            if business_permit:
                VerificationDocument.objects.create(
                    farmer=request.user,
                    document_type='business_permit',
                    document_file=business_permit,
                    status='pending'
                )
            if land_certificate:
                VerificationDocument.objects.create(
                    farmer=request.user,
                    document_type='land_certificate',
                    document_file=land_certificate,
                    status='pending'
                )
            
            # Update farmer profile
            from .models import FarmerProfile
            profile, _ = FarmerProfile.objects.get_or_create(user=request.user)
            profile.farm_size_acres = farm_size or profile.farm_size_acres
            profile.years_in_business = experience_years or profile.years_in_business
            profile.save()
            
            # Update farmer status
            request.user.farmer_verification_status = 'under_review'
            request.user.phone = phone
            request.user.location = location
            request.user.save(update_fields=['farmer_verification_status', 'phone', 'location'])
            
            # Log action
            AdminActionLog.objects.create(
                admin=None,
                action_type='other',
                target_user=request.user,
                description=f'{request.user.username} submitted verification documents'
            )
            
            messages.success(request, 'Verification documents submitted successfully. Admin will review within 24-48 hours.')
            return redirect('accounts:dashboard')
    
    return render(request, 'accounts/farmer_verification.html', {})


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def activity_logs(request):
    log_entries = AdminActionLog.objects.select_related('admin', 'target_user').order_by('-timestamp')[:50]
    return render(request, 'accounts/admin_activity_logs.html', {'logs': log_entries})


