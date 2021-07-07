from django.contrib import admin
from moviechoose.models import MovieTheater, Movie,Session, Ratings

from eventmaker.models import Event

# Register your models here.
admin.site.register(Event)
admin.site.register(MovieTheater)
admin.site.register(Session)
admin.site.register(Movie)
admin.site.register(Ratings)
