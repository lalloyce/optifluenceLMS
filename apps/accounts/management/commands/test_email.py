from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument('--to', type=str, help='Email address to send test email to')

    def handle(self, *args, **options):
        to_email = options.get('to')
        if not to_email:
            self.stdout.write(self.style.ERROR('Please provide an email address using --to parameter'))
            return

        try:
            subject = 'Test Email from OptifluenceLMS'
            message = 'This is a test email from your OptifluenceLMS application. If you receive this, your email configuration is working correctly!'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [to_email]

            self.stdout.write(self.style.WARNING(f'Sending test email to {to_email}...'))
            
            result = send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )

            if result:
                self.stdout.write(self.style.SUCCESS('Test email sent successfully!'))
                self.stdout.write(self.style.SUCCESS(f'From: {from_email}'))
                self.stdout.write(self.style.SUCCESS(f'To: {to_email}'))
            else:
                self.stdout.write(self.style.ERROR('Failed to send test email'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sending email: {str(e)}'))
