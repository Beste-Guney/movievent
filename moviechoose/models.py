from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class Movie(models.Model):
    original_title = models.CharField(max_length=500, null=True)
    title = models.CharField(max_length=500)
    genre = models.IntegerField(blank=True, null=True)
    overview = models.CharField(max_length=1000, null=True)
    poster_path = models.CharField(max_length=500, null=True)
    slug = models.CharField(max_length=500, null=True)
    release_date = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.title


class MovieTheater(models.Model):
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=80, null=True)
    movies = models.ManyToManyField(Movie)
    slug = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.name


class Sessions(models.Model):
    movie = models.ManyToManyField('Movie')
    theater = models.ManyToManyField('MovieTheater')
    session_times = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.session_times


class Review(models.Model):
    movie = models.ForeignKey(Movie, related_name='movie', null=True, on_delete=CASCADE)
    subject = models.CharField(max_length=255)
    idea_on_movie = models.CharField(max_length=1000)
    last_updated = models.DateTimeField(auto_now_add=True)
    reviewer = models.ForeignKey(User, related_name='reviewer', on_delete=CASCADE)


class Ratings(models.Model):
    movie = models.ForeignKey(Movie, related_name='movie_rating', null= True, on_delete=CASCADE)
    score = models.IntegerField(default=0, validators=[
        MaxValueValidator(5),
        MinValueValidator(0),
        ]
    )
    rater = models.ForeignKey(User, related_name='movie_rater', null=True,on_delete=CASCADE)
    def __str__(self):
        return str(self.pk)
