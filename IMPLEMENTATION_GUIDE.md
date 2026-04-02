# Farm Connect Marketplace - Complete Implementation Guide

## Overview
This is a comprehensive agricultural marketplace platform with advanced features for farmers, buyers, and administrators. The system includes real-time messaging, review ratings, farmer verification, intelligent account management, and a sophisticated admin dashboard.

## Architecture

### Database Models

#### 1. **CustomUser (Enhanced)**
The backbone user model with expanded fields:
- **Fields**: Role (farmer/buyer/admin), phone, location, bio, profile_image
- **New Fields**:
  - `farmer_verification_status`: pending/verified/rejected
  - `account_status`: active/flagged/suspended/blocked
  - `kyc_document`: ID/document upload
  - `last_activity`: Track user activity
  - `is_reported`: Flag for suspicious activity
  - `report_count`: Number of reports against user
  - `suspension_reason` & `suspension_until`: Auto-suspension management

**Key Methods**:
- `is_inactive(days=30)`: Check if user hasn't been active
- `is_suspended()`: Check current suspension status
- `get_rating()`: Get farmer's average rating

#### 2. **FarmerProfile**
Extended profile for farmers with aggregated stats:
- `farm_name`, `farm_size_acres`, `years_in_business`
- `total_reviews`, `rating_score` (0-5), `trust_score`
- `total_products_sold`, `successful_transactions`

#### 3. **VerificationDocument**
KYC verification system:
- `document_type`: national_id, passport, tax_id, business_permit, land_certificate
- `status`: pending/verified/rejected
- `verified_by`: Admin who verified
- `admin_notes`: Verification feedback

#### 4. **CropCategory**
Organize crops by category for better browsing:
- Automatically categorize products
- Filter by category in marketplace

#### 5. **Crop (Enhanced)**
Product listings with enhanced features:
- **New Fields**:
  - `category`: Link to CropCategory
  - `quality_grade`: premium/standard/regular
  - `origin`, `harvest_date`: Product details
  - `is_organic`, `is_trending`: Marketing tags
- **Methods**:
  - `get_average_rating()`: Aggregate product reviews
  - `get_review_count()`: Total reviews

#### 6. **Review & Rating**
Buyer reviews for products and farmers:
- `rating` (1-5 stars)
- `verified_purchase`: Only allow reviews from actual purchases
- `is_approved`: Moderation flag
- `is_flagged`: Spam/abuse detection
- Prevents fake reviews with `unique_together` constraint

#### 7. **Conversation & Message**
Modern threaded messaging system:
- `Conversation`: Thread between participants
- `Message`: Individual message in conversation
- **Features**:
  - Read receipts (`is_read`, `read_at`)
  - Typing indicators (`TypingIndicator` model)
  - Message editing (`is_edited`, `edited_at`)
  - Admin moderation (`deleted_by_admin`, `is_flagged`)
  - Attachment support

#### 8. **MessageAttachment**
File attachments in messages:
- `file_type`: image/document/video/audio/other
- `file_size`: Track bandwidth
- `thumbnail`: Auto-generated for images

#### 9. **Notification**
Centralized notification system:
- `notification_type`: message/review/purchase/verification/system/etc
- User preferences and read tracking
- Dynamic notification creation

#### 10. **UserReport**
Report suspicious activity:
- `report_type`: fraud/harassment/failed_transaction/quality_issue/etc
- `severity`: low/medium/high/critical
- `status`: pending/investigating/resolved/dismissed
- Tracks reviewer and response

#### 11. **AdminActionLog**
Complete audit trail:
- Every admin action is logged
- Tracks: who, what, when, why
- Supports compliance and security auditing

#### 12. **FarmerActivityMetric**
Daily analytics for farmers:
- Tracks products listed, requests received, messages
- Profile views, engagement metrics
- Rating history for trends

#### 13. **InactiveAccountFlag**
Auto-detect and manage inactive accounts:
- Flags farmer accounts inactive > 30 days
- Tracks warning sent date
- Scheduled removal process
- Status: flagged/warning_sent/reactivated/removed

#### 14. **SystemAuditLog**
General system events:
- All significant platform events logged
- IP address and user agent tracking
- Helps identify suspicious patterns

#### 15. **PlatformStats**
Daily platform-wide statistics:
- Total users, products, transactions
- Engagement metrics (messages, reviews, reports)
- Business intelligence data

---

