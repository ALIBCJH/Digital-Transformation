# Generated migration to enable PostgreSQL extensions

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_guest_attendancelog_membertransferhistory_and_more'),
    ]

    operations = [
        TrigramExtension(),
    ]