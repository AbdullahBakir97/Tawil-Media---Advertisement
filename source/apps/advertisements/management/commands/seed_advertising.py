"""Fill the rate card with the formats a magazine normally sells, at placeholder
prices. Re-runnable: entries are matched on their slug."""

from django.core.management.base import BaseCommand

from source.apps.advertisements.models import RateCard

CARDS = [
    # slug, channel, de, ar, en, specs, w, h, price, unit, featured
    ("print-full-page", "print", "1/1 Seite", "صفحة كاملة", "Full page",
     "210 × 297 mm + 3 mm Beschnitt, CMYK", 210, 297, 1200, "edition", False),
    ("print-half-page", "print", "1/2 Seite", "نصف صفحة", "Half page",
     "185 × 130 mm, CMYK", 185, 130, 700, "edition", False),
    ("print-quarter-page", "print", "1/4 Seite", "ربع صفحة", "Quarter page",
     "90 × 130 mm, CMYK", 90, 130, 400, "edition", False),
    ("print-back-cover", "print", "U4 · Rückseite", "الغلاف الأخير", "Back cover",
     "210 × 297 mm + 3 mm Beschnitt, CMYK", 210, 297, 1900, "edition", True),
    ("print-inside-cover", "print", "U2 · innere Umschlagseite", "الغلاف الداخلي", "Inside front cover",
     "210 × 297 mm + 3 mm Beschnitt, CMYK", 210, 297, 1600, "edition", False),
    ("digital-leaderboard", "digital", "Leaderboard", "بانر علوي", "Leaderboard",
     "728 × 90 px, JPG/PNG, max. 150 KB", 728, 90, 450, "week", False),
    ("digital-billboard", "digital", "Billboard", "لوحة إعلانية", "Billboard",
     "970 × 250 px, JPG/PNG, max. 200 KB", 970, 250, 750, "week", True),
    ("digital-rectangle", "digital", "Rectangle", "مستطيل", "Rectangle",
     "300 × 250 px, JPG/PNG, max. 120 KB", 300, 250, 350, "week", False),
    ("digital-newsletter", "digital", "Newsletter-Banner", "بانر النشرة البريدية", "Newsletter banner",
     "600 × 150 px, eine Aussendung", 600, 150, 300, "send", False),
    ("digital-sponsored", "digital", "Gesponserte Geschichte", "قصة مموّلة", "Sponsored story",
     "Im Layout der Redaktion, klar gekennzeichnet", None, None, 1400, "package", True),
    ("social-post", "social", "Social-Beitrag", "منشور على الشبكات", "Social post",
     "1080 × 1080 px, ein Beitrag auf allen Kanälen", 1080, 1080, 250, "package", False),
    ("social-story", "social", "Story", "ستوري", "Story",
     "1080 × 1920 px, 24 Stunden", 1080, 1920, 180, "package", False),
]

DESCRIPTIONS = {
    "print-full-page": (
        "Eine ganze Seite im Heft, zwischen den Geschichten der Redaktion.",
        "صفحة كاملة داخل المجلة بين مواد التحرير.",
        "A full page inside the magazine, between the editorial stories.",
    ),
    "print-back-cover": (
        "Die meistgesehene Seite des Hefts – oft im Laden nach oben gelegt.",
        "الصفحة الأكثر مشاهدة في العدد، وغالباً ما تُعرض للأعلى في المتاجر.",
        "The most seen page of the issue, often placed face up in shops.",
    ),
    "digital-sponsored": (
        "Eine Geschichte über Ihr Unternehmen, geschrieben im Ton des Magazins und klar als Anzeige gekennzeichnet.",
        "قصة عن شركتك بأسلوب المجلة، محدّدة بوضوح كإعلان.",
        "A story about your company, written in the magazine's voice and clearly marked as an advertisement.",
    ),
}


class Command(BaseCommand):
    help = "Create the standard rate card entries with placeholder prices."

    def handle(self, *args, **options):
        for order, (slug, channel, de, ar, en, specs, width, height, price, unit, featured) in enumerate(CARDS):
            description = DESCRIPTIONS.get(slug, ("", "", ""))
            RateCard.objects.update_or_create(
                slug=slug,
                defaults={
                    "channel": channel,
                    "name_de": de,
                    "name_ar": ar,
                    "name_en": en,
                    "description_de": description[0],
                    "description_ar": description[1],
                    "description_en": description[2],
                    "specs": specs,
                    "width": width,
                    "height": height,
                    "price": price,
                    "unit": unit,
                    "is_featured": featured,
                    "order": order,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Rate card seeded: {len(CARDS)} entries."))
