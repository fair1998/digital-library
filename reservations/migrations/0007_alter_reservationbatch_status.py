from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0006_alter_reservation_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservationbatch',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('confirmed', 'Confirmed'),
                    ('completed', 'Completed'),
                    ('expired', 'Expired'),
                    ('cancelled', 'Cancelled'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
