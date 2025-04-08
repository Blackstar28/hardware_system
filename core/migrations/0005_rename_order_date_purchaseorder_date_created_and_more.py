# Generated by Django 5.2 on 2025-04-08 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_purchaseorder_supplier_delivery_deliveryitem_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaseorder',
            old_name='order_date',
            new_name='date_created',
        ),
        migrations.RenameField(
            model_name='purchaseorderitem',
            old_name='quantity_ordered',
            new_name='quantity',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='is_fulfilled',
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='status',
            field=models.CharField(default='Pending', max_length=20),
        ),
        migrations.AddField(
            model_name='purchaseorderitem',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
