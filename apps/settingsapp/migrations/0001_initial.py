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
            name="SettingDict",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="SettingValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.JSONField()),
                ("active_from", models.DateTimeField(default=django.utils.timezone.now)),
                ("active_to", models.DateTimeField(blank=True, null=True)),
                (
                    "company",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="settings",
                        to="accounts.company",
                    ),
                ),
                (
                    "setting",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="values",
                        to="settingsapp.settingdict",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="settings",
                        to="accounts.user",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="settingvalue",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("active_to__isnull", True)),
                    models.Q(("active_from__lte", models.F("active_to"))),
                    _connector="OR",
                ),
                name="setting_value_active_interval_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="settingvalue",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("company__isnull", False)), models.Q(("user__isnull", False)), _connector="OR"
                ),
                name="setting_value_has_owner",
            ),
        ),
        migrations.AddConstraint(
            model_name="settingvalue",
            constraint=models.UniqueConstraint(
                fields=("setting", "company", "user", "active_from"), name="uniq_setting_owner_from"
            ),
        ),
    ]
