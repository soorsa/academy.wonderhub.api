from django.template.loader import render_to_string
from academy.services import send_email
import random
import string

def send_forgot_password_email(user, reset_link):
    if user.email:
        context = {
            "name": user.first_name or user.username,
            "link": reset_link
            }
        html = render_to_string(
            "users/forgot_password.html",
            context,
        )
        send_email(to=user.email, subject="Forgot Password 🔒", html=html)

def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))