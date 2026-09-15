"""One page shape for the Studio's short lists.

Ad slots, partners, testimonials, FAQ entries and timeline milestones are all
the same kind of thing: a handful of rows the desk adds to, reorders, switches
off and edits. Writing five nearly identical views would mean five places to
fix every bug, so they share this one and differ only in what they declare.
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View


class CollectionView(View):
    """A list of rows with an edit form beside it.

    Subclasses set :attr:`model` and :attr:`form_class` and describe the page.
    Everything else — creating, editing, deleting, switching a row off,
    moving one up or down — is handled here.
    """

    model = None
    form_class = None
    template_name = "studio/collection.html"

    #: Shown at the top of the page.
    title = ""
    lead = ""
    #: Shown when there is nothing yet.
    empty_title = ""
    empty_lead = ""
    #: The field rows are ordered by, when they can be reordered by hand.
    order_field = None
    #: Route name, so the template can post back to the right page.
    url_name = ""

    def get_queryset(self):
        return self.model.objects.all()

    def row_label(self, item):
        """What each row is called in the list. Overridden where `str` is thin."""
        return str(item)

    def row_meta(self, item):
        """A second line under the label, or an empty string."""
        return ""

    # -- rendering ---------------------------------------------------------

    def _context(self, request, form=None, editing=None):
        items = list(self.get_queryset())
        return {
            "items": [
                {
                    "object": item,
                    "label": self.row_label(item),
                    "meta": self.row_meta(item),
                    "is_active": getattr(item, "is_active", True),
                    "is_editing": editing is not None and item.pk == editing,
                }
                for item in items
            ],
            "form": form if form is not None else self.form_class(),
            "editing": editing,
            "title": self.title,
            "lead": self.lead,
            "empty_title": self.empty_title,
            "empty_lead": self.empty_lead,
            "url_name": self.url_name,
            "can_reorder": bool(self.order_field),
            "can_switch_off": hasattr(self.model, "is_active"),
        }

    def get(self, request):
        editing = request.GET.get("edit")
        form, editing_pk = self.form_class(), None
        if editing:
            item = get_object_or_404(self.model, pk=editing)
            form, editing_pk = self.form_class(instance=item), item.pk
        return render(request, self.template_name, self._context(request, form, editing_pk))

    # -- actions -----------------------------------------------------------

    def post(self, request):
        action = request.POST.get("action", "save")
        handler = {
            "save": self._save,
            "delete": self._delete,
            "toggle": self._toggle,
            "move": self._move,
        }.get(action)
        if handler is None:
            messages.error(request, _("Unknown action."))
            return redirect(self.url_name)
        return handler(request)

    def _save(self, request):
        pk = request.POST.get("pk")
        instance = get_object_or_404(self.model, pk=pk) if pk else None
        form = self.form_class(request.POST, request.FILES, instance=instance)
        if not form.is_valid():
            messages.error(request, _("Something in the form needs attention."))
            return render(request, self.template_name,
                          self._context(request, form, instance.pk if instance else None))
        item = form.save(commit=False)
        if self.order_field and not pk and not getattr(item, self.order_field, 0):
            setattr(item, self.order_field, self.get_queryset().count())
        item.save()
        form.save_m2m()
        messages.success(request, _("Saved."))
        return redirect(self.url_name)

    def _delete(self, request):
        item = get_object_or_404(self.model, pk=request.POST.get("pk"))
        label = self.row_label(item)
        item.delete()
        messages.success(request, _("“%(label)s” was deleted.") % {"label": label})
        return redirect(self.url_name)

    def _toggle(self, request):
        """Switch a row off without deleting it — the usual way to retire one."""
        item = get_object_or_404(self.model, pk=request.POST.get("pk"))
        item.is_active = not item.is_active
        item.save(update_fields=["is_active"])
        return redirect(self.url_name)

    def _move(self, request):
        """Swap a row with its neighbour, which is all reordering needs here."""
        if not self.order_field:
            return redirect(self.url_name)
        rows = list(self.get_queryset())
        index = next((i for i, row in enumerate(rows) if str(row.pk) == request.POST.get("pk")), None)
        if index is None:
            return redirect(self.url_name)
        target = index - 1 if request.POST.get("direction") == "up" else index + 1
        if not 0 <= target < len(rows):
            return redirect(self.url_name)
        current_order = getattr(rows[index], self.order_field)
        setattr(rows[index], self.order_field, getattr(rows[target], self.order_field))
        setattr(rows[target], self.order_field, current_order)
        # Equal values leave the order untouched, so fall back to the positions.
        if getattr(rows[index], self.order_field) == getattr(rows[target], self.order_field):
            setattr(rows[index], self.order_field, target)
            setattr(rows[target], self.order_field, index)
        self.model.objects.bulk_update([rows[index], rows[target]], [self.order_field])
        return redirect(self.url_name)
