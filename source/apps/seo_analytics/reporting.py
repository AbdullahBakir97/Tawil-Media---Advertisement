"""Turning recorded visits into the few numbers the desk actually asks for.

Every function here takes a window in days and returns plain values, so the
template stays a layout and the view stays a handful of calls.
"""

from datetime import timedelta
from urllib.parse import urlsplit

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from source.apps.content.models import Article

from .models import PageVisit

#: What the range selector offers.
WINDOWS = (7, 30, 90)
DEFAULT_WINDOW = 30


def window_start(days):
    """Midnight, `days` ago — so a range is whole days, not a rolling clock."""
    today = timezone.localtime().date()
    return timezone.make_aware(
        timezone.datetime.combine(today - timedelta(days=days - 1), timezone.datetime.min.time())
    )


def visits_in(days):
    return PageVisit.objects.filter(visit_date__gte=window_start(days))


def daily_series(days):
    """One entry per day in the window, including the days nobody came.

    The gaps matter: a chart drawn only from the days that have rows would
    quietly compress a quiet week into a busy-looking line.
    """
    counted = {
        row["day"]: row["visits"]
        for row in visits_in(days).annotate(day=TruncDate("visit_date"))
        .values("day").annotate(visits=Count("id")).order_by("day")
    }
    first = window_start(days).date()
    return [
        {"date": first + timedelta(days=offset), "visits": counted.get(first + timedelta(days=offset), 0)}
        for offset in range(days)
    ]


def totals(days):
    visits = visits_in(days)
    return {
        "visits": visits.count(),
        # Addresses are already truncated to a network, so this counts
        # neighbourhoods rather than people. Named accordingly in the panel.
        "networks": visits.values("ip_address").distinct().count(),
        "readers": visits.exclude(user=None).values("user").distinct().count(),
    }


def top_pages(days, limit=8):
    """The most-read pages, with an article's headline where the URL is one."""
    rows = list(
        visits_in(days).values("url").annotate(visits=Count("id")).order_by("-visits")[:limit]
    )
    slugs = {
        row["url"].rstrip("/").rsplit("/", 1)[-1]: row["url"]
        for row in rows if "/articles/" in row["url"]
    }
    headlines = {}
    if slugs:
        for article in Article.objects.filter(slug__in=slugs):
            headlines[slugs[article.slug]] = article.label
    for row in rows:
        row["label"] = headlines.get(row["url"]) or row["url"]
    return rows


def top_referrers(days, limit=6):
    """Where readers came from, counted by site rather than by exact link."""
    counted = {}
    for row in visits_in(days).exclude(referrer=None).exclude(referrer="").values_list("referrer", flat=True):
        host = urlsplit(row).netloc.lower().removeprefix("www.")
        if host:
            counted[host] = counted.get(host, 0) + 1
    ordered = sorted(counted.items(), key=lambda pair: -pair[1])[:limit]
    return [{"label": host, "visits": visits} for host, visits in ordered]


def busiest_day(series):
    return max(series, key=lambda day: day["visits"], default=None)


def chart_geometry(series, width=720, height=180, pad=4):
    """The points for an area-and-line chart, computed once here rather than
    in the template, where arithmetic does not belong."""
    if not series:
        return {"points": "", "area": "", "peak": 0, "dots": []}
    peak = max(day["visits"] for day in series) or 1
    step = (width - pad * 2) / max(len(series) - 1, 1)
    dots = [
        {
            "x": round(pad + index * step, 2),
            "y": round(height - pad - (day["visits"] / peak) * (height - pad * 2), 2),
            "date": day["date"],
            "visits": day["visits"],
        }
        for index, day in enumerate(series)
    ]
    # The extreme is the story a traffic chart tells, so mark it for a direct label.
    highest = max(dots, key=lambda dot: dot["visits"])
    for dot in dots:
        dot["is_peak"] = dot is highest and highest["visits"] > 0

    points = " ".join(f"{dot['x']},{dot['y']}" for dot in dots)
    area = f"{pad},{height - pad} {points} {dots[-1]['x']},{height - pad}"
    return {
        "points": points,
        "area": area,
        "peak": peak,
        "peak_dot": highest if highest["visits"] else None,
        "dots": dots,
        "width": width,
        "height": height,
        "baseline_y": height - pad,
        "peak_y": pad,
    }
