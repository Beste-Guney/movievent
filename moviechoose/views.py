import random

from django import template
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.text import slugify
from django.views import View
from django.views.generic import ListView
from django.http import HttpResponse, response, JsonResponse
from .models import MovieTheater, Movie, Ratings, Session, Review, Ratings
from eventmaker.models import Event, EventRequest
from django.core import paginator
from accounts.models import Profile
from django.contrib.auth import user_logged_in
from django.http import JsonResponse
from .forms import ReviewForm
from model_utils.managers import QueryManager
from django.db.models.query import QuerySet
from notifications.models import Notification
from movie_recommend.views import get_recommended_movies, get_distance_between_clusters, get_distance_between_centers, \
    k_means_movie, \
    k_means_my_implementation
from movie_recommend.forms import FriendForm


# Create your views here.
class SpecificMovieView(View):
    def get(self, request, movie_name):
        user_profile = Profile.objects.get(user=request.user)
        movie = Movie.objects.get(slug=movie_name)
        reviews = Review.objects.filter(movie=movie)
        actual_reviews = []

        for r in reviews:
            if user_profile.friends.all().filter(username=r.reviewer.username).exists():
                actual_reviews.append(r)
            elif r.reviewer == request.user:
                actual_reviews.append(r)
        theaters = MovieTheater.objects.filter(movies__title=movie.title)
        sessions = Session.objects.filter(movie=movie)
        ratings = Ratings.objects.filter(rater=request.user, movie=movie)
        if ratings:
            rate = ratings[0]
        else:
            rate = None
        return render(request, "movie.html",
                      {'movie': movie, 'theaters': theaters, 'sessions': sessions, 'reviews': actual_reviews,
                       'ratings': rate, })


class MovieView(ListView):
    model = Movie
    context_object_name = 'movies'
    paginate_by = 30
    template_name = 'includes/movies.html'

    def get_queryset(self):
        movies = Movie.objects.all().order_by('title')
        return movies


class MovieFilterView(ListView):
    model = Movie
    context_object_name = 'movies'
    paginate_by = 30
    template_name = 'includes/movies.html'

    def get_queryset(self, *args, **kwargs):
        genre = self.kwargs['genre']
        if genre == 'horror':
            movies = Movie.objects.filter(genre=27)
        elif genre == 'action':
            movies = Movie.objects.filter(genre=28)
        elif genre == 'comedy':
            movies = Movie.objects.filter(genre=35)
        elif genre == 'romance':
            movies = Movie.objects.filter(genre=10749)
        return movies


class TheatersView(View):
    def get(self, request):
        theaters = MovieTheater.objects.all()
        cities = []

        for t in theaters:
            if t.city not in cities:
                cities.append(t.city)

        return render(request, "all_theaters.html", {'theaters': theaters, 'cities': cities, })


class MovieTheaterView(View):
    def get(self, request, theater_name):
        theater = MovieTheater.objects.get(slug=theater_name)
        return render(request, "theater.html", {'theater': theater})


class MainPageView(View):
    def get(self, request):
        owner = request.user
        owner_profile = Profile.objects.get(user=owner)
        events = Event.objects.all()
        events_of_user = []

        for e in events:
            event_request = EventRequest.objects.get(event=e)
            if (
                    e.participants.filter(id=request.user.id).exists() and
                    not event_request.participants.filter(id=request.user.id).exists()) or e.owner == request.user:
                if not e.is_past():
                    events_of_user.append(e)

        if request.user.is_authenticated:
            recommended_movies = get_recommended_movies(request)

            # form for friend request
            form = FriendForm(user=request.user)
            owner = request.user
            return render(request, 'index.html', {'owner_profile': owner_profile, 'events_of_user': events_of_user,
                                                  'movies': recommended_movies, 'form': form, 'user': owner})
        else:
            return redirect('login')

    def post(self, request):
        form = FriendForm(request.POST, user=request.user)
        if form.is_valid():
            friend = form.cleaned_data['friends']
            center_of_user = k_means_my_implementation(request.user)[1]
            center_of_friend = k_means_my_implementation(friend)[1]
            labels_of_friend = k_means_my_implementation(friend)[0]
            labels_of_user = k_means_my_implementation(request.user)[0]

            recommended_movies = get_distance_between_centers(center_of_user, center_of_friend, labels_of_friend, 3)
            recommendations = []
            movies = []

            for j in range(len(recommended_movies)):
                for i in range(len(recommended_movies[j])):
                    if recommended_movies[j][i] not in labels_of_user[i]:
                        recommendations.append(Movie.objects.get(id=recommended_movies[j][i]))
                        break
            for recom in labels_of_user:
                if recom:
                    random_id = random.choice(recom)
                    movies.append(Movie.objects.get(id=random_id))

            context = {'recommendations': recommendations, 'movies': movies, 'friend': friend}

        return render(request, 're_results2.html', context)


class RecommendPage(View):
    def get(self, request):
        owner = request.user
        recommended_movies = get_recommended_movies(request)
        return render(request, 'recommend_info.html', {'movies': recommended_movies})


def filter_data(request, city_value):
    theaters = MovieTheater.objects.all()
    cities = []

    for t in theaters:
        if not t.city in cities:
            cities.append(t.city)

    theaters = MovieTheater.objects.all().filter(city=city_value)
    return render(request, 'all_theaters.html', {'theaters': theaters, 'cities': cities})


class FilterDataView(View):
    def get(self, request):
        filter_category = self.request.GET.get("filter_category")
        theater_set = MovieTheater.objects.filter(city=filter_category)
        return render(request, 'all_theaters.html', {'theaters': theater_set})


class ReviewView(View):
    def get(self, request, movie_name):
        form = ReviewForm()
        return render(request, 'topic_write.html', {'form': form})

    def post(self, request, movie_name):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(slug=movie_name)

        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.reviewer = request.user
            review.save()

        return redirect('movie', movie.slug)


class RatedMovieView(ListView):
    model = Movie
    context_object_name = 'movies'
    paginate_by = 30
    template_name = 'includes/movies.html'

    def get_queryset(self):
        ratings = Ratings.objects.filter(rater=self.request.user)

        movies = []
        for r in ratings:
            movies.append(r.movie)
        return movies


class NotificationUpdate(View):
    def get(self, request, notification_id):
        notification = Notification.objects.get(id=notification_id)
        notification.unread = 0
        notification.save()
        if notification.description == 'Event Request':
            return redirect('event_request')
        else:
            return redirect('friend_requests')


def rate_movie(request):
    if request.method == 'POST':
        el_id = request.POST.get('el_id')
        val = request.POST.get('val')
        movie = Movie.objects.get(id=el_id)

        rate = Ratings.objects.filter(movie=movie, rater=request.user)
        if rate:
            rate[0].score = val
            rate[0].save()
        else:
            rating = Ratings.objects.create(score=val, movie=movie, rater=request.user)
            rating.save()
        return JsonResponse({'success': 'true', 'score': val}, safe=False)
    return JsonResponse({'success': 'false'})


