# Generated by Django 4.2.7 on 2024-09-20 23:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ButtonMod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ru_button', models.CharField(max_length=50, verbose_name='Russia')),
                ('uz_button', models.CharField(max_length=50, verbose_name='Uzbekcha')),
            ],
            options={
                'verbose_name': 'ButtonMod',
                'verbose_name_plural': 'ButtonMods',
            },
        ),
        migrations.CreateModel(
            name='CategiryMod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='holat')),
            ],
        ),
        migrations.CreateModel(
            name='save_user_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(blank=True, null=True, verbose_name='Telegram ID')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='ФИО')),
                ('school', models.CharField(blank=True, max_length=100, null=True, verbose_name='Maktab')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Tuman')),
                ('number', models.CharField(blank=True, max_length=100, null=True, verbose_name='Telefon rakami')),
                ('language', models.CharField(blank=True, max_length=5, null=True, verbose_name='Til')),
            ],
        ),
        migrations.CreateModel(
            name='UserMod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(verbose_name='Telegram ID')),
                ('full_name', models.CharField(max_length=100, verbose_name='ФИО')),
                ('school', models.CharField(max_length=100, verbose_name='Maktab')),
                ('city', models.CharField(max_length=100, verbose_name='Tuman')),
                ('number', models.CharField(max_length=100, verbose_name='Telefon rakami')),
                ('payment', models.BooleanField(default=False, verbose_name='Tolov')),
                ('language', models.CharField(max_length=5, verbose_name='Til')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.CreateModel(
            name='DescriptionMod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uz_text', models.TextField(verbose_name='Malumot uz')),
                ('ru_text', models.TextField(verbose_name='Malumot ru')),
                ('title', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main_app.categirymod', verbose_name='holat')),
            ],
        ),
    ]
