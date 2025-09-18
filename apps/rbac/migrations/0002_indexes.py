from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [("rbac", "0001_initial")]

    operations = [
        migrations.AddIndex(
            model_name="userrole",
            index=models.Index(fields=["user", "active_from"], name="ix_userrole_user_from"),
        ),
        migrations.AddIndex(
            model_name="rolefunction",
            index=models.Index(fields=["role", "function", "active_from"], name="ix_rolefunc_role_fn_from"),
        ),
        # Частичный индекс на привязки роли, Postgres
        migrations.AddIndex(
            model_name="rolefunction",
            index=models.Index(
                name="ix_rolefunc_active_now",
                fields=["role", "function"],
                condition=Q(active_to__isnull=True),
            ),
        ),
    ]
