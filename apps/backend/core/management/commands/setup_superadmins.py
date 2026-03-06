"""
Management command to create the 3 authorized Super Admin accounts.

Usage:
    python manage.py setup_superadmins

This will create or update the 3 super admin accounts with:
- Superuser privileges (is_superuser=True, is_staff=True)
- Emails from the ALLOWED_SUPERADMIN_EMAILS list
- Strong default passwords (should be changed after first login)
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import User

# Must match the list in admin.py and middleware.py
ALLOWED_SUPERADMIN_EMAILS = [
    "superadmin1@example.com",  # Replace with actual email
    "superadmin2@example.com",  # Replace with actual email
    "superadmin3@example.com",  # Replace with actual email
]

# Default passwords (MUST be changed after first login)
DEFAULT_PASSWORDS = {
    "superadmin1@example.com": "SuperAdmin2026!#1",  # Strong password
    "superadmin2@example.com": "SuperAdmin2026!#2",
    "superadmin3@example.com": "SuperAdmin2026!#3",
}


class Command(BaseCommand):
    help = "Create or update the 3 authorized Super Administrator accounts"

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip accounts that already exist (don\'t update them)',
        )

    def handle(self, *args, **options):
        skip_existing = options['skip_existing']
        
        self.stdout.write(self.style.WARNING(
            "\n" + "=" * 70 + "\n"
            "SUPER ADMIN SETUP\n"
            "=" * 70 + "\n"
        ))
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for email in ALLOWED_SUPERADMIN_EMAILS:
                # Generate username from email
                username = email.split('@')[0]
                
                # Check if user exists
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': username,
                        'is_superuser': True,
                        'is_staff': True,
                        'is_active': True,
                        'first_name': 'Super',
                        'last_name': 'Admin',
                    }
                )
                
                if created:
                    # Set password for new user
                    password = DEFAULT_PASSWORDS.get(email, 'ChangeMe2026!')
                    user.set_password(password)
                    user.save()
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Created: {email}\n"
                        f"   Username: {username}\n"
                        f"   Password: {password}\n"
                        f"   ⚠️  IMPORTANT: Change this password immediately after first login!\n"
                    ))
                    created_count += 1
                    
                else:
                    if skip_existing:
                        self.stdout.write(self.style.WARNING(
                            f"⏭️  Skipped: {email} (already exists)\n"
                        ))
                        skipped_count += 1
                    else:
                        # Update existing user to ensure they have correct permissions
                        user.is_superuser = True
                        user.is_staff = True
                        user.is_active = True
                        user.save()
                        
                        self.stdout.write(self.style.SUCCESS(
                            f"🔄 Updated: {email}\n"
                            f"   Ensured: is_superuser=True, is_staff=True, is_active=True\n"
                        ))
                        updated_count += 1
        
        # Summary
        self.stdout.write(self.style.WARNING(
            "\n" + "=" * 70 + "\n"
            "SUMMARY\n"
            "=" * 70 + "\n"
        ))
        
        self.stdout.write(
            f"✅ Created: {created_count}\n"
            f"🔄 Updated: {updated_count}\n"
            f"⏭️  Skipped: {skipped_count}\n"
            f"📊 Total authorized: {len(ALLOWED_SUPERADMIN_EMAILS)}\n"
        )
        
        if created_count > 0:
            self.stdout.write(self.style.WARNING(
                "\n⚠️  SECURITY REMINDER:\n"
                "All new accounts have default passwords shown above.\n"
                "These MUST be changed immediately after first login!\n"
            ))
        
        self.stdout.write(self.style.SUCCESS(
            "\n✅ Super Admin setup completed successfully!\n"
            "\nThese accounts can now access the Django Admin at /admin/\n"
            "All other users will be blocked by the SuperAdminAccessMiddleware.\n"
        ))
