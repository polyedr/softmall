from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Function',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('code', models.CharField(max_length=64, unique=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('code', models.CharField(max_length=64)),
                ('is_active', models.BooleanField(default=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='accounts.company')),
            ],
        ),
        migrations.AddConstraint(
            model_name='role',
            constraint=models.UniqueConstraint(fields=('company', 'code'), name='uniq_company_role_code'),
        ),
        migrations.CreateModel(
            name='RoleFunction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('active_to', models.DateTimeField(blank=True, null=True)),
                ('function', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='role_bindings', to='rbac.function')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='role_functions', to='rbac.role')),
            ],
        ),
        migrations.AddConstraint(
            model_name='rolefunction',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('active_to__isnull', True)), models.Q(('active_from__lte', models.F('active_to'))), _connector='OR'), name='role_function_active_interval_valid'),
        ),
        migrations.AddConstraint(
            model_name='rolefunction',
            constraint=models.UniqueConstraint(fields=('role', 'function', 'active_from'), name='uniq_role_function_from'),
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('active_to', models.DateTimeField(blank=True, null=True)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_bindings', to='rbac.role')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_roles', to='accounts.user')),
            ],
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('active_to__isnull', True)), models.Q(('active_from__lte', models.F('active_to'))), _connector='OR'), name='user_role_active_interval_valid'),
        ),
    ]
