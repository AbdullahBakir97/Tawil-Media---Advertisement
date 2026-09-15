from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import ArchiveYear, Edition


class ArchiveBrowseView(ListView):
    template_name = "archives/browse.html"
    context_object_name = "years"

    def get_queryset(self):
        return ArchiveYear.objects.filter(is_active=True).select_related("cover_image")


class ArchiveYearView(ListView):
    template_name = "archives/year.html"
    context_object_name = "editions"
    paginate_by = 12

    def get_queryset(self):
        self.archive_year = get_object_or_404(ArchiveYear, year=self.kwargs["year"], is_active=True)
        return (
            Edition.objects.filter(archive_year=self.archive_year)
            .select_related("cover_image", "primary_category")
            .order_by("edition_number")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["archive_year"] = self.archive_year
        return context


class EditionDetailView(DetailView):
    template_name = "archives/edition_detail.html"
    context_object_name = "edition"
    queryset = Edition.objects.select_related("archive_year", "cover_image", "primary_category")
