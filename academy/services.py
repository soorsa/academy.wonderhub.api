import requests
from django.conf import settings
from .models import *

def send_email(to, subject, html):
    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [to],
        "subject": subject,
        "html": html,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Email sending failed:", str(e))
        return None


def handle_course_enrollment(tx: Transaction):
    """Creates or activates an enrollment once payment succeeds."""
    meta = tx.metadata
    course = Course.objects.get(id=meta["course_id"])

    # Use student if logged in, otherwise match by guest email + course
    lookup = {"student": tx.user, "course": course} if tx.user else {"email": meta["email"], "course": course}

    Enrollment.objects.update_or_create(
        **lookup,
        defaults={
            "transaction": tx,
            "fullname": meta.get("fullname"),
            "email": meta.get("email"),
            "phone_number": meta.get("phone_number"),
            "amount_paid": tx.amount,
            "is_active": True,
        },
    )


def handle_wallet_deposit(tx: Transaction):
    """Example handler for wallet funding."""
    wallet = tx.user.wallet
    wallet.balance += tx.amount
    wallet.save(update_fields=["balance"])


# Map metadata["purpose"] to its handler
PAYMENT_HANDLERS = {
    "course_enrollment": handle_course_enrollment,
    "wallet_deposit": handle_wallet_deposit,
}
