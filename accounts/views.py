from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, views
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from .models import FriendRequest, Profile
from moviechoose.models import Movie, MovieTheater
from .forms import ProfileForm
from django.utils.decorators import method_decorator
from notifications.signals import notify
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginView(views.LoginView):
    def get(self, request):
        return super().get(request)    

    def post(self, request):
        # get posted data
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        # handle user authentication
        if user is not None and user.is_active and user.is_authenticated:
            login(request, user)
            # move user to main page
            return redirect('main')


class SignUpView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'signup.html', {'form':form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main')
        else:
            return render(request, 'signup.html', {'form':form})


class AccountView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request, user_id):
        receiver = User.objects.get(id = user_id)
        profile_receiver = Profile.objects.get(user=receiver)
        
        sender = request.user
        profile_sender = Profile.objects.get(user=sender)
        is_self = False
        is_friends = False

        # deciding if they are friends or itself
        if sender.id == receiver.id:
            is_self = True
        else:
            for receive in profile_sender.get_friends():
                if receiver.id == receive.id:
                    is_friends = True

        is_there_request = False
        is_there_invitation = False
        friend_request1 = None
        friend_request2 = None

        try:
            friend_request1 = FriendRequest.objects.get(sender=profile_sender, receiver=profile_receiver)
            is_there_request = True
        except FriendRequest.DoesNotExist:
            is_there_request = False
            
        try:
            friend_request2 = FriendRequest.objects.get(sender=profile_receiver, receiver=profile_sender)
            is_there_invitation = True
        except FriendRequest.DoesNotExist:
            is_there_invitation = False

        context = {'profile': profile_receiver, 'receiver': receiver, 'profile_sender': profile_sender,
                   'profile_receiver': profile_receiver, 'sender': sender, 'is_self': is_self, 'is_friends': is_friends,
                   'is_there_request': is_there_request, 'is_there_invitation': is_there_invitation,
                   'friend_request1': friend_request1, 'friend_request2': friend_request2
        }
        return render(request, 'profile.html', context)


class SearchView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        query = request.GET.get('search')
        if query:
            users = User.objects.filter(username__contains=query)
            movies = Movie.objects.filter(title__contains=query)
            theaters = MovieTheater.objects.filter(name__contains=query)
        return render(request, 'searchProfile.html', {'users': users, 'movies': movies, 'theaters': theaters})


class FriendListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    model = Profile
    context_object_name = 'friends'
    paginate_by = 30
    template_name = 'friendlist.html'

    def get_queryset(self):
        user_id = self.kwargs['user_id'] 
        user = User.objects.get(id=user_id)
        user_profile = Profile.objects.get(user=user)
        return user_profile.get_friends()


class UpdateProfileView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        form = ProfileForm()
        return render(request, 'updateProfile.html', {'form': form, 'user': request.user})
    
    def post(self, request):
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            profile.bio = form.cleaned_data['bio']
            profile.favourite_style = form.cleaned_data['favourite_style']
            profile.save()
        return redirect('myprofile')


class MyProfileView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        user = request.user
        profile_user = Profile.objects.get(user=user)
        return render(request, 'mypage.html', {'profile_user':profile_user})


class SendFriendRequestView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request, user_id):
        sender = request.user
        profile_sender = Profile.objects.get(user=sender)
        receiver = User.objects.get(id=user_id)
        profile_receiver = Profile.objects.get(user=receiver)
        friend_request = FriendRequest.objects.create(sender=profile_sender, receiver=profile_receiver)

        # notification area
        sender = request.user
        message = 'You have an friend request from ' + sender.username
        notify.send(sender=sender, recipient=receiver, verb='Message', description=message, type='friend')
        return redirect('profile', receiver.id)


class AcceptFriendRequestView(LoginRequiredMixin, View):
    def get(self, request, request_id):
        friend_request = FriendRequest.objects.get(id=request_id)
        receiver_profile = friend_request.receiver
        sender_profile = friend_request.sender

        if receiver_profile.user == request.user:
            receiver_profile.friends.add(sender_profile.user)
            sender_profile.friends.add(receiver_profile.user)
            friend_request.delete()
        return redirect('profile', sender_profile.user.id)


class CancelRequestView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request, request_id):
        friend_request = FriendRequest.objects.get(id=request_id)
        receiver_profile = friend_request.receiver

        friend_request.delete()
        return redirect('profile', receiver_profile.user.id)


class DeclineInvitationView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request, request_id):
        friend_request = FriendRequest.objects.get(id=request_id)
        sender_profile = friend_request.sender

        friend_request.delete()
        return redirect('profile', sender_profile.user.id)       


class CancelFriendshipView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request, receiver_id):
        user = request.user
        profile_user = Profile.objects.get(user=user)
        receiver = User.objects.get(id=receiver_id)
        profile_receiver = Profile.objects.get(user=receiver)
        profile_user.friends.remove(receiver)
        profile_receiver.friends.remove(user)
        return redirect('profile', receiver.id)


class FriendRequestView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'
    
    def get(self, request):
        profile_receiver = Profile.objects.get(user=request.user)
        friend_request = FriendRequest.objects.filter(receiver=profile_receiver)
        return render(request, 'friend_request.html', {'friend_request': friend_request})