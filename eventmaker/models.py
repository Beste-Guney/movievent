from django.db import models
from moviechoose.models import Movie, MovieTheater,Session
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.db.models.fields import DateTimeField,DateField
from accounts.models import Profile
from datetime import date


# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, related_name="host", on_delete=CASCADE)
    participants = models.ManyToManyField(User)
    movie = models.ForeignKey(Movie, related_name="movie_name", on_delete=CASCADE)
    theater = models.ForeignKey(MovieTheater, related_name="movietheater_name", on_delete=CASCADE, null=True)
    time = models.ForeignKey(Session, related_name='session_time', on_delete=CASCADE, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False, null=True)
    slug = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.name
    
    def is_past(self):
        if self.date < date.today():
            return True
        else:
            return False


class EventRequest(models.Model):
    event = models.OneToOneField(Event, on_delete=CASCADE, related_name="event_name")
    participants = models.ManyToManyField(User, related_name='participants')
    created_time = models.DateTimeField(auto_now_add=True)


class Topic(models.Model):
    event = models.ForeignKey(Event, related_name='events', null=True, on_delete=CASCADE)
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    starter = models.ForeignKey(User, related_name='topics', on_delete=CASCADE)

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]


class Post(models.Model):
    message = models.CharField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='posts',on_delete=models.CASCADE)

    def get_message(self):
        return self.message