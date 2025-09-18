from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        # User
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["company", "is_active"],
                name="ix_user_company_active",
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["company", "email"],
                name="ix_user_company_email",
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["company", "date_joined"],
                name="ix_user_company_joined",
            ),
        ),

        # Company
        migrations.AddIndex(
            model_name="company",
            index=models.Index(
                fields=["is_active"],
                name="ix_company_active_flag",
            ),
        ),
        migrations.AddIndex(
            model_name="company",
            index=models.Index(
                fields=["active_from"],
                name="ix_company_active_from",
            ),
        ),
    ]
