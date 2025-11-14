from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with developer privileges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            help='Specifies the username for the superuser.',
        )
        parser.add_argument(
            '--email',
            help='Specifies the email for the superuser.',
        )
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false',
            dest='interactive',
            help=('Tells Django to NOT prompt the user for input of any kind. '
                  'You must use --username and --email with --noinput.'),
        )
        parser.add_argument(
            '--database',
            default=DEFAULT_DB_ALIAS,
            help='Specifies the database to use. Default is "default".',
        )

    def handle(self, **options):
        username = options['username']
        email = options['email']
        interactive = options['interactive']
        database = options['database']

        # Use Django's built-in createsuperuser but with our custom user model
        call_command(
            'createsuperuser',
            username=username,
            email=email,
            interactive=interactive,
            database=database,
        )
        
        # The superuser will automatically be set as developer due to our CustomUser.save() method
        if username:
            user = User.objects.get(username=username)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser "{username}" created successfully with Developer privileges!'
                )
            )