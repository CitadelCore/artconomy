# Generated by Django 3.0.4 on 2020-03-15 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0089_deliverable_data_copy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lineitem',
            name='order',
        ),
        migrations.RemoveField(
            model_name='order',
            name='adjustment_expected_turnaround',
        ),
        migrations.RemoveField(
            model_name='order',
            name='adjustment_revisions',
        ),
        migrations.RemoveField(
            model_name='order',
            name='adjustment_task_weight',
        ),
        migrations.RemoveField(
            model_name='order',
            name='arbitrator',
        ),
        migrations.RemoveField(
            model_name='order',
            name='auto_finalize_on',
        ),
        migrations.RemoveField(
            model_name='order',
            name='characters',
        ),
        migrations.RemoveField(
            model_name='order',
            name='commission_info',
        ),
        migrations.RemoveField(
            model_name='order',
            name='details',
        ),
        migrations.RemoveField(
            model_name='order',
            name='dispute_available_on',
        ),
        migrations.RemoveField(
            model_name='order',
            name='disputed_on',
        ),
        migrations.RemoveField(
            model_name='order',
            name='escrow_disabled',
        ),
        migrations.RemoveField(
            model_name='order',
            name='expected_turnaround',
        ),
        migrations.RemoveField(
            model_name='order',
            name='final_uploaded',
        ),
        migrations.RemoveField(
            model_name='order',
            name='paid_on',
        ),
        migrations.RemoveField(
            model_name='order',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='order',
            name='revisions',
        ),
        migrations.RemoveField(
            model_name='order',
            name='revisions_hidden',
        ),
        migrations.RemoveField(
            model_name='order',
            name='started_on',
        ),
        migrations.RemoveField(
            model_name='order',
            name='status',
        ),
        migrations.RemoveField(
            model_name='order',
            name='stream_link',
        ),
        migrations.RemoveField(
            model_name='order',
            name='table_order',
        ),
        migrations.RemoveField(
            model_name='order',
            name='task_weight',
        ),
        migrations.RemoveField(
            model_name='order',
            name='trust_finalized',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payout_sent',
        ),
        migrations.RemoveField(
            model_name='revision',
            name='order',
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='deliverable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='sales.Deliverable'),
        ),
        migrations.AlterField(
            model_name='revision',
            name='deliverable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Deliverable'),
        ),
    ]
