# Generated manually for bootstrap-ready architecture

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_add_gin_trigram_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='altar',
            name='parent_node',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='altars',
                to='core.organizationnode',
                db_index=True,
            ),
        ),
    ]
