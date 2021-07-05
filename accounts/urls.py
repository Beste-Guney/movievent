from django.urls import path
from . import views as account_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('addFriend/<int:request_id>', account_views.AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('cancelFriend/<int:receiver_id>', account_views.CancelFriendshipView.as_view(), name='cancel_friendship'),
    path('cancel_request/<int:request_id>', account_views.CancelRequestView.as_view(), name='cancel_request'),
    path('declineInvitation/<int:request_id>', account_views.DeclineInvitationView.as_view(), name='decline_invitation'),
    path('friendlist/<int:user_id>', account_views.FriendListView.as_view(), name='friendlist'),
    path('friend_requests/', account_views.FriendRequestView.as_view(), name='friend_requests'),
    path('signup/', account_views.SignUpView.as_view(), name='signup'),
    path('myaccount/', account_views.MyProfileView.as_view(), name='myprofile'),
    path('results/', account_views.SearchView.as_view(), name='search'),
    path('send_request/<int:user_id>',account_views.SendFriendRequestView.as_view(), name='send_request'),
    path('profile/<int:user_id>', account_views.AccountView.as_view(), name='profile'),
    path('updateProfile/', account_views.UpdateProfileView.as_view(), name='update_profile'),

]