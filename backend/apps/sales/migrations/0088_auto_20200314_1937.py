# Generated by Django 3.0.4 on 2020-03-15 00:37

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0097_auto_20200317_1659'),
        ('sales', '0087_auto_20200417_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineitem',
            name='destination_account',
            field=models.IntegerField(choices=[(300, 'Credit Card'), (301, 'Bank Account'), (302, 'Escrow'), (303, 'Finalized Earnings, available for withdraw'), (304, 'Contingency reserve'), (305, 'Unannotated earnings'), (306, 'Card transaction fees'), (307, 'Other card fees'), (407, 'Cash deposit'), (308, 'ACH Transaction fees'), (309, 'Other ACH fees'), (310, 'Tax staging'), (311, 'Tax')]),
        ),
        migrations.AlterField(
            model_name='product',
            name='owner',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_sales_product', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='primary_submission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='featured_sample_for', to='profiles.Submission'),
        ),
        migrations.AlterField(
            model_name='product',
            name='samples',
            field=models.ManyToManyField(blank=True, related_name='is_sample_for', to='profiles.Submission'),
        ),
        migrations.AlterField(
            model_name='product',
            name='starting_price',
            field=djmoney.models.fields.MoneyField(blank=True, db_index=True, decimal_places=2, default_currency='USD', max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='revision',
            name='owner',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_sales_revision', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='transactionrecord',
            name='category',
            field=models.IntegerField(choices=[(400, 'Artconomy Service Fee'), (401, 'Escrow hold'), (402, 'Escrow release'), (403, 'Escrow refund'), (404, 'Subscription dues'), (405, 'Refund for subscription dues'), (406, 'Cash withdrawal'), (408, 'Third party fee'), (409, 'Premium service bonus'), (410, 'Internal Transfer'), (411, 'Third party refund'), (412, 'Correction'), (414, 'Tax'), (416, 'Manual Payout')], db_index=True),
        ),
        migrations.AlterField(
            model_name='transactionrecord',
            name='destination',
            field=models.IntegerField(choices=[(300, 'Credit Card'), (301, 'Bank Account'), (302, 'Escrow'), (303, 'Finalized Earnings, available for withdraw'), (304, 'Contingency reserve'), (305, 'Unannotated earnings'), (306, 'Card transaction fees'), (307, 'Other card fees'), (407, 'Cash deposit'), (308, 'ACH Transaction fees'), (309, 'Other ACH fees'), (310, 'Tax staging'), (311, 'Tax')], db_index=True),
        ),
        migrations.AlterField(
            model_name='transactionrecord',
            name='source',
            field=models.IntegerField(choices=[(300, 'Credit Card'), (301, 'Bank Account'), (302, 'Escrow'), (303, 'Finalized Earnings, available for withdraw'), (304, 'Contingency reserve'), (305, 'Unannotated earnings'), (306, 'Card transaction fees'), (307, 'Other card fees'), (407, 'Cash deposit'), (308, 'ACH Transaction fees'), (309, 'Other ACH fees'), (310, 'Tax staging'), (311, 'Tax')], db_index=True),
        ),
        migrations.CreateModel(
            name='Deliverable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'New'), (2, 'Payment Pending'), (3, 'Queued'), (4, 'In Progress'), (5, 'Review'), (6, 'Cancelled'), (7, 'Disputed'), (8, 'Completed'), (9, 'Refunded')], db_index=True, default=1)),
                ('revisions', models.IntegerField(default=0)),
                ('revisions_hidden', models.BooleanField(default=True)),
                ('final_uploaded', models.BooleanField(default=False)),
                ('payout_sent', models.BooleanField(default=False, db_index=True)),
                ('details', models.CharField(max_length=5000)),
                ('commission_info', models.TextField(default='', blank=True)),
                ('adjustment_expected_turnaround', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('adjustment_task_weight', models.IntegerField(default=0)),
                ('adjustment_revisions', models.IntegerField(default=0)),
                ('task_weight', models.IntegerField(default=0)),
                ('escrow_disabled', models.BooleanField(db_index=True, default=False)),
                ('trust_finalized', models.BooleanField(db_index=True, default=False)),
                ('table_order', models.BooleanField(db_index=True, default=False)),
                ('expected_turnaround', models.DecimalField(decimal_places=2, default=0, help_text='Number of days completion is expected to take.', max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('disputed_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('started_on', models.DateTimeField(blank=True, null=True)),
                ('paid_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('dispute_available_on', models.DateField(blank=True, null=True)),
                ('auto_finalize_on', models.DateField(blank=True, db_index=True, null=True)),
                ('stream_link', models.URLField(blank=True, default='')),
                ('rating', models.IntegerField(choices=[(0, 'Clean/Safe for work'), (1, 'Risque/mature, not adult content but not safe for work'), (2, 'Adult content, not safe for work'), (3, 'Offensive/Disturbing to most viewers, not safe for work')], db_index=True, default=0, help_text='The desired content rating of this piece.')),
                ('arbitrator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cases_new', to=settings.AUTH_USER_MODEL)),
                ('characters', models.ManyToManyField(blank=True, to='profiles.Character')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Order', related_name='deliverables')),
            ],
        ),
        migrations.AddField(
            model_name='lineitem',
            name='deliverable',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='sales.Deliverable'),
        ),
        migrations.AddField(
            model_name='revision',
            name='deliverable',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='sales.Deliverable'),
        ),
    ]
