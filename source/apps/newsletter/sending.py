"""Sending an issue.

Two rules matter more than anything else here: an issue is never sent twice,
and one bad address never stops the rest. The first is a status check inside a
row lock; the second is a try around each message.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import transaction
from django.utils import timezone

from .composer import plain_text, render_issue
from .models import Issue

logger = logging.getLogger(__name__)

#: How many messages share one SMTP connection before it is reopened.
BATCH = 50


def _message(issue, subscriber, body_html, body_text, connection):
    message = EmailMultiAlternatives(
        subject=issue.subject,
        body=body_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[subscriber.email],
        connection=connection,
        headers={"List-Unsubscribe": f"<{_unsubscribe(subscriber)}>"},
    )
    message.attach_alternative(body_html, "text/html")
    return message


def _unsubscribe(subscriber):
    from .composer import _absolute

    return _absolute(subscriber.unsubscribe_url())


def send_test(issue, email):
    """One copy to one address, without touching the issue's status."""
    message = EmailMultiAlternatives(
        subject=f"[Test] {issue.subject}",
        body=plain_text(issue),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    message.attach_alternative(render_issue(issue), "text/html")
    message.send(fail_silently=False)
    return 1


def send_issue(issue) -> int:
    """Send the issue to its subscribers. Returns how many messages went out.

    Refuses an issue that has already been sent: the row is re-read and marked
    inside one transaction, so two clicks or two cron runs cannot both send it.
    """
    with transaction.atomic():
        fresh = Issue.objects.select_for_update().get(pk=issue.pk)
        if fresh.status == Issue.SENT:
            logger.info("Issue %s was already sent; not sending again.", issue.pk)
            return 0
        fresh.status = Issue.SENT
        fresh.sent_at = timezone.now()
        fresh.save(update_fields=["status", "sent_at"])

    body_text = plain_text(issue)
    sent = 0
    recipients = list(issue.recipients())

    for start in range(0, len(recipients), BATCH):
        connection = get_connection()
        for subscriber in recipients[start : start + BATCH]:
            try:
                body_html = render_issue(issue, subscriber)
                _message(issue, subscriber, body_html, body_text, connection).send(fail_silently=False)
                sent += 1
            except Exception:
                # One refused address must not cost the rest of the list.
                logger.warning("Could not send issue %s to %s", issue.pk, subscriber.email, exc_info=True)
        connection.close()

    Issue.objects.filter(pk=issue.pk).update(sent_count=sent)
    issue.status, issue.sent_at, issue.sent_count = Issue.SENT, timezone.now(), sent
    logger.info("Issue %s sent to %s of %s subscribers.", issue.pk, sent, len(recipients))
    return sent
