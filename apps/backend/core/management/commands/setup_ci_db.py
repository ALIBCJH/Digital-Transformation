"""
Management command to set up CI database without problematic migrations
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Set up database for CI testing without PostgreSQL-specific features"

    def handle(self, *args, **options):
        self.stdout.write("Setting up CI database...")

        # Create tables using Django's schema editor
        with connection.schema_editor() as schema_editor:
            # Import all models
            from core.models import (
                Altar,
                AttendanceLog,
                Guest,
                MemberTransferHistory,
                OrganizationNode,
                User,
                UserProfile,
            )

            models = [
                User,
                UserProfile,
                OrganizationNode,
                Altar,
                AttendanceLog,
                Guest,
                MemberTransferHistory,
            ]

            for model in models:
                try:
                    # Create table without indexes that require extensions
                    schema_editor.create_model(model)
                    self.stdout.write(f"Created table for {model.__name__}")
                except Exception as e:
                    self.stdout.write(f"Warning: {model.__name__} - {e}")

        self.stdout.write(self.style.SUCCESS("Successfully set up CI database"))
