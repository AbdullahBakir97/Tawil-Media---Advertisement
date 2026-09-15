from datetime import date

from django.test import TestCase

from .models import AdCampaign, Advertisement, Advertiser


class AdvertisementCounterTests(TestCase):
    def test_increments_survive_stale_instances(self):
        advertiser = Advertiser.objects.create(name="ACME", email="adv@example.com")
        campaign = AdCampaign.objects.create(
            name="Spring", advertiser=advertiser, budget=100,
            start_date=date(2025, 1, 1), end_date=date(2025, 12, 31),
        )
        ad = Advertisement.objects.create(
            name="Banner", campaign=campaign, url="https://example.com",
            start_date=date(2025, 1, 1), end_date=date(2025, 12, 31),
        )
        stale_copy = Advertisement.objects.get(pk=ad.pk)
        ad.increment_impressions()
        stale_copy.increment_impressions()  # would lose an update with read-modify-save
        ad.refresh_from_db()
        self.assertEqual(ad.impressions, 2)
