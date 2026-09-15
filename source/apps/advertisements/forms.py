"""The campaign planner's request form. Validates the picked placements server-side:
the browser's estimate is never trusted, prices are re-read from the rate card."""

import json

from django import forms
from django.utils.translation import gettext_lazy as _

from source.apps.content.models import Magazine

from .models import CampaignRequest, CampaignRequestItem, RateCard


class CampaignRequestForm(forms.ModelForm):
    """``selection`` is the JSON the planner posts: {"rate_card_slug": quantity}."""

    selection = forms.CharField(widget=forms.HiddenInput, required=False)
    edition_ids = forms.CharField(widget=forms.HiddenInput, required=False)
    consent = forms.BooleanField(
        required=True,
        label=_("I agree that my details may be used to answer this request."),
    )

    class Meta:
        model = CampaignRequest
        fields = ("company", "contact_name", "email", "phone", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-checkbox")
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "form-textarea")
            elif not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs.setdefault("class", "form-input")
            if name in ("company", "contact_name"):
                field.widget.attrs.setdefault("dir", "auto")

    def clean_selection(self):
        raw = self.cleaned_data.get("selection") or "{}"
        try:
            data = json.loads(raw)
        except (TypeError, ValueError) as exc:
            raise forms.ValidationError(_("Your selection could not be read. Please choose the placements again.")) from exc
        if not isinstance(data, dict):
            raise forms.ValidationError(_("Your selection could not be read. Please choose the placements again."))

        cleaned = {}
        for slug, quantity in data.items():
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                continue
            if quantity > 0:
                cleaned[str(slug)] = min(quantity, 99)
        if not cleaned:
            raise forms.ValidationError(_("Choose at least one placement."))
        return cleaned

    def clean_edition_ids(self):
        raw = self.cleaned_data.get("edition_ids") or ""
        return [int(part) for part in raw.split(",") if part.strip().isdigit()]

    def save(self, commit=True, language=""):
        selection = self.cleaned_data["selection"]
        cards = {card.slug: card for card in RateCard.objects.filter(slug__in=selection, is_active=True)}
        if not cards:
            raise forms.ValidationError(_("Choose at least one placement."))

        request_obj = super().save(commit=False)
        request_obj.language = language
        request_obj.estimate = sum(cards[slug].price * qty for slug, qty in selection.items() if slug in cards)
        request_obj.save()

        CampaignRequestItem.objects.bulk_create(
            CampaignRequestItem(request=request_obj, rate_card=cards[slug], quantity=qty, unit_price=cards[slug].price)
            for slug, qty in selection.items()
            if slug in cards
        )
        editions = Magazine.objects.filter(pk__in=self.cleaned_data["edition_ids"])
        if editions:
            request_obj.editions.set(editions)
        return request_obj
