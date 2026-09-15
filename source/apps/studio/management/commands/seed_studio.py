"""Fill the Studio with a working starting point: a theme, the announcement line,
partners, testimonials, FAQ entries and the timeline. Safe to re-run."""

from django.core.management.base import BaseCommand

from source.apps.studio.models import FAQ, Announcement, HeroConfig, Milestone, Testimonial, Theme

THEMES = [
    {
        "slug": "almadina",
        "name": "Almadina",
        "accent": "#f2b25c",
        "brand": "#062a4a",
        "brand_deep": "#031428",
        "interaction": "#0284c7",
        "display_font": "playfair",
        "radius": 20,
        "is_default": True,
    },
    {
        "slug": "almadina-winter",
        "name": "Almadina · Winter",
        "accent": "#7dd3fc",
        "brand": "#14213d",
        "brand_deep": "#0b1626",
        "interaction": "#0369a1",
        "display_font": "playfair",
        "radius": 8,
        "is_default": False,
    },
]

ANNOUNCEMENTS = [
    ("editorial", "Die neue Ausgabe ist erschienen – jetzt im Handel und online", "صدر العدد الجديد – في الأكشاك وعلى الإنترنت", "The new edition is out now, in print and online", 0),
    ("ad", "Werben in der nächsten Ausgabe: Buchungsschluss [DATUM]", "أعلن في العدد القادم: آخر موعد للحجز [التاريخ]", "Advertise in the next edition: booking closes [DATE]", 1),
    ("editorial", "Newsletter: jede Woche die neue Ausgabe und unsere besten Geschichten", "النشرة البريدية: العدد الجديد وأفضل القصص كل أسبوع", "Newsletter: the new edition and our best stories, weekly", 2),
]

TESTIMONIALS = [
    ("Über Almadina erreichen wir Kundinnen und Kunden, die sonst keine Anzeige von uns sehen würden.",
     "من خلال المدينة نصل إلى زبائن ما كانوا ليروا إعلاننا في مكان آخر.",
     "Almadina reaches customers who would never see an advertisement from us anywhere else.",
     "[Name]", "[Unternehmen], Berlin"),
    ("Die Redaktion versteht unsere Community – das merkt man in jedem Heft.",
     "هيئة التحرير تفهم مجتمعنا، ويظهر ذلك في كل عدد.",
     "The editorial team understands our community, and it shows in every issue.",
     "[Name]", "[Organisation], Berlin"),
]

FAQS = [
    ("help", "Wo bekomme ich die gedruckte Ausgabe?", "أين أحصل على النسخة المطبوعة؟", "Where can I get the printed edition?",
     "In unseren Auslagestellen in Berlin und in weiteren Städten – oder kostenlos online.",
     "في أماكن التوزيع في برلين ومدن أخرى، أو مجاناً عبر الإنترنت.",
     "At our pick-up points in Berlin and other cities, or free of charge online."),
    ("help", "Erscheint Almadina auch auf Deutsch?", "هل تصدر المدينة بالألمانية أيضاً؟", "Is Almadina published in German too?",
     "Die Website erscheint auf Deutsch, Arabisch und Englisch. Das Heft erscheint auf Arabisch.",
     "الموقع بالألمانية والعربية والإنجليزية، والمجلة المطبوعة بالعربية.",
     "The website is in German, Arabic and English. The printed magazine is in Arabic."),
    ("advertise", "Wie buche ich eine Anzeige?", "كيف أحجز إعلاناً؟", "How do I book an advertisement?",
     "Schreiben Sie uns über das Kontaktformular. Wir senden Ihnen die Mediadaten und planen die Platzierung mit Ihnen.",
     "راسلنا عبر نموذج الاتصال. سنرسل لك الملف الإعلامي ونخطط معك مكان الإعلان.",
     "Write to us through the contact form. We will send the media kit and plan the placement with you."),
    ("about", "Seit wann gibt es Almadina?", "منذ متى تصدر المدينة؟", "How long has Almadina existed?",
     "Seit 2006 – als erstes arabisches Magazin in Deutschland.",
     "منذ عام 2006، كأول مجلة عربية في ألمانيا.",
     "Since 2006, as the first Arabic magazine in Germany."),
]

MILESTONES = [
    (2006, "Erste Ausgabe in Berlin", "أول عدد في برلين", "First edition in Berlin", "", "", ""),
    (2012, "[MEILENSTEIN]", "[محطة]", "[MILESTONE]", "", "", ""),
    (2019, "[MEILENSTEIN]", "[محطة]", "[MILESTONE]", "", "", ""),
    (2026, "Gedruckt und digital", "مطبوع ورقمي", "In print and digital", "", "", ""),
]


class Command(BaseCommand):
    help = "Create a starting Studio setup: theme, announcements, testimonials, FAQ, timeline."

    def handle(self, *args, **options):
        for data in THEMES:
            Theme.objects.update_or_create(slug=data.pop("slug"), defaults=data)
        HeroConfig.for_placement("home")

        for kind, de, ar, en, order in ANNOUNCEMENTS:
            Announcement.objects.update_or_create(
                text_de=de, defaults={"kind": kind, "text_ar": ar, "text_en": en, "order": order}
            )
        for de, ar, en, name, role in TESTIMONIALS:
            Testimonial.objects.update_or_create(
                name=name, quote_de=de, defaults={"quote_ar": ar, "quote_en": en, "role": role}
            )
        for page, q_de, q_ar, q_en, a_de, a_ar, a_en in FAQS:
            FAQ.objects.update_or_create(
                question_de=q_de,
                defaults={"page": page, "question_ar": q_ar, "question_en": q_en, "answer_de": a_de, "answer_ar": a_ar, "answer_en": a_en},
            )
        for year, t_de, t_ar, t_en, x_de, x_ar, x_en in MILESTONES:
            Milestone.objects.update_or_create(
                year=year,
                defaults={"title_de": t_de, "title_ar": t_ar, "title_en": t_en, "text_de": x_de, "text_ar": x_ar, "text_en": x_en},
            )
        self.stdout.write(self.style.SUCCESS("Studio seeded."))
