from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
	    return self.name

class Listing(models.Model):
    STATUS = (
    ('Active', 'Active'),
    ('Not Active', 'Not Active'),
    )

    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)    
    title = models.CharField(max_length=50, null=True)
    description = description = models.TextField(max_length=200, null=True, blank=True)
    current_price = models.FloatField(null=True)
    image = models.ImageField(null=True, blank=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS)
    in_watchlist = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listing-detail', kwargs={'pk': self.pk})

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Bid(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE)
    amount = models.FloatField(null=True)
    winner = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
	    return '{}-{}'.format(self.user.username, str(self.amount))

class Watchlist(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE)

    def __str__(self):
	    return '{}-{}'.format(self.user.username, self.listing.title)

class Comment(models.Model):
    post = models.ForeignKey(Listing, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    content = models.TextField(max_length=160, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
	    return '{}-{}'.format(self.post.title, self.author.username)

    