## Features Implementation

### 1. Messaging System (`messaging/` app)

**Models**: Conversation, Message, MessageAttachment, TypingIndicator, Notification

**Views**:
- `conversations_list`: List all conversations
- `conversation_detail`: Open and chat in conversation
- `start_conversation`: Start new chat with user
- `notifications`: View all notifications
- `typing_indicator`: Real-time typing status
- `block_conversation`: Block unwanted chats

**Features**:
✅ Real-time conversation threading
✅ Read receipts with timestamps
✅ Typing indicators
✅ File attachments (images, documents)
✅ Message history
✅ Notification system
✅ Conversation blocking
✅ Message flagging for admin review

**URLs**:
```
/messages/                          - List conversations
/messages/conversation/<id>/        - View conversation
/messages/start/<user_id>/          - Start new chat
/messages/notifications/            - View notifications
```

### 2. Review & Rating System (`crops/` app)

**Models**: Review, Rating (aggregated in FarmerProfile)

**Views**:
- `post_review`: Submit review after purchase
- `farmer_reviews`: View all reviews for farmer
- `flag_review`: Report inappropriate review

**Key Features**:
✅ Purchase-verified reviews only
✅ One review per buyer per farmer
✅ 5-star rating system
✅ Review title and detailed comment
✅ Helpful/unhelpful counts
✅ Admin moderation queue
✅ Spam detection and flagging
✅ Farmer ranking based on reviews

**Prevents Fake Reviews**:
- `verified_purchase` field ensures buyer actually purchased
- Unique constraint: one review per (buyer, farmer, crop)
- Admin approval workflow
- Flagging system for suspicious reviews

### 3. Farmer Verification (`accounts/` app)

**Models**: VerificationDocument, FarmerProfile

**Process**:
1. Farmer uploads KYC documents (ID, tax cert, etc)
2. Documents stored with timestamps
3. Admin reviews in dashboard
4. Approved: `farmer_verification_status = 'verified'`
5. `kyc_verified_date` recorded for audit

**Document Types**:
- National ID / Passport
- Tax ID / Business License
- Land Certificate / Registration
- Other supporting documents

**Admin Workflow**:
```
/dashboard/verifications/              - View pending
/dashboard/verifications/<id>/approve/ - Approve document
```

### 4. Activity Management & Auto-Flagging

**Features**:
- `last_activity` field automatically updated on any action
- `is_inactive(days=30)` method checks inactivity
- `InactiveAccountFlag` model tracks:
  - Flagged date
  - Inactivity duration
  - Warning sent status
  - Removal scheduling
  
**Auto-Actions**:
1. 30 days inactive → Flag account
2. Warning notification sent to farmer
3. 60 days inactive → Mark for removal
4. Admin verifies before removal

**Metrics Dashboard**:
- FarmerActivityMetric tracks daily activity
- Used for analytics and trend detection
- Admin analytics page shows trends

### 5. Account Restrictions & Security

**Status Levels**:
- `active`: Normal operation
- `flagged`: Suspected issue, under review
- `suspended`: Temporarily blocked (with end date)
- `blocked`: Permanently disabled

**Automatic Triggers**:
- Multiple reports → Flag account
- Verified fraud → Suspend account
- Repeated violations → Block permanently

**Manual Admin Actions**:
```
/dashboard/users/<id>/flag/     - Flag user account
/dashboard/users/<id>/suspend/  - Suspend with duration
```

### 6. Admin Dashboard

**Main Views**:
- `admin_dashboard`: Overview with key metrics
- `user_management`: Manage all users
- `user_detail`: View user profile & history
- `user_reports`: Manage reports
- `report_detail`: Handle specific report
- `manage_verifications`: Approve KYC docs
- `activity_logs`: Audit trail of admin actions
- `platform_analytics`: Business intelligence

**Key Widgets**:
- Total users/farmers/buyers
- Active/flagged/suspended accounts
- Pending verifications
- Open reports
- Top-rated farmers
- Recent system actions

**URLs**:
```
/dashboard/              - Main admin dashboard
/dashboard/users/        - User management
/dashboard/reports/      - User reports
/dashboard/verifications/ - KYC verification
/dashboard/logs/         - Activity audit log
/dashboard/analytics/    - Business analytics
```

### 7. Crop Listing & Browsing

