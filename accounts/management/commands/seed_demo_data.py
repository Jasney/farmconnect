from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import FarmerProfile
from crops.models import CropCategory, Crop

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed demo farmers, crops, and buyer accounts for testing marketplace flow'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding demo data...'))

        # Ensure categories exist
        categories = [
            {'name': 'Legumes', 'slug': 'legumes', 'description': 'Beans, peas, lentils and other legumes'},
            {'name': 'Cereals', 'slug': 'cereals', 'description': 'Wheat, maize, rice and other grains'},
            {'name': 'Vegetables', 'slug': 'vegetables', 'description': 'Leafy greens and root vegetables'},
            {'name': 'Fruits', 'slug': 'fruits', 'description': 'Seasonal and tropical fruits'},
            {'name': 'Other', 'slug': 'other', 'description': 'Miscellaneous produce'},
        ]
        for cat_data in categories:
            CropCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'description': cat_data['description']}
            )

        # Create verified farmer accounts
        farmer_infos = [
            {'username': 'farmer_joel', 'email': 'joel@example.com', 'full_name': 'Joel Farm'},
            {'username': 'farmer_ruby', 'email': 'ruby@example.com', 'full_name': 'Ruby Farms'},
            {'username': 'farmer_amy', 'email': 'amy@example.com', 'full_name': 'Amy Agro'},
            {'username': 'farmer_hassan', 'email': 'hassan@example.com', 'full_name': 'Hassan Harvest'},
            {'username': 'farmer_kemi', 'email': 'kemi@example.com', 'full_name': 'Kemi Crops'},
            {'username': 'farmer_tunde', 'email': 'tunde@example.com', 'full_name': 'Tunde Greenery'},
            {'username': 'farmer_rose', 'email': 'rose@example.com', 'full_name': 'Rose Orchards'},
            {'username': 'farmer_owen', 'email': 'owen@example.com', 'full_name': 'Owen AgroTech'},
        ]

        farmers = []
        for idx, info in enumerate(farmer_infos, start=1):
            user, created = User.objects.get_or_create(
                username=info['username'],
                defaults={
                    'email': info['email'],
                    'role': 'farmer',
                    'first_name': info['full_name'].split()[0],
                    'last_name': ' '.join(info['full_name'].split()[1:]) or '',
                    'farmer_verification_status': 'verified',
                    'is_verified': True,
                    'account_status': 'active',
                    'national_id': f'ID{1000 + idx}',
                }
            )
            if created:
                user.set_password('farmerpass123')
                user.save()

            user.role = 'farmer'
            user.farmer_verification_status = 'verified'
            user.is_verified = True
            user.account_status = 'active'
            user.save()

            profile, _ = FarmerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'farm_name': info['full_name'],
                    'farm_size_acres': 10 + idx * 2,
                    'years_in_business': 2 + idx,
                    'trust_score': min(9.5, 2.0 + idx * 0.4),
                    'risk_level': 'trusted',
                }
            )
            farmers.append(user)

        # Create crops for each farmer
        sample_crops = [
            {'name': 'Red Beans', 'type': 'legumes', 'category_slug': 'legumes', 'price_per_unit': 95.00, 'quantity_available': 120, 'unit': 'kg', 'quality_grade': 'premium', 'is_organic': True},
            {'name': 'White Maize', 'type': 'cereals', 'category_slug': 'cereals', 'price_per_unit': 65.00, 'quantity_available': 220, 'unit': 'kg', 'quality_grade': 'standard', 'is_organic': False},
            {'name': 'Cabbage', 'type': 'vegetables', 'category_slug': 'vegetables', 'price_per_unit': 12.00, 'quantity_available': 400, 'unit': 'kg', 'quality_grade': 'standard', 'is_organic': True},
            {'name': 'Mango', 'type': 'fruits', 'category_slug': 'fruits', 'price_per_unit': 170.00, 'quantity_available': 90, 'unit': 'kg', 'quality_grade': 'premium', 'is_organic': False},
            {'name': 'Cassava', 'type': 'other', 'category_slug': 'other', 'price_per_unit': 45.00, 'quantity_available': 300, 'unit': 'kg', 'quality_grade': 'standard', 'is_organic': False},
            {'name': 'Green Peas', 'type': 'legumes', 'category_slug': 'legumes', 'price_per_unit': 150.00, 'quantity_available': 80, 'unit': 'kg', 'quality_grade': 'premium', 'is_organic': True},
            {'name': 'Rice', 'type': 'cereals', 'category_slug': 'cereals', 'price_per_unit': 120.00, 'quantity_available': 130, 'unit': 'kg', 'quality_grade': 'standard', 'is_organic': False},
            {'name': 'Tomato', 'type': 'vegetables', 'category_slug': 'vegetables', 'price_per_unit': 30.00, 'quantity_available': 360, 'unit': 'kg', 'quality_grade': 'premium', 'is_organic': True},
        ]

        for idx, farmer in enumerate(farmers):
            seed = sample_crops[idx % len(sample_crops)]
            category = CropCategory.objects.get(slug=seed['category_slug'])

            Crop.objects.update_or_create(
                name=f"{seed['name']} - {farmer.username}",
                farmer=farmer,
                defaults={
                    'type': seed['type'],
                    'category': category,
                    'price_per_unit': seed['price_per_unit'],
                    'quantity_available': seed['quantity_available'],
                    'unit': seed['unit'],
                    'description': f"Fresh {seed['name']} from {farmer.farmer_profile.farm_name}.",
                    'quality_grade': seed['quality_grade'],
                    'origin': farmer.location or 'Local Farm',
                    'harvest_date': None,
                    'is_organic': seed['is_organic'],
                    'is_trending': idx % 2 == 0,
                    'is_active': True,
                }
            )

            extra_variant = sample_crops[(idx + 1) % len(sample_crops)]
            category2 = CropCategory.objects.get(slug=extra_variant['category_slug'])
            Crop.objects.update_or_create(
                name=f"{extra_variant['name']} - {farmer.username}",
                farmer=farmer,
                defaults={
                    'type': extra_variant['type'],
                    'category': category2,
                    'price_per_unit': extra_variant['price_per_unit'],
                    'quantity_available': extra_variant['quantity_available'],
                    'unit': extra_variant['unit'],
                    'description': f"Premium {extra_variant['name']} from {farmer.farmer_profile.farm_name}.",
                    'quality_grade': extra_variant['quality_grade'],
                    'origin': farmer.location or 'Local Farm',
                    'harvest_date': None,
                    'is_organic': extra_variant['is_organic'],
                    'is_trending': (idx + 1) % 2 == 0,
                    'is_active': True,
                }
            )

        # Create buyer accounts
        buyer_infos = [
            {'username': 'buyer_ken', 'email': 'ken@example.com'},
            {'username': 'buyer_ana', 'email': 'ana@example.com'},
        ]
        for info in buyer_infos:
            buyer, created = User.objects.get_or_create(
                username=info['username'],
                defaults={
                    'email': info['email'],
                    'role': 'buyer',
                    'is_verified': True,
                    'account_status': 'active',
                }
            )
            if created:
                buyer.set_password('buyerpass123')
                buyer.save()

        self.stdout.write(self.style.SUCCESS('Seeding farmers, crops and buyer accounts completed.'))
        self.stdout.write(self.style.SUCCESS('Use login credentials farmer*/farmerpass123 and buyer*/buyerpass123.'))
