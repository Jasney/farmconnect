from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser
from crops.models import Crop, PurchaseRequest

class PurchaseRequestTests(TestCase):
    def setUp(self):
        self.farmer = CustomUser.objects.create_user(username='farmer1', password='test12345', role='farmer')
        self.buyer = CustomUser.objects.create_user(username='buyer1', password='test12345', role='buyer')
        self.crop = Crop.objects.create(
            name='Test Maize',
            type='maize',
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
