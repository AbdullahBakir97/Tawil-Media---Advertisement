/**
 * Flip-book reader. Wraps the vendored page-flip library in an Alpine component so
 * an edition reads like the printed magazine: drag a corner, click the edges, use the
 * arrow keys, jump from the thumbnails, zoom, go fullscreen, share the open page.
 *
 * Markup contract (templates/studio/reader.html):
 *   x-data="flipbook({ pages: <n>, rtl: <bool> })" x-init="mount()"
 *   x-ref="stage"  the sized area the book must fit inside
 *   x-ref="book"   the element holding one .reader-page per page
 */
document.addEventListener('alpine:init', () => {
  window.Alpine.data('flipbook', ({ pages = 0, rtl = false } = {}) => ({
    total: pages,
    current: 0,
    thumbs: false,
    shared: false,
    zoom: 1,
    flip: null,

    get label() {
      if (!this.total) return '';
      const spread = this.flip && this.flip.getOrientation && this.flip.getOrientation() === 'landscape';
      const first = this.current + 1;
      if (spread && first < this.total && first > 1) return `${first}–${Math.min(first + 1, this.total)} / ${this.total}`;
      return `${first} / ${this.total}`;
    },

    mount() {
      if (!this.total || !window.St || !window.St.PageFlip) return;
      const size = this.fit();
      this.flip = new window.St.PageFlip(this.$refs.book, {
        width: size.width,
        height: size.height,
        size: 'stretch',
        minWidth: 240,
        maxWidth: 1400,
        minHeight: 320,
        maxHeight: 1900,
        drawShadow: true,
        maxShadowOpacity: 0.4,
        flippingTime: 700,
        usePortrait: true,
        showCover: true,
        mobileScrollSupport: false,
        swipeDistance: 25,
        clickEventForward: false,
        disableFlipByClick: false,
        startPage: this.startPage(),
      });
      this.flip.loadFromHTML(this.$refs.book.querySelectorAll('.reader-page'));
      this.current = this.flip.getCurrentPageIndex();
      this.flip.on('flip', (event) => {
        this.current = event.data;
        this.syncHash();
      });
      window.addEventListener('resize', this.onResize.bind(this));
      window.addEventListener('keydown', this.onKey.bind(this));
    },

    /** Page index from the #page-N fragment, so a shared link opens where it left off. */
    startPage() {
      const match = /^#page-(\d+)$/.exec(window.location.hash);
      if (!match) return 0;
      return Math.min(Math.max(parseInt(match[1], 10) - 1, 0), this.total - 1);
    },

    syncHash() {
      const hash = `#page-${this.current + 1}`;
      if (window.location.hash !== hash) history.replaceState(null, '', hash);
    },

    /** A single page is 3:4; fit the widest two-page spread into the stage. */
    fit() {
      const stage = this.$refs.stage;
      const pad = 48;
      const available = {
        width: Math.max(stage.clientWidth - pad, 240),
        height: Math.max(stage.clientHeight - pad - 28, 300),
      };
      const spread = available.width > 900;
      const perPage = spread ? available.width / 2 : available.width;
      let width = Math.min(perPage, (available.height * 3) / 4);
      return { width: Math.round(width * this.zoom), height: Math.round(((width * 4) / 3) * this.zoom) };
    },

    onResize() {
      if (!this.flip) return;
      const size = this.fit();
      this.flip.update({ width: size.width, height: size.height });
    },

    onKey(event) {
      if (!this.flip || event.target.matches('input, textarea')) return;
      const forward = rtl ? 'ArrowLeft' : 'ArrowRight';
      const back = rtl ? 'ArrowRight' : 'ArrowLeft';
      if (event.key === forward || event.key === 'PageDown') { event.preventDefault(); this.next(); }
      if (event.key === back || event.key === 'PageUp') { event.preventDefault(); this.prev(); }
      if (event.key === 'Home') { event.preventDefault(); this.goto(0); }
      if (event.key === 'End') { event.preventDefault(); this.goto(this.total - 1); }
    },

    next() { if (this.flip) this.flip.flipNext(); },
    prev() { if (this.flip) this.flip.flipPrev(); },
    goto(index) { if (this.flip) this.flip.flip(index); this.thumbs = false; },

    zoomIn() { this.zoom = Math.min(this.zoom + 0.15, 1.8); this.onResize(); },
    zoomOut() { this.zoom = Math.max(this.zoom - 0.15, 0.7); this.onResize(); },

    fullscreen() {
      const el = this.$el;
      if (document.fullscreenElement) document.exitFullscreen();
      else if (el.requestFullscreen) el.requestFullscreen();
    },

    async share() {
      const url = `${window.location.origin}${window.location.pathname}#page-${this.current + 1}`;
      try {
        if (navigator.share) await navigator.share({ url });
        else await navigator.clipboard.writeText(url);
        this.shared = true;
        setTimeout(() => { this.shared = false; }, 2000);
      } catch (error) { /* the viewer cancelled */ }
    },
  }));
});
