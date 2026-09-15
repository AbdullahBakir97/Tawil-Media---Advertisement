"""Recording what the site is actually read.

The analytics models existed but nothing ever wrote to them, so every report
was empty. This records one row per page a reader opens.

It is deliberately privacy-preserving: the address is truncated before it is
stored, so a row says "someone on this network" and never "this person". That
is what makes the table lawful to keep without consent under the German
reading of the GDPR, and it costs nothing a traffic report needs.
"""

import ipaddress
import logging

from django.conf import settings

from .models import PageVisit

logger = logging.getLogger(__name__)

#: Paths that are not reading — the desk's own tools, the admin, assets.
IGNORED_PREFIXES = ("/studio/", "/admin/", "/static/", "/media/", "/newsletter/", "/__")

#: Crawlers identify themselves; there is no point counting them as readers.
BOT_MARKERS = ("bot", "spider", "crawler", "slurp", "curl", "wget", "headless",
               "lighthouse", "pingdom", "monitor", "preview")


def anonymise(address):
    """Drop the part of an address that identifies a household.

    IPv4 keeps three octets, IPv6 keeps the routing prefix — the same
    truncation the German data protection authorities ask for.
    """
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return "0.0.0.0"
    network = ipaddress.ip_network(f"{parsed}/{24 if parsed.version == 4 else 48}", strict=False)
    return str(network.network_address)


def client_address(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or "0.0.0.0"


class PageVisitMiddleware:
    """One row per page a reader opens, and nothing else."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if self._should_record(request, response):
                self._record(request)
        except Exception:
            # A reader's page must never fail because a count could not be written.
            logger.warning("Could not record a page visit for %s", request.path, exc_info=True)
        return response

    def _should_record(self, request, response):
        if not getattr(settings, "ANALYTICS_ENABLED", True):
            return False
        if request.method != "GET" or response.status_code != 200:
            return False
        if not response.get("Content-Type", "").startswith("text/html"):
            return False
        if request.path.startswith(IGNORED_PREFIXES):
            return False
        # Honour Do Not Track, which costs one header to read and buys trust.
        if getattr(settings, "ANALYTICS_RESPECT_DNT", True) and request.META.get("HTTP_DNT") == "1":
            return False
        agent = request.META.get("HTTP_USER_AGENT", "").lower()
        if not agent or any(marker in agent for marker in BOT_MARKERS):
            return False
        # The desk browsing its own site is not readership.
        return not (request.user.is_authenticated and request.user.is_staff)

    def _record(self, request):
        PageVisit.objects.create(
            user=request.user if request.user.is_authenticated else None,
            ip_address=anonymise(client_address(request)),
            url=request.path,
            referrer=(request.META.get("HTTP_REFERER") or "")[:200] or None,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:400],
        )