**Enhanced Features**:
- **Filtering**: By type, category, price, organic
- **Sorting**: By price, rating, newest, trending
- **Search**: By name, description, origin
- **Saved Listings**: Bookmark favorite products
- **Product Categories**: Organized browsing
- **Quality Grades**: Premium, Standard, Regular

**Product Page Shows**:
- Product reviews and average rating
- Farmer profile with badges
- Farmer's other products
- Purchase request option

**URLs**:
```
/crops/                           - Browse marketplace
/crops/crop/<id>/                - View product detail
/crops/add/                       - Create new listing
/crops/my-listings/              - Manage listings
/crops/saved-listings/           - Saved products
/crops/requests/                 - Purchase requests
```

### 8. Review & Purchase Workflow

**Buyer Flow**:
1. Browse crops → See reviews and ratings
2. Send purchase request
3. Farmer accepts/declines
4. After completion → Post review
5. Review generates notification to farmer
6. Farmer rating updated

**Review Impact**:
- Aggregated into farmer's rating score
- Updates `FarmerProfile.rating_score`
- Influences search ranking
- Displayed on farmer profile

---

## Admin Features

### User Management
- View all farmers and buyers
- Filter by role and account status
- View detailed user profile
- See all actions against user
- View user activity metrics

### Report Handling
- View all user reports
- Filter by severity and status
- Detailed report investigation
- Take action: suspend, warn, or dismiss
- Create detailed audit log

### Verification Management
- Review pending KYC documents
- Approve or reject with notes
- Document change tracking
- Verify farmer account
- Email notifications to farmers

### Account Restrictions
- Flag suspicious accounts
- Suspend temporarily with duration
- Block permanently
- Add suspension reason
- Track all actions with audit log

### System Auditing
- Complete action log
  - Admin actions (flag, suspend, ban)
  - System actions (auto-flagging, removal)
  - User actions (important events)
- Filter by action type, user, date
- Export for compliance

### Analytics & Reporting
- Platform stats dashboard
- Top-rated farmers
- Most active buyers
- Popular products
- Transaction trends
- User growth metrics

---

## Security Features

### 1. Farmer Verification
- Multi-document KYC process
- Admin approval required
- Document versioning
- Verified date tracking

### 2. Review Integrity
- Purchase verification required
- One review per farmer limit
- Spam detection
- Admin moderation queue

### 3. Account Security
- Automatic inactivity detection
- Multi-level account status
- Suspension mechanism
- Permanent blocking option

### 4. Communication Safety
- Message moderation by admin
- Ability to flag/remove messages
- Conversation blocking
- Report system for harassment

### 5. Audit Trail
- Admin action logging
- System event tracking
- IP address recording
- User agent tracking
- Compliance ready

---

## API & Integration Points

### Admin API Endpoints
```
GET  /dashboard/                 - Admin dashboard
GET  /dashboard/users/           - List users
GET  /dashboard/users/<id>/      - User detail
POST /dashboard/users/<id>/flag/ - Flag user
POST /dashboard/users/<id>/suspend/ - Suspend user
GET  /dashboard/reports/         - List reports
POST /dashboard/reports/<id>/    - Handle report
GET  /dashboard/verifications/   - Pending verifications
POST /dashboard/verifications/<id>/approve/ - Approve doc
GET  /dashboard/analytics/       - Analytics dashboard
```

### Messaging API
```
GET  /messages/                  - Conversations list
GET  /messages/conversation/<id>/ - View conversation
POST /messages/conversation/<id>/ - Send message
POST /messages/start/<user_id>/  - Start new chat
GET  /messages/notifications/    - View notifications
```

### Crops API
```
GET  /crops/                     - Browse marketplace
GET  /crops/crop/<id>/          - Product detail
POST /crops/review/<id>/        - Post review
GET  /crops/farmer/<id>/reviews/ - View farmer reviews
POST /crops/review/<id>/flag/   - Flag review
```

---

## Business Logic

### Farmer Ranking Algorithm
1. Collect all reviews for farmer
2. Filter approved reviews only
3. Calculate average rating (0-5)
4. Count total reviews
5. Recent reviews weighted higher
6. Updated in real-time

### Inactivity Detection
1. Track `last_activity` on every action
2. Daily check for farmers > 30 days inactive
3. Create `InactiveAccountFlag`
4. Send warning notification
5. If still inactive after 7 days → schedule removal
6. Admin can reactivate account

