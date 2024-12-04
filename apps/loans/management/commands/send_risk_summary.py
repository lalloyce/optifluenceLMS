from django.core.management.base import BaseCommand
from django.utils import timezone
from ...services.alert_notifications import AlertNotificationService

class Command(BaseCommand):
    help = 'Send daily risk alerts summary'

    def handle(self, *args, **options):
        try:
            AlertNotificationService.send_daily_summary()
            self.stdout.write(
                self.style.SUCCESS('Successfully sent daily risk alerts summary')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending daily summary: {str(e)}')
            )
