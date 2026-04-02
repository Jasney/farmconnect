import numpy as np
from sklearn.linear_model import LogisticRegression
from django.utils import timezone
from django.db.models import Avg
from .models import CustomUser, FarmerProfile
from crops.models import Review, PurchaseRequest
from admin_panel.models import UserReport


def compute_farmer_features(farmer):
    """Extract feature vector for a farmer"""
    avg_rating = Review.objects.filter(farmer=farmer, is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0
    report_count = getattr(farmer, 'report_count', 0) or UserReport.objects.filter(reported_user=farmer).count()
    successful_transactions = PurchaseRequest.objects.filter(crop__farmer=farmer, status='completed').count()
    days_inactive = (timezone.now() - farmer.last_activity).days if farmer.last_activity else 999
    total_reviews = Review.objects.filter(farmer=farmer, is_approved=True).count()

    return np.array([
        avg_rating,
        report_count,
        successful_transactions,
        days_inactive,
        total_reviews,
    ], dtype=float)


def train_trust_model():
    """Train a simple logistic regression model from existing farmer data."""
    from .models import CustomUser
    from admin_panel.models import UserReport

    farmers = CustomUser.objects.filter(role='farmer')
    X = []
    y = []

    for f in farmers:
        features = compute_farmer_features(f)

        # indirect label: trusted when active and low report_count and high rating
        label = 1 if (f.account_status == 'active' and f.report_count < 2 and (features[0] >= 3.5 or features[2] >= 3)) else 0

        X.append(features)
        y.append(label)

    if len(X) < 2:
        raise ValueError('Not enough farmers for training model')

    X_array = np.stack(X)
    y_array = np.array(y)

    model = LogisticRegression(solver='liblinear')
    model.fit(X_array, y_array)

    return model


def update_farmer_risk_scores():
    """Update trust and risk predictions for all farmers"""
    from admin_panel.models import UserReport

    farmers = CustomUser.objects.filter(role='farmer')
    if farmers.count() < 2:
        return []

    try:
        model = train_trust_model()
    except Exception as e:
        return []

    results = []
    from admin_panel.models import UserReport

    for farmer in farmers:
        features = compute_farmer_features(farmer).reshape(1, -1)
        prob = model.predict_proba(features)[0, 1]

        # map probability to trust score 0-5
        trust_score = round(min(5.0, max(0.0, prob * 5)), 2)

        profile, _ = FarmerProfile.objects.get_or_create(user=farmer)
        profile.trust_score = trust_score
        profile.risk_level = 'trusted' if prob >= 0.7 else ('risky' if prob < 0.35 else 'moderate')
        profile.save()

        farmer.farmer_verification_status = farmer.farmer_verification_status or 'pending'
        farmer.save(update_fields=['farmer_verification_status'])

        report_count = UserReport.objects.filter(reported_user=farmer).count()

        # Auto-flag or block risky farmers
        if profile.risk_level == 'risky' and farmer.account_status == 'active':
            if report_count >= 5:
                farmer.account_status = 'blocked'
                log_action = 'auto_block'
                description = f"Auto-blocked due to very low trust score ({profile.trust_score}) and high report count ({report_count})"
            else:
                farmer.account_status = 'flagged'
                log_action = 'auto_flag'
                description = f"Auto-flagged due to low trust score ({profile.trust_score})"

            farmer.save(update_fields=['account_status'])
            # Log the auto-action
            from admin_panel.models import AdminActionLog
            AdminActionLog.objects.create(
                admin=None,  # System action
                action_type=log_action,
                target_user=farmer,
                description=description,
                reason='ML Risk Detection'
            )

        results.append({'farmer': farmer.username, 'trust_score': trust_score, 'risk_level': profile.risk_level})

    return results
