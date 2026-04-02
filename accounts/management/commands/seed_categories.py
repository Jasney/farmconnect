from django.core.management.base import BaseCommand
from crops.models import CropCategory

class Command(BaseCommand):
    help = 'Seed initial crop categories'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Legumes', 'slug': 'legumes', 'description': 'Beans, peas, lentils, and other legumes'},
            {'name': 'Cereals', 'slug': 'cereals', 'description': 'Wheat, maize, rice, barley, and other grains'},
            {'name': 'Fruits', 'slug': 'fruits', 'description': 'Apples, oranges, bananas, mangoes, and other fruits'},
            {'name': 'Vegetables', 'slug': 'vegetables', 'description': 'Leafy greens, root vegetables, and other veggies'},
            {'name': 'Tubers', 'slug': 'tubers', 'description': 'Potatoes, cassava, sweet potatoes, and other tubers'},
        ]

        for cat_data in categories:
            category, created = CropCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Category seeding completed.')
        )