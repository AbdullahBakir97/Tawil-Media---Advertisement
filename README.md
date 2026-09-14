# Tawil Media

A Django platform for publishing articles and magazines, running advertising
campaigns, selling subscriptions and browsing a digitised archive.

[![CI](https://github.com/AbdullahBakir97/Tawil-Media---Advertisement/actions/workflows/ci.yml/badge.svg)](https://github.com/AbdullahBakir97/Tawil-Media---Advertisement/actions/workflows/ci.yml)

## Stack

| Layer      | Choice                                                            |
|------------|-------------------------------------------------------------------|
| Backend    | Python 3.11+, Django 5.1, django-taggit                            |
| Frontend   | Django templates, Tailwind CSS 3, HTMX 1.9, Alpine.js 3            |
| Database   | SQLite by default, PostgreSQL via environment variables            |
| Tooling    | ruff, GitHub Actions, Dependabot                                   |

## Project layout

```
project/            settings, root urls, wsgi/asgi
source/apps/
  core/             home, static pages, search, newsletter, error pages
  users/            e-mail login, registration, profile & settings
  content/          articles, categories, media, magazines
  archives/         archive years, editions, edition contents
  advertisements/   advertisers, campaigns, placements, ads
  subscriptions/    plans, subscriptions, billing, discount codes
  payments/         payment methods, payments, refunds, invoices
  seo_analytics/    SEO settings, analytics events, page visits
templates/          site templates (base/, pages/, content/, auth/, …)
static/             css/ (Tailwind source + compiled dist/), js/, img/
tests/              project-level tests (pages, auth flow, migrations)
```

The `advertisements`, `subscriptions`, `payments` and `seo_analytics` apps
currently provide models and admin only; their public views are not built yet.

## Getting started

```bash
git clone https://github.com/AbdullahBakir97/Tawil-Media---Advertisement.git
cd Tawil-Media---Advertisement

python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

cp .env.example .env                                  # optional, defaults work for local dev
python manage.py migrate
python manage.py createsuperuser                      # prompts for e-mail and password
python manage.py runserver
```

Open http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/admin/ for
the admin. Publish an article (tick "Is published") and it appears on the
homepage.

### Frontend assets

The compiled stylesheet `static/css/dist/main.css` is committed, so Node is only
needed when you change templates or CSS:

```bash
npm install
npm run build        # vendor htmx/alpine + build minified CSS
npm run watch:css    # rebuild on change during development
```

CI fails if `main.css` is out of date, so rebuild before committing.

### Configuration

All environment-specific settings are read from environment variables; see
`.env.example`. In production set at least `DEBUG=0`, a long random
`SECRET_KEY`, `ALLOWED_HOSTS`, and the `POSTGRES_*` / `EMAIL_*` variables.

## Quality checks

```bash
ruff check .
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
python manage.py test
```

These are the exact steps CI runs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).
Security issues: see [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
