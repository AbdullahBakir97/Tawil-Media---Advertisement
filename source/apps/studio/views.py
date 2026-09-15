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

from source.apps.content.models import Article, Contributor, Magazine, Media
from source.apps.content.workflow import BOARD_ORDER, PUBLISHED, SCHEDULED, STATUS_CHOICES
from source.apps.events.models import Event
from source.apps.newsletter.composer import render_issue
from source.apps.newsletter.models import LANGUAGES, Issue, IssueBlock, NewsletterSubscriber
from source.apps.newsletter.sending import send_issue, send_test

from .collections import CollectionView
from .forms import (
    AdSlotForm,
    AnnouncementForm,
    ArticleForm,
    FAQForm,
    HeroForm,
    IssueForm,
    MagazineForm,
    MediaDetailsForm,
    MediaUploadForm,
    MilestoneForm,
    PartnerForm,
    TestimonialForm,
    ThemeForm,
)
from .models import FAQ, AdSlot, Announcement, HeroConfig, Milestone, Partner, PressKit, Testimonial, Theme
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
            + Magazine.objects.exclude(status=PUBLISHED).count()
            + Event.objects.exclude(status=PUBLISHED).count(),
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
            "event_columns": self._columns(Event),
            "due_now": Article.objects.due().count() + Magazine.objects.due().count() + Event.objects.due().count(),
            "now": timezone.now(),
        }

    def get(self, request):
        return render(request, "studio/desk.html", self._context())

    def post(self, request):
        """One move per post: to draft, to review, scheduled or live."""
        model = {"magazine": Magazine, "event": Event}.get(request.POST.get("kind"), Article)
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


class ArticleEditorView(StaffOnly, View):
    """Write an article without leaving the Studio.

    The same page creates and edits: without a pk it is a new piece, with one
    it is that piece. Saving never changes the workflow state — moving a draft
    along is a separate, deliberate click, so a quick typo fix cannot publish
    something by accident.
    """

    def _article(self, pk):
        return get_object_or_404(Article, pk=pk) if pk else Article()

    def _context(self, request, article, form=None):
        return {
            "article": article if article.pk else None,
            "form": form or ArticleForm(instance=article),
            "is_new": article.pk is None,
            "preview_url": article.preview_url() if article.pk else "",
            "languages": [("de", _("German")), ("ar", _("Arabic")), ("en", _("English"))],
        }

    def get(self, request, pk=None):
        return render(request, "studio/article_edit.html", self._context(request, self._article(pk)))

    def post(self, request, pk=None):
        article = self._article(pk)
        action = request.POST.get("action", "save")

        if action == "delete" and article.pk:
            title = article.title
            article.delete()
            messages.success(request, _("“%(title)s” was deleted.") % {"title": title})
            return redirect("studio:desk")

        form = ArticleForm(request.POST, instance=article)
        if not form.is_valid():
            messages.error(request, _("Something in the form needs attention."))
            return render(request, "studio/article_edit.html", self._context(request, article, form))

        article = form.save(commit=False)
        if article.author_id is None and not article.pk:
            article.author = request.user
        article.save()
        form.save_m2m()

        if action == "save-and-review":
            article.send_to_review()
            messages.success(request, _("Saved and sent to review."))
        else:
            messages.success(request, _("Saved."))
        return redirect("studio:article_edit", pk=article.pk)


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


class NewsletterListView(StaffOnly, View):
    """Every issue: what went out, what is queued, what is still being written."""

    def get(self, request):
        return render(request, "studio/newsletter.html", {
            "issues": Issue.objects.all()[:40],
            "form": IssueForm(),
            "subscriber_counts": {
                code: NewsletterSubscriber.objects.filter(is_active=True, language=code).count()
                for code, _label in LANGUAGES
            },
        })

    def post(self, request):
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save()
            return redirect("studio:newsletter_edit", pk=issue.pk)
        return render(request, "studio/newsletter.html", {"issues": Issue.objects.all()[:40], "form": form})


