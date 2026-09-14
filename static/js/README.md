# JavaScript

Plain ES modules, no bundler. `base.html` loads:

1. HTMX and Alpine.js from a CDN.
2. `core/htmx-conf.js` – global HTMX configuration (CSRF header, toasts,
   loading states). Not a module; it needs the `htmx` global.
3. `app.js` as `type="module"` – the entry point that imports everything else.

```
static/js/
├── app.js                   # entry point
├── core/
│   ├── utils.js             # debounce, DOM helpers, formatting
│   ├── state.js             # tiny observable store
│   └── htmx-conf.js
├── components/
│   ├── search.js            # header search suggestions
│   ├── infinite-scroll.js
│   └── lazy-load.js
└── analytics/
    ├── tracking.js          # page-view / event tracking
    └── performance.js       # Web-Vitals style reporting
```

Components initialise themselves only when their DOM hook is present
(`[data-search-input]`, `[data-infinite-scroll]`, `[data-lazy]`).

Analytics modules are imported lazily and only when `<body>` carries a
`data-analytics-endpoint` attribute and the page is not in debug mode. There is
no server endpoint for them yet.
