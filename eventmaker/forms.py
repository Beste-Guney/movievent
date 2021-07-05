from django import forms
from .models import Event, Topic, Post
from moviechoose.models import Movie, MovieTheater, Sessions
from accounts.models import Profile


class TopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': 'Your ideas about the movie...'}
        ),
    )

    class Meta:
        model = Topic
        fields = ['subject', 'message']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]


class DateInput(forms.DateInput):
    input_type = 'date'


class DeterminedEventForm(forms.ModelForm):
    
    class Meta:
        model = Event
        fields = ['name', 'participants', 'movie', 'theater', 'time', 'date']

        widgets = {
            'date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        owner_profile = Profile.objects.get(user=user)
        self.fields['participants'].queryset = owner_profile.friends.all()


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'participants', 'movie', 'theater', 'time', 'date']

        widgets = {
            'date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        owner_profile = Profile.objects.get(user=user)
        self.fields['participants'].queryset = owner_profile.friends.all()
        self.fields['theater'].queryset = MovieTheater.objects.none()
        self.fields['time'].queryset = Sessions.objects.none()

        if 'movie' in self.data:
            try:
                movie_id = int(self.data.get('movie'))
                self.fields['theater'].queryset = MovieTheater.objects.filter(movies__id=movie_id).order_by('name')
                self.fields['time'].queryset = Sessions.objects.filter(movie__id=movie_id)
            except (ValueError, TypeError):
                pass  
        elif self.instance.pk:
            self.fields['theater'].queryset = self.instance.movie.movietheater_set.order_by('name')
            self.fields['time'].queryset = self.instance.movie.sessions_set.order_by('session_times')