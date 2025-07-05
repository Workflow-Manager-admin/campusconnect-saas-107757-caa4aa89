from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from api.models import User, College, CollegeAdmin, UserRole


class Command(BaseCommand):
    help = 'Set up initial data for the CampusConnect system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a super admin user',
        )
        parser.add_argument(
            '--create-sample-college',
            action='store_true',
            help='Create a sample college with admin',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up initial data...'))

        if options['create_superuser']:
            self.create_superuser()

        if options['create_sample_college']:
            self.create_sample_college()

        self.stdout.write(self.style.SUCCESS('Initial data setup completed!'))

    def create_superuser(self):
        """Create a super admin user if it doesn't exist."""
        email = 'admin@campusconnect.com'
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Super admin user {email} already exists')
            )
            return

        User.objects.create(
            email=email,
            password_hash=make_password('admin123'),
            first_name='Super',
            last_name='Admin',
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            email_verified=True
        )

        self.stdout.write(
            self.style.SUCCESS(f'Super admin user created: {email} / admin123')
        )

    def create_sample_college(self):
        """Create a sample college with admin user."""
        college_code = 'SAMPLE001'
        
        if College.objects.filter(code=college_code).exists():
            self.stdout.write(
                self.style.WARNING(f'Sample college {college_code} already exists')
            )
            return

        # Create college
        college = College.objects.create(
            name='Sample University',
            code=college_code,
            address='123 University Street',
            city='Sample City',
            state='Sample State',
            country='India',
            postal_code='123456',
            website='https://sample-university.edu',
            contact_email='info@sample-university.edu',
            contact_phone='+91-1234567890',
            description='Sample university for testing purposes',
            is_active=True,
            subscription_plan='premium',
            subscription_expires_at=timezone.now() + timezone.timedelta(days=365)
        )

        # Create college admin user
        admin_email = 'tpo@sample-university.edu'
        admin_user = User.objects.create(
            email=admin_email,
            password_hash=make_password('tpo123'),
            first_name='TPO',
            last_name='Admin',
            role=UserRole.TPO,
            is_active=True,
            email_verified=True
        )

        # Create college admin relationship
        CollegeAdmin.objects.create(
            user=admin_user,
            college=college,
            designation='Training & Placement Officer',
            department='Placement Cell',
            is_primary=True,
            permissions={
                'can_manage_jobs': True,
                'can_manage_students': True,
                'can_send_notifications': True,
                'can_view_analytics': True
            }
        )

        self.stdout.write(
            self.style.SUCCESS(f'Sample college created: {college.name}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'College admin created: {admin_email} / tpo123')
        )
