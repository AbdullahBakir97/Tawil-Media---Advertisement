"""Studio: the in-site editor for staff. Every page is server-rendered; forms post
with HTMX and swap back the updated panel and preview."""

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import TemplateView

from source.apps.content.models import Article, Magazine, Media
from source.apps.content.workflow import BOARD_ORDER, PUBLISHED, SCHEDULED, STATUS_CHOICES

from .forms import AnnouncementForm, HeroForm, MediaDetailsForm, MediaUploadForm, ThemeForm
from .models import FAQ, AdSlot, Announcement, HeroConfig, Milestone, Partner, Testimonial, Theme
from .services import render_magazine_pages


class StaffOnly(UserPassesTestMixin):
    raise_exception = False

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class DashboardView(StaffOnly, TemplateView):
    template_name = "studio/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            hero=HeroConfig.for_placement("home"),
            themes=Theme.objects.all(),
            announcements=Announcement.objects.all()[:8],
            ad_count=AdSlot.objects.filter(is_active=True).count(),
            partner_count=Partner.objects.filter(is_active=True).count(),
            testimonial_count=Testimonial.objects.filter(is_active=True).count(),
            faq_count=FAQ.objects.filter(is_active=True).count(),
            milestone_count=Milestone.objects.filter(is_active=True).count(),
            desk_open=Article.objects.exclude(status=PUBLISHED).count()
            + Magazine.objects.exclude(status=PUBLISHED).count(),
            media_count=Media.objects.count(),
            media_missing_alt=Media.objects.filter(media_type="image", alt_text="").count(),
            magazines=Magazine.objects.all()[:8],
        )
        return ctx


def _hero_context(request, hero, form=None):
    articles = Article.objects.published().select_related("author").prefetch_related("categories")[:6]
    magazines = list(Magazine.objects.published().select_related("cover_image")[:3])
    return {
        "hero": hero,
        "form": form or HeroForm(instance=hero),
        "featured_articles": articles,
        "header_magazines": magazines,
        "variants": HeroConfig.VARIANTS,
    }


class HeroEditorView(StaffOnly, View):
    """Pick a design, edit the copy, see the result immediately."""

    def get(self, request):
        hero = HeroConfig.for_placement("home")
        return render(request, "studio/hero.html", _hero_context(request, hero))

    def post(self, request):
        hero = HeroConfig.for_placement("home")
        if "variant" in request.POST and len(request.POST) <= 2:  # "Use this design" button
            hero.variant = request.POST["variant"]
            hero.save(update_fields=["variant", "updated_at"])
            if request.headers.get("HX-Request"):
                response = render(request, "studio/partials/hero_preview.html", _hero_context(request, hero))
                response["HX-Trigger"] = "hero-saved"
                return response
            return redirect("studio:hero")
        form = HeroForm(request.POST, request.FILES, instance=hero)
        if form.is_valid():
            hero = form.save()
            messages.success(request, _("Hero saved."))
            if request.headers.get("HX-Request"):
                return render(request, "studio/partials/hero_editor.html", _hero_context(request, hero))
            return redirect("studio:hero")
        if request.headers.get("HX-Request"):
            return render(request, "studio/partials/hero_editor.html", _hero_context(request, hero, form))
        return render(request, "studio/hero.html", _hero_context(request, hero, form))


@method_decorator(xframe_options_sameorigin, name="dispatch")
class HeroPreviewView(StaffOnly, View):
    """Render one variant with the saved config, for the gallery of choices.

    Framed by the Studio, so same-origin framing is allowed here only."""

    def get(self, request, variant):
        hero = HeroConfig.for_placement("home")
        preview = HeroConfig(**{f.name: getattr(hero, f.name) for f in HeroConfig._meta.fields if f.name != "id"})
        preview.variant = variant
        ctx = _hero_context(request, preview)
        ctx["preview_variant"] = variant
        return render(request, "studio/partials/hero_frame.html", ctx)


class ThemeListView(StaffOnly, TemplateView):
    template_name = "studio/themes.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["themes"] = Theme.objects.all()
        ctx["form"] = ThemeForm()
        return ctx


class ThemeEditView(StaffOnly, View):
    def get(self, request, pk=None):
        theme = get_object_or_404(Theme, pk=pk) if pk else None
        return render(request, "studio/theme_form.html", {"form": ThemeForm(instance=theme), "theme": theme})

    def post(self, request, pk=None):
        theme = get_object_or_404(Theme, pk=pk) if pk else None
        form = ThemeForm(request.POST, instance=theme)
        if form.is_valid():
            form.save()
            messages.success(request, _("Theme saved."))
            return redirect("studio:themes")
        return render(request, "studio/theme_form.html", {"form": form, "theme": theme})


class AnnouncementListView(StaffOnly, View):
    def get(self, request):
        return render(
            request,
            "studio/announcements.html",
            {"items": Announcement.objects.all(), "form": AnnouncementForm()},
        )

    def post(self, request):
        pk = request.POST.get("pk")
        instance = get_object_or_404(Announcement, pk=pk) if pk else None
        if request.POST.get("action") == "delete" and instance:
            instance.delete()
            return redirect("studio:announcements")
        form = AnnouncementForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _("Announcement saved."))
            return redirect("studio:announcements")
        return render(request, "studio/announcements.html", {"items": Announcement.objects.all(), "form": form})


