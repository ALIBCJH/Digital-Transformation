from django.core.management.base import BaseCommand

from core.models import OrganizationUnit


class Command(BaseCommand):
    help = 'Seeds the database with Central Region altars and sub-regions'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Central Region organizational structure...')

        # Create continent (Africa)
        africa, created = OrganizationUnit.objects.get_or_create(
            name='Africa',
            level='CONTINENT',
            defaults={'is_active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created continent: {africa.name}'))
        else:
            self.stdout.write(f'- Continent already exists: {africa.name}')

        # Create country (Kenya)
        kenya, created = OrganizationUnit.objects.get_or_create(
            name='Kenya',
            level='COUNTRY',
            parent=africa,
            defaults={'is_active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created country: {kenya.name}'))
        else:
            self.stdout.write(f'- Country already exists: {kenya.name}')

        # Create region - Nyeri Main Altar (serves as both REGION and ALTAR)
        nyeri_region, created = OrganizationUnit.objects.get_or_create(
            name='Nyeri Main Altar',
            level='REGION',
            parent=kenya,
            defaults={'is_active': True}
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created region: {nyeri_region.name}')
            )
        else:
            self.stdout.write(f'- Region already exists: {nyeri_region.name}')

        # Define sub-regions under Nyeri Main Altar
        # Each sub-region is also an altar
        sub_regions = [
            'Mweiga Altar',
            'Karatina Main Altar',
            'Chaka Main Altar',
            'Wamagana Altar',
            'Kieni Altar',
        ]

        # Create sub-regions (which are also altars)
        created_count = 0
        for sub_region_name in sub_regions:
            sub_region, created = OrganizationUnit.objects.get_or_create(
                name=sub_region_name,
                level='SUB_REGION',
                parent=nyeri_region,
                defaults={'is_active': True}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created sub-region: {sub_region_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'- Sub-region already exists: {sub_region_name}'
                    )
                )

            # Also create the altar entry for the same location
            altar, altar_created = OrganizationUnit.objects.get_or_create(
                name=sub_region_name,
                level='ALTAR',
                parent=sub_region,
                defaults={'is_active': True}
            )
            if altar_created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Created altar: {sub_region_name}')
                )
            else:
                self.stdout.write(f'  - Altar already exists: {sub_region_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Seeding completed! '
                f'Created {created_count} new organizational units.'
            )
        )

        # Display summary
        total_regions = OrganizationUnit.objects.filter(level='REGION').count()
        total_sub_regions = OrganizationUnit.objects.filter(level='SUB_REGION').count()
        total_altars = OrganizationUnit.objects.filter(level='ALTAR').count()

        self.stdout.write('\n📊 Database Summary:')
        self.stdout.write(f'  Regions: {total_regions}')
        self.stdout.write(f'  Sub-regions: {total_sub_regions}')
        self.stdout.write(f'  Altars: {total_altars}')
