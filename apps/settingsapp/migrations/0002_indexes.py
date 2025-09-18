from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [("settingsapp", "0001_initial")]

    operations = [
        migrations.AddIndex(
            model_name="settingvalue",
            index=models.Index(fields=["setting", "company", "user", "active_from"], name="ix_setval_keys_from"),
        ),
        migrations.AddIndex(
            model_name="settingvalue",
            index=models.Index(
                name="ix_setval_company_active",
                fields=["setting", "company"],
                condition=Q(active_to__isnull=True),
            ),
        ),
        migrations.AddIndex(
            model_name="settingvalue",
            index=models.Index(
                name="ix_setval_user_active",
                fields=["setting", "user"],
                condition=Q(active_to__isnull=True),
            ),
        ),
    ]