class DeskView(StaffOnly, View):
    """The editorial board. Four columns — draft, in review, scheduled, live —
    and one click to move a piece along. Articles and editions share it, because
    the desk plans them together."""

    RECENT_LIVE = 8

    def _columns(self, model):
        columns = []
        for status in BOARD_ORDER:
            items = model.objects.in_status(status)
            if status == PUBLISHED:
                items = items[: self.RECENT_LIVE]
            elif status == SCHEDULED:
                items = items.order_by("scheduled_for")
            columns.append({"status": status, "label": dict(STATUS_CHOICES)[status], "items": list(items)})
        return columns

    def _context(self):
        return {
            "article_columns": self._columns(Article),
            "magazine_columns": self._columns(Magazine),
            "due_now": Article.objects.due().count() + Magazine.objects.due().count(),
            "now": timezone.now(),
        }

    def get(self, request):
        return render(request, "studio/desk.html", self._context())

    def post(self, request):
        """One move per post: to draft, to review, scheduled or live."""
        model = Magazine if request.POST.get("kind") == "magazine" else Article
        item = get_object_or_404(model, pk=request.POST.get("pk"))
        move = request.POST.get("move")

        if move == "draft":
            item.back_to_draft(request.POST.get("note", ""))
        elif move == "review":
            item.send_to_review(request.POST.get("note", ""))
        elif move == "live":
            item.go_live()
        elif move == "schedule":
            when = parse_datetime(request.POST.get("when", "") or "")
            if when is None:
                messages.error(request, _("That date could not be read."))
                return self._respond(request)
            if timezone.is_naive(when):
                when = timezone.make_aware(when)
            item.schedule(when)
        else:
            messages.error(request, _("Unknown move."))
            return self._respond(request)

        messages.success(request, _("“%(title)s” is now %(status)s.") % {
            "title": item.title, "status": item.get_status_display().lower()
        })
        return self._respond(request)

    def _respond(self, request):
        if request.headers.get("HX-Request"):
            return render(request, "studio/partials/desk_board.html", self._context())
        return redirect("studio:desk")


class MediaLibraryView(StaffOnly, View):
    """Every uploaded file in one place: upload, search, and set the alt text,
    the caption, the credit and the focal point of each picture."""

    PER_PAGE = 24

    def _context(self, request, selected=None, form=None):
        items = Media.objects.all()
        query = request.GET.get("q", "").strip()
        kind = request.GET.get("kind", "")
        if query:
            items = items.filter(alt_text__icontains=query) | items.filter(file__icontains=query)
        if kind in dict(Media.MEDIA_TYPE_CHOICES):
            items = items.filter(media_type=kind)
        page = Paginator(items.distinct(), self.PER_PAGE).get_page(request.GET.get("page"))
        visible = list(page.object_list)
        selected = selected or (visible[0] if visible else None)
        return {
            "page_obj": page,
            "items": visible,
            "query": query,
            "kind": kind,
            "kinds": Media.MEDIA_TYPE_CHOICES,
            "selected": selected,
            "form": form or (MediaDetailsForm(instance=selected) if selected else None),
            "upload_form": MediaUploadForm(),
            "total": Media.objects.count(),
        }

    def get(self, request):
        selected = None
        if request.GET.get("pk"):
            selected = get_object_or_404(Media, pk=request.GET["pk"])
        ctx = self._context(request, selected=selected)
        if request.headers.get("HX-Request") and request.GET.get("pk"):
            return render(request, "studio/partials/media_details.html", ctx)
        return render(request, "studio/media.html", ctx)

    def post(self, request):
        if request.POST.get("action") == "upload":
            files = request.FILES.getlist("files")
            if files:
                created = MediaUploadForm().save(files)
                messages.success(request, _("%(count)d file(s) uploaded.") % {"count": len(created)})
            return redirect(f"{reverse('studio:media')}?pk={created[0].pk}" if files else "studio:media")

        item = get_object_or_404(Media, pk=request.POST.get("pk"))
        if request.POST.get("action") == "delete":
            item.delete()
            messages.success(request, _("File deleted."))
            return redirect("studio:media")

        form = MediaDetailsForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            if request.headers.get("HX-Request"):
                response = render(request, "studio/partials/media_details.html", self._context(request, selected=item))
                response["HX-Trigger"] = "media-saved"
                return response
            messages.success(request, _("Image details saved."))
            return redirect(f"{reverse('studio:media')}?pk={item.pk}")
        ctx = self._context(request, selected=item, form=form)
        if request.headers.get("HX-Request"):
            return render(request, "studio/partials/media_details.html", ctx)
        return render(request, "studio/media.html", ctx)


class MagazinePagesView(StaffOnly, View):
    """Re-render an edition's flip-book pages from its PDF."""

    def post(self, request, slug):
        magazine = get_object_or_404(Magazine, slug=slug)
        count = render_magazine_pages(magazine)
        messages.success(request, _("%(count)d pages rendered.") % {"count": count})
        return redirect(request.POST.get("next") or reverse("studio:dashboard"))


class ReaderView(View):
    """The flip-book reader for one published edition. Public."""

    def get(self, request, slug):
        magazine = get_object_or_404(Magazine.objects.published().select_related("cover_image", "theme"), slug=slug)
        pages = list(magazine.pages.all())
        return render(
            request,
            "studio/reader.html",
            {"magazine": magazine, "pages": pages, "theme": magazine.theme, "hide_footer": True},
        )


def studio_toolbar(request):
    """Small partial rendered from base.html for staff."""
    return HttpResponse(status=204)
