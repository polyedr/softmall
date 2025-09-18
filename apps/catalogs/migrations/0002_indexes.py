from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [("catalogs", "0001_initial")]

    operations = [
        migrations.AddIndex(
            model_name="companyproperty",
            index=models.Index(fields=["company", "property_code", "active_from"], name="ix_cprop_company_code_from"),
        ),
        migrations.AddIndex(
            model_name="userproperty",
            index=models.Index(fields=["user", "property_code", "active_from"], name="ix_uprop_user_code_from"),
        ),
        migrations.AddIndex(
            model_name="companymodulelicense",
            index=models.Index(fields=["company", "module", "active_from"], name="ix_cmod_company_mod_from"),
        ),
        migrations.AddIndex(
            model_name="companyproperty",
            index=models.Index(
                name="ix_cprop_active",
                fields=["company", "property_code"],
                condition=Q(active_to__isnull=True),
            ),
        ),
    ]
