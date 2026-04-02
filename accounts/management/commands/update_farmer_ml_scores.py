from django.core.management.base import BaseCommand
from accounts.ml_utils import update_farmer_risk_scores

class Command(BaseCommand):
    help = 'Update farmers trust score and risk level using ML model based on activity/reviews/reports.'

    def handle(self, *args, **options):
        try:
            results = update_farmer_risk_scores()
            if not results:
                self.stdout.write(self.style.WARNING('No farmers to evaluate or not enough data.'))
                return

            for row in results:
                self.stdout.write(f"Farmer {row['farmer']}: trust_score={row['trust_score']}, risk_level={row['risk_level']}")

            self.stdout.write(self.style.SUCCESS('Farmer ML scores updated successfully.'))

        except ImportError as ie:
            self.stdout.write(self.style.ERROR('Missing dependency: please install scikit-learn.'))
            self.stdout.write(str(ie))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating ML scores: {e}'))
            raise
