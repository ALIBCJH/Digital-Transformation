"""
Seed Central Region Demo Data
==============================

Creates the organizational hierarchy:
- Central Region (Root for demo)
  ├── Nyeri (Sub-Region)
  │   ├── Main Altar
  │   └── Gatito Altar
  ├── Mweiga (Sub-Region)
  │   └── Mweiga Altar
  ├── Karatina (Sub-Region)
  │   └── Karatina Altar
  ├── Chaka (Sub-Region)
  │   └── Chaka Altar
  ├── MUKURWE-INI (Sub-Region)
  │   └── Mukurwe-ini Altar
  └── Kieni (Sub-Region)
      └── Kieni Altar

Usage:
    python manage.py seed_central_region
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Altar, OrganizationNode, User


class Command(BaseCommand):
    help = "Seed Central Region organizational structure for demo"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🌱 Seeding Central Region Demo Data...\n")
        )

        # =============================================
        # 1. CREATE ROOT NODE: CENTRAL REGION
        # =============================================
        central_region, created = OrganizationNode.objects.get_or_create(
            code="CENTRAL",
            defaults={
                "name": "Central Region",
                "parent": None,  # Root node
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Created: {central_region.name}"))
        else:
            self.stdout.write(
                self.style.WARNING(f"→ Already exists: {central_region.name}")
            )

        # =============================================
        # 2. CREATE SUB-REGIONS
        # =============================================
        sub_regions_data = [
            ("NYERI", "Nyeri"),
            ("MWEIGA", "Mweiga"),
            ("KARATINA", "Karatina"),
            ("CHAKA", "Chaka"),
            ("MUKURWEINI", "MUKURWE-INI"),
            ("KIENI", "Kieni"),
        ]

        sub_regions = {}

        self.stdout.write("\n📍 Creating Sub-Regions:")
        for code, name in sub_regions_data:
            sub_region, created = OrganizationNode.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "parent": central_region,
                },
            )
            sub_regions[code] = sub_region

            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"  → {name} (exists)"))

        # =============================================
        # 3. CREATE ALTARS
        # =============================================
        altars_data = [
            # Nyeri has 2 altars
            ("NYERI_MAIN", "Nyeri Main Altar", "NYERI", "Nyeri Town", -0.4197, 36.9489),
            ("NYERI_GATITO", "Gatito Altar", "NYERI", "Gatito", -0.4300, 36.9600),
            # Other sub-regions have 1 altar each
            ("MWEIGA_001", "Mweiga Altar", "MWEIGA", "Mweiga", -0.3167, 36.9833),
            (
                "KARATINA_001",
                "Karatina Altar",
                "KARATINA",
                "Karatina",
                -0.4833,
                37.1333,
            ),
            ("CHAKA_001", "Chaka Altar", "CHAKA", "Chaka", -0.3500, 37.0000),
            (
                "MUKURWEINI_001",
                "Mukurwe-ini Altar",
                "MUKURWEINI",
                "Mukurwe-ini",
                -0.4667,
                37.0167,
            ),
            ("KIENI_001", "Kieni Altar", "KIENI", "Kieni", -0.3000, 37.0500),
        ]

        self.stdout.write("\n⛪ Creating Altars:")
        for code, name, parent_code, city, lat, lng in altars_data:
            altar, created = Altar.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "parent_node": sub_regions[parent_code],
                    "city": city,
                    "latitude": lat,
                    "longitude": lng,
                    "is_active": True,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ {name} ({city})"))
            else:
                self.stdout.write(self.style.WARNING(f"  → {name} (exists)"))

        # =============================================
        # 4. UPDATE NODE STATISTICS
        # =============================================
        self.stdout.write("\n📊 Updating statistics...")

        for sub_region in sub_regions.values():
            altar_count = sub_region.altars.filter(is_active=True).count()
            sub_region.total_altars = altar_count
            sub_region.save()

        # Update Central Region stats
        central_region.total_altars = Altar.objects.filter(
            parent_node__in=sub_regions.values(), is_active=True
        ).count()
        central_region.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"  ✓ Central Region: {central_region.total_altars} altars"
            )
        )

        # =============================================
        # 5. CREATE DEMO ADMIN USERS
        # =============================================
        self.stdout.write("\n👤 Creating demo admin users...")

        # Central Region Admin (sees all 6 sub-regions)
        central_admin, created = User.objects.get_or_create(
            username="central_admin",
            defaults={
                "email": "central@example.com",
                "first_name": "Central",
                "last_name": "Administrator",
                "admin_scope": central_region,
                "is_staff": True,
                "is_superuser": False,
            },
        )
        if created:
            central_admin.set_password("admin123")
            central_admin.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "  ✓ Central Admin (username: central_admin, password: admin123)"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"    Scope: {central_region.name} → Can see all 6 sub-regions"
                )
            )

        # Nyeri Sub-Region Admin (sees only Nyeri + 2 altars)
        nyeri_admin, created = User.objects.get_or_create(
            username="nyeri_admin",
            defaults={
                "email": "nyeri@example.com",
                "first_name": "Nyeri",
                "last_name": "Administrator",
                "admin_scope": sub_regions["NYERI"],
                "is_staff": True,
                "is_superuser": False,
            },
        )
        if created:
            nyeri_admin.set_password("admin123")
            nyeri_admin.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "  ✓ Nyeri Admin (username: nyeri_admin, password: admin123)"
                )
            )
            self.stdout.write(
                self.style.SUCCESS("    Scope: Nyeri → Can see only Nyeri + 2 altars")
            )

        # =============================================
        # 6. SUMMARY
        # =============================================
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS("✅ CENTRAL REGION DEMO DATA SEEDED SUCCESSFULLY!\n")
        )

        self.stdout.write("📋 Summary:")
        self.stdout.write(f"  • 1 Region: {central_region.name}")
        self.stdout.write(
            "  • 6 Sub-Regions: Nyeri, Mweiga, Karatina, Chaka, MUKURWE-INI, Kieni"
        )
        self.stdout.write("  • 7 Altars: Nyeri (2), Others (1 each)")
        self.stdout.write("  • 2 Demo Admins created")

        self.stdout.write("\n🔑 Login Credentials:")
        self.stdout.write("  Central Admin:")
        self.stdout.write("    Email: central@example.com")
        self.stdout.write("    Password: admin123")
        self.stdout.write("    Scope: Full Central Region")

        self.stdout.write("\n  Nyeri Admin:")
        self.stdout.write("    Email: nyeri@example.com")
        self.stdout.write("    Password: admin123")
        self.stdout.write("    Scope: Nyeri Sub-Region only")

        self.stdout.write("\n🌐 Organizational Path Example:")
        self.stdout.write(f"  {central_region.path}")
        self.stdout.write(f'  {sub_regions["NYERI"].path}')

        altar_example = Altar.objects.filter(code="NYERI_MAIN").first()
        if altar_example:
            self.stdout.write(f"  {altar_example.get_organizational_path()}")

        self.stdout.write("\n" + "=" * 60)
