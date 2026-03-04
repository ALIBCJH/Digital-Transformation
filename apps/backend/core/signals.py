"""
Signals for automatic bootstrap and data integrity
"""
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps


@receiver(post_migrate)
def create_default_organization_structure(sender, **kwargs):
    """
    Post-migrate signal to optionally create a default root organization node.
    This ensures the app has a minimal viable structure on first deploy.
    
    NOTE: This creates a "fallback" structure only if NO OrganizationNodes exist.
    Users can create their own custom structures through signup.
    """
    if sender.name != 'core':
        return

    # Import models here to avoid circular imports
    OrganizationNode = apps.get_model('core', 'OrganizationNode')
    
    # Only create if absolutely no nodes exist
    if OrganizationNode.objects.count() == 0:
        print("\n🏗️  Creating default root organization node...")
        root = OrganizationNode.objects.create(
            name="Global Root",
            code="GLOBAL",
            depth=0,
            path="/GLOBAL/",
            is_active=True
        )
        print(f"✅ Created root node: {root.name} (ID: {root.id})")
        print("   Users can now create their own altar hierarchies during signup.\n")
    else:
        print(f"✅ Organization structure exists ({OrganizationNode.objects.count()} nodes)")
