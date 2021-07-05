from django.urls import path
from . import views as eventView


urlpatterns = [
    path('acceptRequest/<int:request_id>', eventView.AcceptEventRequestView.as_view(), name= 'accept_event_request'),
    path('ajax/load-sessions/', eventView.load_sessions, name='ajax_load_sessions'),
    path('ajax/load-theaters/', eventView.load_theaters, name='ajax_load_theaters'),
    path('cancel_event/<int:event_id>', eventView.CancelEventView.as_view(), name='cancel_event'),
    path('createTopic/<int:event_id>', eventView.CreateTopicView.as_view(), name='create_topic'),
    path('declineEventRequest/<int:request_id>', eventView.DeclineEventRequestView.as_view(),
         name='decline_event_request'),
    path('eventRequest/', eventView.EventRequestView.as_view(), name='event_request'),
    path('leaveEvent/<int:event_id>', eventView.LeaveEventView.as_view(), name='leaveEvent'),
    path('createEvent/', eventView.EventCreationView.as_view(), name="createEvent" ),
    path('createEvent/<slug:movie_name>/<slug:theater_name>/<int:session_id>', eventView.EventCreationView2.as_view(),
         name='create_specific_event'),
    path('upcomingActivity/', eventView.UpcomingEventView.as_view(), name='events'),
    path('pastActivity/', eventView.PastEventView.as_view(), name='past_events'),
    path('pastActivity/<slug:event_name>', eventView.EventView.as_view(), name='past_event_info'),
    path('replyTopic/<int:topic_id>', eventView.ReplyTopicView.as_view(), name='reply_topic'),
    path('upcomingActivity/<slug:event_name>', eventView.EventView.as_view(), name='eventInfo'),
]