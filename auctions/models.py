from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_listings")
    title = models.CharField(max_length=512)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=True)
    image = models.URLField(max_length=200, blank=True)
    active = models.BooleanField()
    starting_price = models.DecimalField(max_digits=19, decimal_places=2)

    CATEGORY_CHOICES = [
    ("COL", 'Collectibles'),
    ("BOK", 'Books'),
    ("ELE", 'Electronics'),
    ("FAS", 'Fashion'),
    ("HOM", 'Home and Garden'),
    ("AUT", 'Auto parts'),
    ("MUS", 'Musical instruments'),
    ("SPO", 'Sporting goods'),
    ("TOY", 'Toys and Hobbies'),
    ("OTH", 'Other'),
    ]
    category = models.CharField(
        max_length=3,
        choices=CATEGORY_CHOICES,
        default="OTH",
    )

    def __str__(self):
        return f"{self.id}: {self.title}, {self.category}, {self.active}"


class Bid(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=True)
    price = models.DecimalField(max_digits=19, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.user}: {self.listing}, {self.price}, {self.created}"


class Comment(models.Model):
    text_comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.user}: {self.listing}, {self.text_comment}, {self.created}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlisted")
    active = models.BooleanField()

    def __str__(self):
        return f"{self.user}: {self.listing}"