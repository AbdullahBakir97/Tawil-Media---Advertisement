"""Studio: the in-site editor for staff. Every page is server-rendered; forms post
with HTMX and swap back the updated panel and preview."""

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import TemplateView

from source.apps.content.models import Article, Magazine

from .forms import AnnouncementForm, HeroForm, ThemeForm
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
