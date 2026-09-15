import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language
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
        language = (get_language() or "de").split("-")[0]
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email, defaults={"language": language}
        )
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


def unsubscribe(request, token):
    """Leaving the list, from the link in every letter.

    A GET shows a confirmation; only a POST actually unsubscribes, so a mail
    client or a link-scanner fetching the URL cannot remove somebody by
    accident.
    """
    subscriber = get_object_or_404(NewsletterSubscriber, token=token)
    if request.method == "POST":
        if subscriber.is_active:
            subscriber.is_active = False
            subscriber.save(update_fields=["is_active", "updated_at"])
            logger.info("Newsletter unsubscribe for %s", subscriber.email)
        return render(request, "newsletter/unsubscribed.html", {"subscriber": subscriber, "done": True})
    return render(request, "newsletter/unsubscribe.html", {"subscriber": subscriber})


def unsubscribe_info(request):
    """Where the preview's unsubscribe link points, since it has no token."""
    return render(request, "newsletter/unsubscribe.html", {"subscriber": None})
