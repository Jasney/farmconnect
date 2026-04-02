from django.test import TestCase
from django.urls import reverse

class BasicTests(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Farm Connect')