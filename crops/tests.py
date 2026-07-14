from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser
from crops.models import Crop, PurchaseRequest, SavedListing
from crops.forms import ReviewForm
from market.models import MarketPrice

class PurchaseRequestTests(TestCase):
    def setUp(self):
        self.farmer = CustomUser.objects.create_user(
            username='farmer1',
            password='test12345',
            role='farmer',
            farmer_verification_status='verified',
            account_status='active',
        )
        self.buyer = CustomUser.objects.create_user(username='buyer1', password='test12345', role='buyer')
        self.crop = Crop.objects.create(
            name='Test Maize',
            type='cereals',
            price_per_unit=100.00,
            quantity_available=100,
            unit='kg',
            description='Test crop',
            farmer=self.farmer,
        )

    def test_buyer_can_create_purchase_request(self):
        self.client.login(username='buyer1', password='test12345')
        response = self.client.post(reverse('send_purchase_request', args=[self.crop.id]), {
            'quantity_requested': 10,
            'message': 'Need this ASAP'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PurchaseRequest.objects.filter(buyer=self.buyer, crop=self.crop).exists())

    def test_farmer_cannot_send_purchase_request(self):
        self.client.login(username='farmer1', password='test12345')
        response = self.client.post(reverse('send_purchase_request', args=[self.crop.id]), {
            'quantity_requested': 10,
            'message': 'Invalid request'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PurchaseRequest.objects.filter(buyer=self.farmer, crop=self.crop).exists())


class CropRegressionTests(TestCase):
    def setUp(self):
        self.farmer = CustomUser.objects.create_user(
            username='verifiedfarmer',
            password='test12345',
            role='farmer',
            farmer_verification_status='verified',
            account_status='active',
            location='Nairobi',
        )
        self.matching_buyer = CustomUser.objects.create_user(
            username='seriousbuyer',
            password='test12345',
            role='buyer',
            location='Nairobi',
        )
        self.crop = Crop.objects.create(
            name='Beans',
            type='legumes',
            price_per_unit=120.00,
            quantity_available=25,
            unit='kg',
            description='Fresh beans',
            farmer=self.farmer,
        )
        self.other_crop = Crop.objects.create(
            name='Beans',
            type='legumes',
            price_per_unit=118.00,
            quantity_available=40,
            unit='kg',
            description='Similar beans crop',
            farmer=self.farmer,
        )
        SavedListing.objects.create(user=self.matching_buyer, crop=self.crop)
        PurchaseRequest.objects.create(
            buyer=self.matching_buyer,
            crop=self.other_crop,
            quantity_requested=10,
            agreed_price=self.other_crop.price_per_unit,
            status='completed',
        )
        MarketPrice.objects.create(crop_name='Beans', price=110.00, unit='kg', location='Nairobi')
        MarketPrice.objects.create(crop_name='Beans', price=132.00, unit='kg', location='Kiambu')

    def test_review_form_initializes(self):
        form = ReviewForm()
        self.assertIn('title', form.fields)
        self.assertIn('comment', form.fields)

    def test_crop_detail_works_without_farmer_profile(self):
        response = self.client.get(reverse('crop_detail', args=[self.crop.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beans')
        self.assertContains(response, 'Market Insight')

    def test_crop_update_redirects_to_detail(self):
        self.client.login(username='verifiedfarmer', password='test12345')
        response = self.client.post(reverse('crop_update', args=[self.crop.id]), {
            'name': 'Updated Beans',
            'type': 'legumes',
            'price_per_unit': '130.00',
            'quantity_available': 20,
            'unit': 'kg',
            'description': 'Updated stock',
            'quality_grade': 'standard',
            'is_organic': 'on',
        })
        self.assertRedirects(response, reverse('crop_detail', args=[self.crop.id]))

    def test_crop_detail_shows_buyer_matches_for_owner(self):
        self.client.login(username='verifiedfarmer', password='test12345')
        response = self.client.get(reverse('crop_detail', args=[self.crop.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buyer Matches')
        self.assertContains(response, 'seriousbuyer')

    def test_flag_review_without_referer_redirects_to_crop_detail(self):
        buyer = CustomUser.objects.create_user(username='buyer2', password='test12345', role='buyer')
        purchase_request = PurchaseRequest.objects.create(
            buyer=buyer,
            crop=self.crop,
            quantity_requested=5,
            agreed_price=self.crop.price_per_unit,
            status='completed',
        )
        review = self.crop.reviews.create(
            buyer=buyer,
            farmer=self.farmer,
            rating=5,
            title='Great',
            comment='Excellent produce',
            purchase_request=purchase_request,
            verified_purchase=True,
        )

        self.client.login(username='buyer2', password='test12345')
        response = self.client.post(reverse('flag_review', args=[review.id]), {
            'reason': 'Spam'
        })

        self.assertRedirects(response, reverse('crop_detail', args=[self.crop.id]))


class MarketplaceAiFeatureTests(TestCase):
    def setUp(self):
        self.farmer = CustomUser.objects.create_user(
            username='farmerai',
            password='test12345',
            role='farmer',
            farmer_verification_status='verified',
            account_status='active',
            location='Nairobi',
        )
        self.buyer = CustomUser.objects.create_user(
            username='buyeralpha',
            password='test12345',
            role='buyer',
            location='Kiambu',
        )
        self.crop = Crop.objects.create(
            name='Maize',
            type='cereals',
            price_per_unit=95.00,
            quantity_available=60,
            unit='kg',
            description='Dry maize',
            farmer=self.farmer,
        )
        SavedListing.objects.create(user=self.buyer, crop=self.crop)
        MarketPrice.objects.create(crop_name='Maize', price=100.00, unit='kg', location='Nairobi')
        MarketPrice.objects.create(crop_name='Maize', price=108.00, unit='kg', location='Eldoret')

    def test_dashboard_shows_price_insights(self):
        self.client.login(username='farmerai', password='test12345')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Price Insights')
        self.assertContains(response, 'AI Assistant')

    def test_ai_assistant_answers_price_question(self):
        self.client.login(username='farmerai', password='test12345')
        response = self.client.post(reverse('accounts:ai_assistant'), {
            'question': 'What is the price of maize?'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Market outlook for Maize')
        self.assertContains(response, 'Average market price')
