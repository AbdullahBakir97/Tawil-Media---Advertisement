# CSS

The stylesheet is built with [Tailwind CSS](https://tailwindcss.com) v3 from
`static/css/index.css`. Templates use Tailwind utility classes; the files in
this directory add design tokens and a few component classes on top.

```
static/css/
├── index.css            # entry point: Tailwind layers + the files below
├── base/
│   ├── variables.css    # design tokens (colours, spacing, fonts) + dark theme
│   ├── typography.css
│   ├── colors.css
│   └── animations.css
├── components/          # .btn, .form-*, .card, .modal
├── layouts/             # .container, grid / flex helpers
└── dist/main.css        # compiled output – committed, do not edit by hand
```

## Building

```bash
npm install
npm run build:css   # one-off, minified
npm run watch:css   # rebuild on change while developing
```

`static/css/dist/main.css` is committed so the Django app runs without Node.
CI fails if it is out of date, so rebuild it before committing template or CSS
changes.

## Theming

* Semantic colours (`bg-primary`, `text-secondary`, `border-primary`, …) map to
  the CSS variables in `base/variables.css` and switch automatically in dark
  mode.
* Brand shades (`bg-primary-600`, `text-primary-400`, …) come from the palette
  in `tailwind.config.js`.
* Dark mode is class based: `<html class="dark">`. `base.html` sets the class
  before first paint from `localStorage` or the OS preference, and the Alpine
  `$store.theme.toggle()` flips it.
