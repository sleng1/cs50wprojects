# Generated by Django 4.2.5 on 2023-09-12 04:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0002_comment_comment_comment_commenter_comment_listing"),
    ]

    operations = [
        migrations.AddField(
            model_name="bid",
            name="user",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="user_bids",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="bid",
            name="item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="listing_bids",
                to="auctions.listing",
            ),
        ),
    ]
