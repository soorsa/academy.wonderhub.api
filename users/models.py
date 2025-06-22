from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
import os
import email
from email.policy import default
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator,MinValueValidator
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save
from django.shortcuts import reverse
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify
from PIL import Image
from random import randint
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)  # Use email as the primary field
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='student')

    USERNAME_FIELD = 'email'  # Use email for authentication
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Fields required when creating superuser
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"





class BankAccount(models.Model):
    instructor = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_accounts')
    bank = models.CharField(max_length=50, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    

    class Meta:
        verbose_name = ("BankAccount")
        verbose_name_plural = ("BankAccounts")

    def __str__(self):
        return f"{self.instructor}'s {self.bank} bank"

    # def get_absolute_url(self):
    #     return reverse("BankAccount_detail", kwargs={"pk": self.pk})



class Withdrawal(models.Model):
    """Model definition for Withdrawal."""

    # TODO: Define fields here
    STATUS = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField( max_length=50, choices=STATUS)
    date = models.DateTimeField(auto_now=True)
    class Meta:
        """Meta definition for Withdrawal."""

        verbose_name = 'Withdrawal'
        verbose_name_plural = 'Withdrawals'

    def __str__(self):
        """Unicode representation of Withdrawal."""
        return f'{self.status} withdrawal of {self.amount} by {self.instructor}'

    def clean(self):
        if self.instructor.role != 'instructor':
            raise ValidationError("Only instructors can request withdrawals.")