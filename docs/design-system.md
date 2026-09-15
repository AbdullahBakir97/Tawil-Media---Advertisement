# Design system

Living reference: `/design/` (staff, or anyone while `DEBUG=1`).
Source of truth: `static/css/base/variables.css` (tokens) and `tailwind.config.js` (utilities).

## Direction

Editorial magazine typography for content, navy and gold brand language for
identity moments. Three languages: German (default, no URL prefix), Arabic
(`/ar/`, right-to-left) and English (`/en/`).

## Colour roles

| Role | Token | Used for |
|------|-------|----------|
| Navy | `navy-800/900`, `bg-brand` | header, footer, hero, covers |
| Gold | `gold-400` (`gold-600` on white) | section rules, active nav underline, Subscribe / Read-the-edition CTA, pull quotes |
| Sky | `sky-600/700`, `link` | links, buttons, focus rings, category labels, form accents |
| Almadina red | `almadina` | the Almadina brand tag and Live/Breaking badges only |
| Rose | `error` | errors (kept distinct from the brand red) |

Surfaces use semantic tokens that switch with the theme: `bg-primary` (page),
`bg-secondary` (cards), `bg-tertiary` (inset), `text-primary/secondary/tertiary`,
`border-primary/secondary`. Dark mode is class based (`<html class="dark">`).

## Typography

| Role | Latin | Arabic |
|------|-------|--------|
| Display (headings, pull quotes) | Playfair Display 500/700 | Amiri 400/700 |
| Body (text, UI) | Source Sans 3 400/600 | IBM Plex Sans Arabic 400/500/600 |

Fonts are self-hosted from `static/fonts/` (`npm run vendor` refreshes them)
and subset per script. `:lang(ar)` switches faces and loosens line-height.
Utilities: `font-display`, `font-body`. Classes: `.eyebrow`, `.kicker`,
`.lead`, `.dek`, `.byline`, `.pull-quote`, `.section-title`, `.measure`.

## Layout rules for RTL

Use logical properties and Tailwind logical utilities (`ms-`, `me-`, `ps-`,
`pe-`, `start-`, `end-`, `text-start`), never `left/right` or `ml/mr`, for
anything that should mirror. Icons that imply direction (arrows, chevrons)
get `rtl:rotate-180`. Figures stay left-to-right (`.stat-value`).

## Components

`static/css/components/`: `buttons.css` (`.btn`, `-primary`, `-brand`,
`-secondary`, `-outline`, `-ghost`, `-danger`, `-link`, sizes, `-icon`),
`forms.css` (`.form-input/-select/-textarea/-checkbox/-radio/-switch`,
`.form-label/-help/-error`, `.input-group`, `.form-input--on-brand`),
`cards.css` (`.card`, `--feature`, `--row`, `--lift`, `.stat-tile`,
`.skeleton`, `.panel`, `--brand`, `--glass`), `alerts.css` (`.alert-*`,
`.toast`, `.empty-state`), `badges.css` (`.badge-*`, `.tag`, `.avatar`,
`.count-bubble`, `.divider`), `header.css`.

## Motion

GSAP + ScrollTrigger are vendored; `static/js/core/motion.js` reads
`data-motion` attributes:

| Attribute | Effect |
|-----------|--------|
| `data-motion="fade-up"` | rise and fade in on scroll |
| `data-motion="fade-in"`, `scale-in`, `slide-start` | variants (`slide-start` mirrors in RTL) |
| `data-motion="stagger"` | children animate in sequence (`data-stagger="0.1"`) |
| `data-motion="count" data-count="500" data-suffix="K+"` | count up |
| `data-motion="words"` | headline words rise one by one |
| `data-motion="parallax" data-speed="0.2"` | scroll parallax |
| `data-hero` + `data-hero-item` / `data-hero-bg` | page-load timeline |
| `data-lift` | spring hover lift |

Elements start visible; GSAP animates *from* the hidden state, so pages read
without JavaScript and honour `prefers-reduced-motion`. Content swapped in by
HTMX is animated automatically.
