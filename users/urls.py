"""wonderhub_stack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from fileinput import hook_encoded
from django.urls import path, include
from django.contrib.auth import views as login_views
from allauth.account import views as allauth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views


urlpatterns = [

    # AUTH VIEWS
    path('register/', views.Registration, name='register'),
    path('accounts/', include('allauth.urls')),
    path('login/', allauth_views.LoginView.as_view(template_name='users/login.html'), name = 'login'),
    path('logout/', allauth_views.LogoutView.as_view(template_name='users/logout.html'), name = 'logout'),
]
