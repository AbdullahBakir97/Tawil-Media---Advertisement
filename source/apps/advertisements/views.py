"""The advertising hub: what we sell, what it costs, and the planner that turns a
selection into a request. Server-rendered; the planner posts with HTMX."""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from source.apps.content.models import Magazine

from .forms import CampaignRequestForm
from .models import MediaKit, RateCard

log = logging.getLogger(__name__)


def _hub_context(form=None):
    cards = RateCard.objects.filter(is_active=True)
    return {
        "rate_cards": cards,
        "print_cards": [c for c in cards if c.channel == "print"],
        "digital_cards": [c for c in cards if c.channel == "digital"],
        "social_cards": [c for c in cards if c.channel == "social"],
        "bundle_cards": [c for c in cards if c.channel == "bundle"],
        "media_kit": MediaKit.current(),
        "editions": Magazine.objects.published().select_related("cover_image")[:6],
        "form": form or CampaignRequestForm(),
        "faq_page": "advertise",
        **settings.ADVERTISING_STATS,
        **settings.CONTACT_DETAILS,
    }


class AdvertiseView(TemplateView):
    """`/advertise/` — audience, formats, rate card, planner."""

    template_name = "advertising/hub.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_hub_context())
        return context


def request_campaign(request):
    """Take the planner's selection, store the request, notify the desk."""
    if request.method != "POST":
        return render(request, "advertising/partials/planner_form.html", _hub_context(), status=405)

    form = CampaignRequestForm(request.POST)
    if not form.is_valid():
        return render(request, "advertising/partials/planner_form.html", _hub_context(form), status=400)

    campaign_request = form.save(language=translation.get_language() or "")
    _notify(campaign_request)
    return render(
        request,
        "advertising/partials/planner_done.html",
        {"campaign_request": campaign_request, **settings.CONTACT_DETAILS},
    )


def _notify(campaign_request):
    """Tell the advertising desk. A mail failure must never lose the request."""
    recipient = settings.CONTACT_DETAILS.get("contact_email")
    if not recipient:
        return
    lines = [
        f"{campaign_request.company} ({campaign_request.contact_name})",
        f"{campaign_request.email} {campaign_request.phone}".strip(),
        "",
        *campaign_request.summary_lines(),
        "",
        f"Estimate: {campaign_request.estimate} EUR",
        f"Editions: {', '.join(m.title for m in campaign_request.editions.all()) or '—'}",
        "",
        campaign_request.message or "",
    ]
    try:
        send_mail(
            subject=_("New campaign request: %(company)s") % {"company": campaign_request.company},
            message="\n".join(lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=True,
        )
    except Exception:  # pragma: no cover - the request is already stored
        log.exception("Could not send the campaign request notification")
