# Generated by Django 4.2.7 on 2024-09-26 10:52

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
                ('uz_button', models.CharField(max_length=50, verbose_name='Uzbekcha')),
                ('ru_button', models.CharField(max_length=50, verbose_name='Russia')),
            ],
            options={
                'verbose_name': 'ButtonMod',
                'verbose_name_plural': 'ButtonMods',
            },
        ),
        migrations.CreateModel(
            name='CategoryMod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='holati')),
            ],
            options={
                'verbose_name': 'Holat',
                'verbose_name_plural': 'Holatlar',
            },
        ),
        migrations.CreateModel(
            name='ParentMod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(verbose_name='Telegram ID')),
                ('code', models.CharField(max_length=50, verbose_name='Code')),
                ('parent_name', models.CharField(max_length=100, verbose_name='ФИО')),
                ('school', models.CharField(max_length=100, verbose_name='Maktab')),
                ('class_name', models.CharField(max_length=100, verbose_name='klass')),
                ('city', models.CharField(max_length=100, verbose_name='Tuman')),
                ('parent_number', models.CharField(max_length=100, verbose_name='Telefon rakami')),
                ('payment', models.BooleanField(default=False, verbose_name='Tolov')),
                ('language', models.CharField(max_length=5, verbose_name='Til')),
            ],
            options={
                'verbose_name': 'Ota/Ona',
                'verbose_name_plural': 'Otalar/Onalar',
            },
        ),
        migrations.CreateModel(
            name='save_user_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(blank=True, null=True, verbose_name='Telegram ID')),
                ('who', models.CharField(blank=True, max_length=10, null=True, verbose_name='Qaysi foydalanuvchi')),
                ('school', models.CharField(blank=True, max_length=100, null=True, verbose_name='Maktab')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Tuman')),
                ('class_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='class_name')),
                ('teacher_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='teacher_name')),
                ('student_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='student_name')),
                ('student_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='student_number')),
                ('teacher_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='teacher_number')),
                ('language', models.CharField(blank=True, max_length=5, null=True, verbose_name='Til')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='Code')),
            ],
            options={
                'verbose_name': 'save_user_data',
                'verbose_name_plural': 'save_user_datalar',
            },
        ),
        migrations.CreateModel(
            name='TeacherMod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(verbose_name='Telegram ID')),
                ('code', models.CharField(max_length=50, verbose_name='Code')),
                ('teacher_name', models.CharField(max_length=100, verbose_name='ФИО')),
                ('school', models.CharField(max_length=100, verbose_name='Maktab')),
                ('class_name', models.CharField(max_length=100, verbose_name='klass')),
                ('city', models.CharField(max_length=100, verbose_name='Tuman')),
                ('teacher_number', models.CharField(max_length=100, verbose_name='Telefon rakami')),
                ('payment', models.BooleanField(default=False, verbose_name='Tolov')),
                ('language', models.CharField(max_length=5, verbose_name='Til')),
            ],
            options={
                'verbose_name': 'Uztoz',
                'verbose_name_plural': 'Uztozlar',
            },
        ),
        migrations.CreateModel(
            name='UserMod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, verbose_name='Code')),
                ('telegram_id', models.BigIntegerField(verbose_name='Telegram ID')),
                ('student_name', models.CharField(max_length=100, verbose_name='student_name')),
                ('teacher_name1', models.CharField(max_length=100, verbose_name='teacher_name1')),
                ('school', models.CharField(max_length=100, verbose_name='school')),
                ('class_name', models.CharField(max_length=100, verbose_name='class_name')),
                ('city', models.CharField(max_length=100, verbose_name='Tuman')),
                ('student_number', models.CharField(max_length=100, verbose_name='student_number')),
                ('teacher_number', models.CharField(max_length=100, verbose_name='teacher_number')),
                ('payment', models.BooleanField(default=False, verbose_name='Tolov')),
                ('language', models.CharField(max_length=5, verbose_name='Til')),
                ('parents', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.parentmod', verbose_name='Parents')),
                ('teacher_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.teachermod', verbose_name='Teachers')),
            ],
            options={
                'verbose_name': 'Okuvchi',
                'verbose_name_plural': 'Okuvchilar',
            },
        ),
        migrations.CreateModel(
            name='DescriptionMod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uz_text', models.TextField(verbose_name='Malumot uz')),
                ('ru_text', models.TextField(verbose_name='Malumot ru')),
                ('title', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main_app.categorymod', verbose_name='holat')),
            ],
            options={
                'verbose_name': 'Description',
                'verbose_name_plural': 'Descriptions',
            },
        ),
    ]
