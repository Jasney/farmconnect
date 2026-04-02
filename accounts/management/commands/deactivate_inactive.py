from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Deactivate inactive farmer accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days of inactivity before deactivation',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deactivated without actually doing it',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        threshold = timezone.now() - timedelta(days=days)
        
        inactive_farmers = CustomUser.objects.filter(
            role='farmer',
            last_activity__lt=threshold,
            account_status='active'
        )
        
        count = inactive_farmers.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would deactivate {count} inactive farmer accounts (inactive for {days} days)'
                )
            )
            for farmer in inactive_farmers[:5]:  # Show first 5
                self.stdout.write(f'  - {farmer.username} (last activity: {farmer.last_activity})')
            if count > 5:
                self.stdout.write(f'  ... and {count - 5} more')
        else:
            deactivated = inactive_farmers.update(account_status='blocked')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deactivated {deactivated} inactive farmer accounts'
                )
            )