class NewsletterEditView(StaffOnly, View):
    """Compose one issue: the copy, the blocks, and a preview of the real mail."""

    #: What the desk can drop in, and where each comes from.
    def _choices(self):
        return {
            "articles": Article.objects.published().select_related("author").prefetch_related("media")[:12],
            "editions": Magazine.objects.published().select_related("cover_image")[:6],
            "events": Event.objects.upcoming()[:6],
            "ads": AdSlot.objects.filter(is_active=True)[:6],
        }

    def _context(self, issue, form=None):
        return {
            "issue": issue,
            "form": form or IssueForm(instance=issue),
            "blocks": issue.blocks.select_related("article", "edition", "event", "ad_slot"),
            "recipients": issue.recipients().count(),
            **self._choices(),
        }

    def get(self, request, pk):
        issue = get_object_or_404(Issue, pk=pk)
        return render(request, "studio/newsletter_edit.html", self._context(issue))

    def post(self, request, pk):
        issue = get_object_or_404(Issue, pk=pk)
        action = request.POST.get("action", "save")

        if issue.is_sent and action != "duplicate":
            messages.error(request, _("This issue has already gone out. Duplicate it to send another."))
            return redirect("studio:newsletter_edit", pk=issue.pk)

        if action == "add-block":
            self._add_block(request, issue)
        elif action == "remove-block":
            issue.blocks.filter(pk=request.POST.get("block")).delete()
        elif action == "move-block":
            self._move_block(request, issue)
        elif action == "schedule":
            when = parse_datetime(request.POST.get("when", "") or "")
            if when is None:
                messages.error(request, _("That date could not be read."))
            else:
                if timezone.is_naive(when):
                    when = timezone.make_aware(when)
                issue.scheduled_for, issue.status = when, Issue.SCHEDULED
                issue.save(update_fields=["scheduled_for", "status", "updated_at"])
                messages.success(request, _("Queued to go out."))
        elif action == "unschedule":
            issue.status, issue.scheduled_for = Issue.DRAFT, None
            issue.save(update_fields=["status", "scheduled_for", "updated_at"])
        elif action == "test":
            address = request.POST.get("email", "").strip()
            if address:
                send_test(issue, address)
                messages.success(request, _("Test sent to %(email)s.") % {"email": address})
        elif action == "send":
            sent = send_issue(issue)
            messages.success(request, _("Sent to %(count)d subscribers.") % {"count": sent})
            return redirect("studio:newsletter")
        else:
            form = IssueForm(request.POST, instance=issue)
            if form.is_valid():
                issue = form.save()
                messages.success(request, _("Issue saved."))
            else:
                return render(request, "studio/newsletter_edit.html", self._context(issue, form))

        if request.headers.get("HX-Request"):
            return render(request, "studio/partials/newsletter_blocks.html", self._context(issue))
        return redirect("studio:newsletter_edit", pk=issue.pk)

    def _add_block(self, request, issue):
        kind = request.POST.get("kind", IssueBlock.ARTICLE)
        target = request.POST.get("target")
        block = IssueBlock(issue=issue, kind=kind, order=issue.blocks.count())
        if kind in (IssueBlock.ARTICLE, IssueBlock.LEAD):
            block.article_id = target
        elif kind == IssueBlock.EDITION:
            block.edition_id = target
        elif kind == IssueBlock.EVENT:
            block.event_id = target
        elif kind == IssueBlock.AD:
            block.ad_slot_id = target
        elif kind == IssueBlock.TEXT:
            block.heading = request.POST.get("heading", "")
            block.body = request.POST.get("body", "")
        block.save()

    def _move_block(self, request, issue):
        """Swap a block with its neighbour, which is all reordering needs."""
        blocks = list(issue.blocks.all())
        index = next((i for i, block in enumerate(blocks) if str(block.pk) == request.POST.get("block")), None)
        if index is None:
            return
        target = index - 1 if request.POST.get("direction") == "up" else index + 1
        if not 0 <= target < len(blocks):
            return
        blocks[index].order, blocks[target].order = target, index
        IssueBlock.objects.bulk_update([blocks[index], blocks[target]], ["order"])


@method_decorator(xframe_options_sameorigin, name="dispatch")
class NewsletterPreviewView(StaffOnly, View):
    """The issue as the e-mail really renders, framed by the composer."""

    def get(self, request, pk):
        issue = get_object_or_404(Issue, pk=pk)
        return HttpResponse(render_issue(issue))


class PressView(TemplateView):
    """The press page. Public.

    The kit holds only what a journalist cannot work out for themselves — the
    boilerplate, the contact and the downloadable assets. The numbers, the
    colours and the current edition are read from the site's own data, so the
    page cannot quietly go stale.
    """

    template_name = "studio/press.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        kit = PressKit.current()
        theme = Theme.objects.filter(is_default=True).first()
        ctx.update(
            kit=kit,
            assets=list(kit.assets.all()) if kit else [],
            theme=theme,
            palette=[
                (_("Brand"), getattr(theme, "brand", "#0b2545")),
                (_("Brand, deep"), getattr(theme, "brand_deep", "#08182e")),
                (_("Editorial gold"), getattr(theme, "accent", "#f2b25c")),
                (_("Interaction"), getattr(theme, "interaction", "#0284c7")),
            ],
            latest_edition=Magazine.objects.published().select_related("cover_image").first(),
            contributors=Contributor.objects.filter(is_active=True).select_related("portrait")[:4],
        )
        return ctx


