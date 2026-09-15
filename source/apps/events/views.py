from django.http import Http404
from django.views.generic import DetailView, TemplateView

from .models import Event


class EventListView(TemplateView):
    """What is coming up, and what has already happened."""

    template_name = "events/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upcoming = list(Event.objects.upcoming().select_related("image"))
        context["next_event"] = upcoming[0] if upcoming else None
        context["upcoming"] = upcoming[1:]
        context["past"] = Event.objects.past().select_related("image")[:9]
        return context


class EventDetailView(DetailView):
    template_name = "events/detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.select_related("image")

    def get_object(self, queryset=None):
        event = super().get_object(queryset)
        if not event.can_be_seen_by(self.request):
            raise Http404
        return event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_preview"] = not self.object.is_published
        context["more"] = Event.objects.upcoming().exclude(pk=self.object.pk)[:3]
        return context
