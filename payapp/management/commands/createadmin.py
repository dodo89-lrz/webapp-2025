from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates the default admin1 user if it does not exist'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin1').exists():
            User.objects.create_superuser(
                username='admin1',
                email='admin1@example.com',
                password='admin1'
            )
            self.stdout.write(self.style.SUCCESS('Superuser "admin1" created successfully.'))
        else:
            self.stdout.write('Superuser "admin1" already exists.')
