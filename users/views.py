from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib.auth import login, authenticate
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Q
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User
# from .serializers import *
# from .filters import *
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from django.http import JsonResponse, HttpResponse
from validate_email import validate_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import *


# REGISTRATION VIEWS.
def Registration(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # user.is_superuser=True
            # user.save()
            email = str(form.cleaned_data.get('email'))
            password = str(form.cleaned_data.get('password1'))

            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, "Registration successful! You are now logged in.")
                return redirect("home")  # Change "home" to your desired redirect URL
    else:
        form = RegisterForm(request.POST)
    return render(request, 'users/register.html', {'form': form})
