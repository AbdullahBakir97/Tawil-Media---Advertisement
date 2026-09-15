/**
 * Campaign planner. Counts what the visitor picked and shows a running estimate.
 * Prices are read from the JSON the server rendered and are re-checked server-side
 * when the request is sent, so the browser's total is only a preview.
 *
 * Markup contract (templates/advertising/partials/planner.html):
 *   x-data="planner()" x-init="init()"
 *   <script type="application/json" id="planner-data">[{slug, name, price}, …]</script>
 */
document.addEventListener('alpine:init', () => {
  window.Alpine.data('planner', () => ({
    cards: [],
    selected: {},
    editions: [],

    init() {
      const node = document.getElementById('planner-data');
      if (!node) return;
      try {
        this.cards = JSON.parse(node.textContent);
      } catch (error) {
        this.cards = [];
      }
    },

    card(slug) {
      return this.cards.find((entry) => entry.slug === slug);
    },

    qty(slug) {
      return this.selected[slug] || 0;
    },

    inc(slug) {
      this.selected = { ...this.selected, [slug]: Math.min(this.qty(slug) + 1, 99) };
    },

    dec(slug) {
      const next = { ...this.selected };
      if (next[slug] > 1) next[slug] -= 1;
      else delete next[slug];
      this.selected = next;
    },

    toggleEdition(id) {
      this.editions = this.editions.includes(id)
        ? this.editions.filter((entry) => entry !== id)
        : [...this.editions, id];
    },

    get lines() {
      return Object.entries(this.selected)
        .map(([slug, quantity]) => {
          const card = this.card(slug);
          if (!card) return null;
          return { slug, name: card.name, quantity, total: card.price * quantity };
        })
        .filter(Boolean);
    },

    get total() {
      return this.lines.reduce((sum, line) => sum + line.total, 0);
    },

    /** Money in the page's own language, without decimals for whole amounts. */
    format(value) {
      const locale = document.documentElement.lang || 'de';
      try {
        return new Intl.NumberFormat(locale, {
          style: 'currency',
          currency: 'EUR',
          maximumFractionDigits: value % 1 ? 2 : 0,
        }).format(value);
      } catch (error) {
        return `${Math.round(value)} €`;
      }
    },
  }));
});
