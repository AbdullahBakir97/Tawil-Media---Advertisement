import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .forms import SubscribeForm
from .models import NewsletterSubscriber

logger = logging.getLogger(__name__)


@require_POST
def subscribe(request):
    """Store a newsletter sign-up.

    Answers with an HTML partial for HTMX requests (the footer forms swap it
    into the page) and with JSON otherwise.
    """
    form = SubscribeForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data["email"].lower()
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=["is_active", "updated_at"])
            created = True
        status, message = ("success", "Thanks! You're subscribed.") if created else (
            "info", "You are already subscribed to our newsletter."
        )
        logger.info("Newsletter subscription for %s (%s)", email, status)
        http_status = 200
    else:
        status, message, http_status = "error", "Please enter a valid e-mail address.", 400

    if request.headers.get("HX-Request"):
        # Return 200 so htmx swaps the message in; the status is carried in the markup.
        return render(request, "partials/newsletter_response.html", {"status": status, "message": message})
    return JsonResponse({"status": status, "message": message}, status=http_status)
