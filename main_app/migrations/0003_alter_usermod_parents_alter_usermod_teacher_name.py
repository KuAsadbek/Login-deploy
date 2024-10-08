# Generated by Django 4.2.7 on 2024-10-02 00:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_remove_parentmod_code_remove_teachermod_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermod',
            name='parents',
            field=models.ForeignKey(blank=True, default='None', null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.parentmod', verbose_name='Parents'),
        ),
        migrations.AlterField(
            model_name='usermod',
            name='teacher_name',
            field=models.ForeignKey(blank=True, default='None', null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.teachermod', verbose_name='Teachers'),
        ),
    ]
