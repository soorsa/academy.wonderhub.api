from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    # AUTH VIEWS
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name = 'login'),
    path('logout/', views.logout_user, name = 'logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('change-password/', views.change_password, name='change-password'),
    path('forgot-password/', views.request_password_reset, name='forgot-password'),
    path('reset-password/', views.set_new_password, name='set-new-password'),

]