def studio_toolbar(request):
    """Small partial rendered from base.html for staff."""
    return HttpResponse(status=204)


# ---------------------------------------------------------------------------
# The short lists. Each declares only what makes it different; the shared
# CollectionView in collections.py does the rest.
# ---------------------------------------------------------------------------


class AdSlotListView(StaffOnly, CollectionView):
    model = AdSlot
    form_class = AdSlotForm
    url_name = "studio:ad_slots"
    title = _("Ad slots")
    lead = _("Where adverts appear, who booked them and for how long.")
    empty_title = _("No ad slots yet")
    empty_lead = _("Add one and it appears wherever its key is placed in the design.")

    def get_queryset(self):
        return AdSlot.objects.order_by("key", "-weight")

    def row_label(self, item):
        return item.advertiser or item.key

    def row_meta(self, item):
        parts = [item.key, item.get_format_display()]
        if item.starts_at or item.ends_at:
            starts = f"{item.starts_at:%d.%m.%Y}" if item.starts_at else "…"
            ends = f"{item.ends_at:%d.%m.%Y}" if item.ends_at else "…"
            parts.append(f"{starts} – {ends}")
        return " · ".join(parts)


class PartnerListView(StaffOnly, CollectionView):
    model = Partner
    form_class = PartnerForm
    url_name = "studio:partners"
    order_field = "order"
    title = _("Partners")
    lead = _("The logos shown across the site.")
    empty_title = _("No partners yet")
    empty_lead = _("Upload a logo and it joins the row on the front page.")

    def row_meta(self, item):
        return item.url


class TestimonialListView(StaffOnly, CollectionView):
    model = Testimonial
    form_class = TestimonialForm
    url_name = "studio:testimonials"
    order_field = "order"
    title = _("Voices")
    lead = _("What readers and partners say about the magazine.")
    empty_title = _("No voices yet")
    empty_lead = _("Add a quote and it appears where the design asks for one.")

    def row_label(self, item):
        return item.name

    def row_meta(self, item):
        return item.role


class FAQListView(StaffOnly, CollectionView):
    model = FAQ
    form_class = FAQForm
    url_name = "studio:faq"
    order_field = "order"
    title = _("FAQ")
    lead = _("The questions each page answers, in the order they are asked.")
    empty_title = _("No questions yet")
    empty_lead = _("Add the first one and it appears on the page you choose.")

    def get_queryset(self):
        return FAQ.objects.order_by("page", "order")

    def row_label(self, item):
        return item.question_de or item.question_en or item.question_ar

    def row_meta(self, item):
        return item.get_page_display()


class MilestoneListView(StaffOnly, CollectionView):
    model = Milestone
    form_class = MilestoneForm
    url_name = "studio:timeline"
    title = _("Timeline")
    lead = _("The years that shaped the magazine.")
    empty_title = _("No milestones yet")
    empty_lead = _("Add a year and it appears on the timeline.")

    def get_queryset(self):
        return Milestone.objects.order_by("year")

    def row_label(self, item):
        return item.title_de or item.title_en or item.title_ar

    def row_meta(self, item):
        return str(item.year)


class MagazineEditorView(StaffOnly, View):
    """An edition's details and its contents.

    Like the article editor, saving never changes the workflow state — an
    edition goes live from the desk, deliberately.
    """

    def get(self, request, pk=None):
        if pk is None and request.GET.get("new") is None:
            return render(request, "studio/magazine_list.html", {
                "magazines": Magazine.objects.select_related("cover_image").order_by("-issue_number", "-created_at"),
            })
        magazine = get_object_or_404(Magazine, pk=pk) if pk else Magazine()
        return render(request, "studio/magazine_edit.html", self._context(magazine))

    def _context(self, magazine, form=None):
        return {
            "magazine": magazine if magazine.pk else None,
            "form": form or MagazineForm(instance=magazine),
            "is_new": magazine.pk is None,
        }

    def post(self, request, pk=None):
        magazine = get_object_or_404(Magazine, pk=pk) if pk else Magazine()
        if request.POST.get("action") == "delete" and magazine.pk:
            title = magazine.title
            magazine.delete()
            messages.success(request, _("“%(title)s” was deleted.") % {"title": title})
            return redirect("studio:magazines")

        form = MagazineForm(request.POST, request.FILES, instance=magazine)
        if not form.is_valid():
            messages.error(request, _("Something in the form needs attention."))
            return render(request, "studio/magazine_edit.html", self._context(magazine, form))
        magazine = form.save()
        messages.success(request, _("Saved."))
        return redirect("studio:magazine_edit", pk=magazine.pk)
