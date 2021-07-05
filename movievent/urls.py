"""movievent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from moviechoose import views as movieChooseViews
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
import notifications.urls

urlpatterns = [
    path('', movieChooseViews.MainPageView.as_view(), name='main'),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('notification_read/<int:notification_id>', movieChooseViews.NotificationUpdate.as_view(), name='notification_view'),
    path('account/', include('accounts.urls')),
    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('info/', include('moviechoose.urls')),
    path('event/', include('eventmaker.urls')),
    path('recommend/', include('movie_recommend.urls')),
    path('admin/', admin.site.urls),
    path('rate/', movieChooseViews.rate_movie, name='rate_movie'),
    path('reset/',auth_views.PasswordResetView.as_view(template_name='password_reset.html',email_template_name='password_reset_email.html',subject_template_name='password_reset_subject.txt'),name='password_reset'),
    path('reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),name='password_reset_done'),
    re_path('reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset/complete/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),name='password_reset_complete'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)