from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    listing_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_listings")
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=1000)
    starting_bid = models.DecimalField(max_digits=20, decimal_places=2)
    image = models.URLField(default=None)
    category = models.CharField(max_length=64, default=None)
    listing_watchlist = models.ManyToManyField(User, blank=True, related_name="user_watchlist")
    is_closed = models.BooleanField(default=False)

class Bid(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT, related_name="user_bids")
    item = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name="listing_bids")
    price = models.DecimalField(max_digits=20, decimal_places=2)

class Comment(models.Model):
    commenter = models.ForeignKey(User, default=None, on_delete=models.PROTECT, related_name="user_comments")
    listing = models.ForeignKey(Listing, default=None, on_delete=models.PROTECT, related_name="listing_comments")
    comment = models.CharField(max_length=200, blank=True)