import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TimezoneDict",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name="PropertyCodeDict",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name="Module",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name="UserProperty",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.JSONField()),
                ("active_from", models.DateTimeField(default=django.utils.timezone.now)),
                ("active_to", models.DateTimeField(blank=True, null=True)),
                (
                    "property_code",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="user_values",
                        to="catalogs.propertycodedict",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="properties", to="accounts.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CompanyProperty",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.JSONField()),
                ("active_from", models.DateTimeField(default=django.utils.timezone.now)),
                ("active_to", models.DateTimeField(blank=True, null=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="properties", to="accounts.company"
                    ),
                ),
                (
                    "property_code",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="company_values",
                        to="catalogs.propertycodedict",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CompanyModuleLicense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("active_from", models.DateTimeField(default=django.utils.timezone.now)),
                ("active_to", models.DateTimeField(blank=True, null=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="module_licenses",
                        to="accounts.company",
                    ),
                ),
                (
                    "module",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="company_licenses",
                        to="catalogs.module",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="userproperty",
            constraint=models.UniqueConstraint(
                fields=("user", "property_code", "active_from"), name="uniq_user_prop_from"
            ),
        ),
        migrations.AddConstraint(
            model_name="userproperty",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("active_to__isnull", True)),
                    models.Q(("active_from__lte", models.F("active_to"))),
                    _connector="OR",
                ),
                name="user_prop_active_interval_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="companyproperty",
            constraint=models.UniqueConstraint(
                fields=("company", "property_code", "active_from"), name="uniq_company_prop_from"
            ),
        ),
        migrations.AddConstraint(
            model_name="companyproperty",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("active_to__isnull", True)),
                    models.Q(("active_from__lte", models.F("active_to"))),
                    _connector="OR",
                ),
                name="company_prop_active_interval_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="companymodulelicense",
            constraint=models.UniqueConstraint(
                fields=("company", "module", "active_from"), name="uniq_company_module_from"
            ),
        ),
        migrations.AddConstraint(
            model_name="companymodulelicense",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("active_to__isnull", True)),
                    models.Q(("active_from__lte", models.F("active_to"))),
                    _connector="OR",
                ),
                name="company_module_active_interval_valid",
            ),
        ),
    ]
