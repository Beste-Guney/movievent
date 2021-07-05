from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from django.db.models.expressions import Case


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE)
    bio = models.TextField()
    favourite_style = models.CharField(max_length=8, null=True)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add=True)

    def get_friends(self):
        return self.friends.all()
    
    def get_friends_no(self):
        return self.friends.all().count()
    
    def __str__(self):
        return self.user.username


class FriendRequest(models.Model):
    sender = models.ForeignKey(Profile, on_delete=CASCADE, related_name= 'sender')
    receiver = models.ForeignKey(Profile, on_delete=CASCADE, related_name= 'receiver')
    status = models.CharField(max_length=8)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    

