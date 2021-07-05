from django.urls import path
from . import views as movieChooseViews


urlpatterns = [
    path('allmovies/', movieChooseViews.MovieView.as_view(), name='allmovies'),
    path('allmovies/<slug:genre>/', movieChooseViews.MovieFilterView.as_view(), name='filter_movies'),
    path('filter/<slug:city_value>/', movieChooseViews.filter_data, name='filtered_data'),
    path('rated_movies/', movieChooseViews.RatedMovieView.as_view(), name='rated_movies'),
    path('review_movie/<slug:movie_name>', movieChooseViews.ReviewView.as_view(), name='review_movie'),
    path('movieTheater/', movieChooseViews.TheatersView.as_view(), name="theaters"),
    path( 'movieTheater/<slug:theater_name>/', movieChooseViews.MovieTheaterView.as_view(), name="theater"),
    path('recommend/', movieChooseViews.RecommendPage.as_view(), name= 'recommend_page'),
    path('recommend_friend/', movieChooseViews.MainPageView.as_view(), name="recommend"),
    path('<slug:movie_name>/', movieChooseViews.SpecificMovieView.as_view(), name='movie'),
]