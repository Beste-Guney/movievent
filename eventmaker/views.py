from django.shortcuts import render, redirect
from django.views import View
from eventmaker.forms import DeterminedEventForm, EventForm, TopicForm, PostForm
from moviechoose.models import Movie, MovieTheater, Sessions
from django.utils.text import slugify
from .models import Event, EventRequest, Post, Topic
from django.utils import timezone
from notifications.signals import notify


# functions for ajax request
def load_theaters(request):
    movie_id = request.GET.get('movie')
    theaters = MovieTheater.objects.filter(movies__id=movie_id)
    return render(request, 'includes/theater_dropdown_list_options.html', {'theaters': theaters})


def load_sessions(request):
    movie_id = request.GET.get('movie')
    sessions = Sessions.objects.filter(movie__id=movie_id).order_by
    return render(request, 'includes/sessions_dropdown_list_options.html', {'sessions': sessions})


def find_past_upcoming_events(request):
    events = Event.objects.all()
    eventsupcoming = []
    eventspast = []

    for e in events:
        event_request = EventRequest.objects.get(event=e)
        if (
                e.participants.filter(id=request.user.id).exists() and
                not event_request.participants.filter(id=request.user.id).exists()) \
                or e.owner == request.user:
            if e.is_past():
                eventspast.append(e)
            else:
                eventsupcoming.append(e)
    return eventspast, eventsupcoming


class UpcomingEventView(View):
    def get(self, request):
        is_past = False
        eventsupcoming = find_past_upcoming_events(request)[1]
        eventspast = find_past_upcoming_events(request)[0]

        return render(request, 'events.html', {'eventsupcoming': eventsupcoming, 'eventspast': eventspast,
                                               'is_past': is_past})


class PastEventView(View):
    def get(self, request):
        is_past = True
        eventsupcoming = find_past_upcoming_events(request)[1]
        eventspast = find_past_upcoming_events(request)[0]

        return render(request, 'events.html', {'eventsupcoming': eventsupcoming, 'eventspast': eventspast,
                                               'is_past': is_past})


class EventRequestView(View):
    def get(self, request):
        event_requests = EventRequest.objects.all()
        requests = []
        for e in event_requests:
            if e.participants.filter(id=request.user.id).exists():
                requests.append(e)
        return render(request, 'event_request.html', {'requests': requests})


class EventView(View):
    def get(self, request, event_name):
        event = Event.objects.get(slug=event_name)
        topics = Topic.objects.filter(event=event)
        topics = topics.order_by('-last_updated')
        is_there_request = EventRequest.objects.get(event=event).participants.filter(id=request.user.id).exists()
        event_request = None
        is_self = False
        if event.owner == request.user:
            is_self = True
        if is_there_request:
            event_request = EventRequest.objects.get(event=event)

        if event.is_past():
            return render(request, 'pastevent.html',
                          {'event': event, 'topics': topics, 'is_there_request': is_there_request,
                           'event_request': event_request, 'event': event, 'is_self': is_self})
        else:
            return render(request, 'upcoming_event.html',
                          {'event': event, 'topics': topics, 'is_there_request': is_there_request,
                           'event_request': event_request, 'event': event, 'is_self': is_self})


def form_helper(request, form):
    if form.is_valid():
        event = form.save(commit=False)
        event.owner = request.user
        event.slug = slugify(event.name)
        event.save()
        event_request = EventRequest.objects.create(event=event)
        form.save_m2m()

        participants = event.participants.all()

        # notification area
        sender = request.user
        list_of_recipients = participants
        message = 'Event Request'
        notify.send(sender=sender, recipient=list_of_recipients, verb='Message', description=message)
        for p in participants:
            event_request.participants.add(p)

    return


class EventCreationView(View):
    def get(self, request):
        form = EventForm(user=request.user)
        owner = request.user
        return render(request, 'makeEvent.html', {'form': form, 'user': owner})

    def post(self, request):
        form = EventForm(request.POST, user=request.user)
        form_helper(request, form)

        return redirect('main')


class EventCreationView2(View):
    def get(self, request, movie_name, theater_name, session_id):
        movie = Movie.objects.get(slug=movie_name)
        session = Sessions.objects.get(id=session_id)
        theater = MovieTheater.objects.get(slug=theater_name)
        owner = request.user
        form = DeterminedEventForm(initial={'movie': movie, 'theater': theater, 'time': session}, user=request.user)
        return render(request, 'makeEvent.html', {'form': form, 'user': owner})

    def post(self, request, movie_name, theater_name, session_id):
        form = DeterminedEventForm(request.POST, user=request.user)
        form_helper(request, form)
        return redirect('main')


class AcceptEventRequestView(View):
    def get(self, request, request_id):
        event_request = EventRequest.objects.get(id=request_id)
        event_request.participants.remove(request.user)
        if not event_request.participants:
            event_request.delete()
        return redirect('eventInfo', event_request.event.slug)


class DeclineEventRequestView(View):
    def get(self, request, request_id):
        event_request = EventRequest.objects.get(id=request_id)
        event = event_request.event
        event_request.participants.remove(request.user)
        event.participants.remove(request.user)
        return redirect('events')


class CancelEventView(View):
    def get(self, request, event_id):
        event = Event.objects.get(id=event_id)
        event_request = EventRequest.objects.get(event=event)
        event.delete()
        event_request.delete()
        return redirect('events')


class LeaveEventView(View):
    def get(self, request, event_id):
        event = Event.objects.get(id=event_id)
        event.participants.remove(request.user)
        return redirect('events')


class CreateTopicView(View):
    def get(self, request, event_id):
        form = TopicForm()
        return render(request, 'topic_write.html', {'form': form})

    def post(self, request, event_id):
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            message = form.cleaned_data['message']
            event = Event.objects.get(id=event_id)
            topic.event = event
            topic.starter = request.user
            topic.save()
            Post.objects.create(message=message, topic=topic, created_by=request.user)

            if event.is_past:
                return redirect('past_event_info', event.slug)
            else:
                return redirect('eventInfo', event.slug)


class ReplyTopicView(View):
    def get(self, request, topic_id):
        form = PostForm()
        topic = Topic.objects.get(id=topic_id)
        return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

    def post(self, request, topic_id):
        form = PostForm(request.POST)
        topic = Topic.objects.get(id=topic_id)
        event = topic.event
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

        if event.is_past:
            return redirect('past_event_info', event.slug)
        else:
            return redirect('event_info', event.slug)