### Review Verification
1. Check purchase completed
2. Verify buyer is actual purchaser
3. One review per (buyer, farmer, crop)
4. Auto-approve if not flagged
5. Flagged reviews in moderation queue
6. Admin can approve/reject

---

## Setup Instructions

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser
```

### 3. Collect Static Files
```bash
python manage.py collectstatic
```

### 4. Update Settings
Add to `settings.py`:
- REST framework for future API
- Celery for background tasks (email, inactivity detection)
- WebSocket support (django-channels) for real-time messaging

### 5. Create Initial Data
```bash
python manage.py shell
from crops.models import CropCategory
CropCategory.objects.create(
    name='Legumes',
    slug='legumes',
    description='Beans, peas, lentils'
)
# ... add more categories
```

---

## Next Steps & Recommendations

### Phase 2: Real-Time Features
1. **WebSocket Integration** (django-channels)
   - Live typing indicators
   - Real-time notifications
   - Live activity updates

2. **Background Tasks** (Celery)
   - Inactivity detection (daily cron)
   - Notification delivery
   - Report auto-escalation
   - Email notifications

### Phase 3: Advanced Analytics
1. Dashboard charts and graphs
2. Trend analysis
3. Predictive analytics for farmer success
4. Seasonal trends

### Phase 4: Mobile App
1. React Native / Flutter app
2. Native push notifications
3. Offline messaging queue
4. Image compression for messaging

### Phase 5: Payment Integration
1. M-Pesa payment gateway
2. Escrow system
3. Commission calculation
4. Transaction history

### Phase 6: Machine Learning
1. Product recommendation engine
2. Farmer matching (buyer finds compatible farmer)
3. Fraud detection
4. Review sentiment analysis

---

## File Structure
```
project/
├── admin_panel/              # Admin features
│   ├── models.py            # Reports, logs, analytics
│   ├── views.py             # Admin views
│   ├── urls.py              # Admin routes
│   └── admin.py             # Django admin config
├── accounts/                # User management
│   ├── models.py            # CustomUser, FarmerProfile, VerificationDocument
│   └── forms.py             # User registration, verification forms
├── crops/                   # Product catalog
│   ├── models.py            # Crop, Review, PurchaseRequest, CropCategory
│   ├── views.py             # Product, review, rating views
│   ├── forms.py             # Crop and review forms
│   └── urls.py              # Product routes
├── messaging/               # Chat system
│   ├── models.py            # Conversation, Message, Notification
│   ├── views.py             # Messaging views
│   ├── forms.py             # Message forms
│   └── urls.py              # Message routes
├── frontend/
│   ├── templates/           # HTML templates
│   └── static/
│       └── css/
│           └── marketplace.css  # Modern theme
└── requirements.txt         # Python dependencies
```

---

## Troubleshooting

### Issue: Migrations fail
**Solution**:
```bash
python manage.py migrate --fake admin_panel 0001
python manage.py migrate
```

### Issue: Static files not loading
**Solution**:
```bash
python manage.py collectstatic --noinput
```

### Issue: Images not uploading
**Solution**: Ensure `MEDIA_ROOT` and `MEDIA_URL` in settings.py

### Issue: Admin dashboard 404
**Solution**: Ensure user is_staff and role='admin'

---

## Security Notes

1. **Verification**: Always require KYC before farmer can sell
2. **Rate Limiting**: Add rate limiting to prevent spam
3. **File Uploads**: Validate and scan files for malware
4. **SQL Injection**: Use ORM (Django queryset) - never raw SQL
5. **CSRF**: Django middleware enabled by default
6. **XSS**: Use `{{ var|escape }}` in templates

---

## Performance Optimization

1. **Database Indexes**: Already added on key queries
2. **Select Related**: Implemented in views (less queries)
3. **Pagination**: Crop list shows 12 per page
4. **Caching**: Add Redis for frequently accessed data
5. **Async Tasks**: Use Celery for heavy processing

---

## Testing

Example test file creation:
```bash
# For admin_panel
touch admin_panel/tests.py

# For crops
touch crops/tests.py

# For messaging
touch messaging/tests.py

# Run tests
python manage.py test
```

---

## Support & Documentation

- Django Documentation: https://docs.djangoproject.com/
- Django Best Practices: https://www.codementor.io/@sheena/django-best-practices-n6qlo
- Security: https://django.readthedocs.io/en/stable/topics/security/

---

**Last Updated**: March 31, 2026
**Version**: 1.0 Beta
