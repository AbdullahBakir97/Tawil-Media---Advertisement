/**
 * Focal point picker. Clicking (or dragging) on the picture moves the point that
 * every crop keeps in view; the three previews show what a wide, a square and a
 * tall crop would look like. The value is posted as two numbers between 0 and 1.
 *
 * Markup contract (templates/studio/partials/media_details.html):
 *   x-data="focal({ x: 0.5, y: 0.5 })"  →  pick($event), reset(), x, y
 */
document.addEventListener('alpine:init', () => {
  window.Alpine.data('focal', (start = {}) => ({
    x: typeof start.x === 'number' ? start.x : 0.5,
    y: typeof start.y === 'number' ? start.y : 0.5,

    pick(event) {
      const box = event.currentTarget.getBoundingClientRect();
      if (!box.width || !box.height) return;
      this.x = clamp((event.clientX - box.left) / box.width);
      this.y = clamp((event.clientY - box.top) / box.height);
    },

    reset() {
      this.x = 0.5;
      this.y = 0.5;
    },
  }));
});

function clamp(value) {
  return Math.min(1, Math.max(0, Number.isFinite(value) ? value : 0.5));
}
