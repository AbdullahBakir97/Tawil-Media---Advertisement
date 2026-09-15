from django import forms

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
