# Generated by Django 5.2 on 2025-04-08 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_product_low_stock_threshold'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='low_stock_threshold',
            field=models.IntegerField(default=5),
        ),
    ]
