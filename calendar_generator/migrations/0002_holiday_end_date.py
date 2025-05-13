# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('calendar_generator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='holiday',
            name='end_date',
            field=models.DateField(blank=True, help_text='End date of the holiday (if it spans multiple days)',
                                   null=True),
        ),
        migrations.AlterField(
            model_name='holiday',
            name='date',
            field=models.DateField(help_text='Start date of the holiday'),
        ),
    ]
