from django import forms
from django.utils.translation import gettext_lazy as _

from source.apps.content.models import Media
from source.apps.newsletter.models import Issue

from .models import Announcement, HeroConfig, Theme


class HeroForm(forms.ModelForm):
    class Meta:
        model = HeroConfig
        fields = (
            "variant", "theme", "background",
            "show_masthead", "show_stats", "show_ticker", "show_partners", "show_issue_facts",
            "kicker_de", "kicker_ar", "kicker_en",
            "headline_de", "headline_ar", "headline_en",
            "dek_de", "dek_ar", "dek_en",
            "primary_label_de", "primary_label_ar", "primary_label_en", "primary_url",
            "secondary_label_de", "secondary_label_ar", "secondary_label_en", "secondary_url",
            "pages_label", "price_label",
        )
        widgets = {
            **{f"dek_{lang}": forms.Textarea(attrs={"rows": 3}) for lang in ("de", "ar", "en")},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = "form-checkbox" if isinstance(field.widget, forms.CheckboxInput) else "form-input"
            if isinstance(field.widget, forms.Select):
                css = "form-select"
            if isinstance(field.widget, forms.Textarea):
                css = "form-textarea"
            field.widget.attrs.setdefault("class", css)
            if name.endswith("_ar"):
                field.widget.attrs["dir"] = "rtl"


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ("name", "slug", "accent", "brand", "brand_deep", "interaction", "display_font", "radius", "is_default")
        widgets = {
            "accent": forms.TextInput(attrs={"type": "color"}),
            "brand": forms.TextInput(attrs={"type": "color"}),
            "brand_deep": forms.TextInput(attrs={"type": "color"}),
            "interaction": forms.TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-checkbox")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-input")


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ("kind", "text_de", "text_ar", "text_en", "url", "is_active", "starts_at", "ends_at", "order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-checkbox")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-input")
            if name.endswith("_ar"):
                field.widget.attrs["dir"] = "rtl"


def _style(form):
    """The studio's own input classes, applied once for every field."""
    for name, field in form.fields.items():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs.setdefault("class", "form-checkbox")
        elif isinstance(field.widget, forms.Select):
            field.widget.attrs.setdefault("class", "form-select")
        elif isinstance(field.widget, forms.Textarea):
            field.widget.attrs.setdefault("class", "form-textarea")
        elif not isinstance(field.widget, forms.FileInput):
            field.widget.attrs.setdefault("class", "form-input")
        if name.endswith("_ar"):
            field.widget.attrs["dir"] = "rtl"


class MultiFileInput(forms.ClearableFileInput):
    """Django refuses `multiple` on the plain widget; the view reads the files
    with `request.FILES.getlist`, so allowing it here is safe."""

    allow_multiple_selected = True


class MediaUploadForm(forms.Form):
    """Several files at once. Each becomes its own Media row; the type is read
    from the file itself rather than asked for."""

    files = forms.FileField(
        widget=MultiFileInput(attrs={"multiple": True, "accept": "image/*,video/*,.pdf"}),
        label=_("Files"),
    )

    IMAGE = {"jpg", "jpeg", "png", "webp", "gif", "avif", "tif", "tiff", "bmp", "svg"}
    VIDEO = {"mp4", "webm", "mov", "m4v", "ogv"}

    @classmethod
    def kind(cls, name):
        suffix = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if suffix in cls.IMAGE:
            return "image"
        return "video" if suffix in cls.VIDEO else "document"

    def save(self, files):
        return [Media.objects.create(file=item, media_type=self.kind(item.name)) for item in files]


class MediaDetailsForm(forms.ModelForm):
    """Alt text, caption, credit and the focal point. The focal point comes from
    the picker as two hidden numbers between 0 and 1."""

    class Meta:
        model = Media
        fields = ("alt_text", "caption", "credit", "focal_x", "focal_y")
        widgets = {
            "focal_x": forms.HiddenInput(),
            "focal_y": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)
        self.fields["alt_text"].widget.attrs["placeholder"] = _("What is in the picture?")
        self.fields["caption"].widget.attrs["placeholder"] = _("Shown under the image")
        self.fields["credit"].widget.attrs["placeholder"] = _("Photographer or agency")

    def _clamp(self, name):
        value = self.cleaned_data.get(name)
        if value is None:
            return 0.5
        return min(1.0, max(0.0, value))

    def clean_focal_x(self):
        return self._clamp("focal_x")

    def clean_focal_y(self):
        return self._clamp("focal_y")


class IssueForm(forms.ModelForm):
    """Subject, preheader and intro. The blocks are edited on their own."""

    class Meta:
        model = Issue
        fields = ("language", "subject", "preheader", "intro")
        widgets = {"intro": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)
        self.fields["subject"].widget.attrs["placeholder"] = _("What the inbox shows first")
        self.fields["preheader"].widget.attrs["placeholder"] = _("The line after the subject")
        self.fields["intro"].widget.attrs["placeholder"] = _("A few lines from the desk")
