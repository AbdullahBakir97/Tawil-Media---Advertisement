/**
 * Motion system built on GSAP + ScrollTrigger (vendored in static/js/vendor).
 *
 * Templates opt in with data attributes instead of writing JavaScript:
 *
 *   data-motion="fade-up"          element rises and fades in when it scrolls into view
 *   data-motion="fade-in"          opacity only
 *   data-motion="slide-start"      slides in from the reading start (RTL-aware)
 *   data-motion="scale-in"         subtle zoom
 *   data-motion="stagger"          each direct child animates in sequence
 *   data-motion="count"            counts a number up (reads data-count / data-suffix)
 *   data-motion="words"            headline words rise one by one
 *   data-motion="parallax"         background drifts with scroll (data-speed="0.2")
 *   data-motion-delay="0.2"        extra delay in seconds
 *   data-motion-once="false"       replay every time it enters the viewport
 *
 * Elements start visible (no opacity:0 in CSS) so the page reads correctly
 * without JavaScript, in reader modes and in thumbnails. GSAP animates *from*
 * the hidden state. Reduced-motion users get static pages.
 */

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const isRtl = () => document.documentElement.dir === 'rtl';

const EASE = 'power3.out';
const DUR = 0.7;

function readNumber(el, attr, fallback) {
  const v = parseFloat(el.dataset[attr]);
  return Number.isFinite(v) ? v : fallback;
}

function fromFor(kind) {
  const x = (isRtl() ? 1 : -1) * 32;
  switch (kind) {
    case 'fade-in': return { opacity: 0 };
    case 'slide-start': return { opacity: 0, x };
    case 'scale-in': return { opacity: 0, scale: 0.94 };
    case 'fade-up':
    default: return { opacity: 0, y: 24 };
  }
}

function splitWords(el) {
  if (el.dataset.motionSplit) return el.querySelectorAll('.motion-word');
  const text = el.textContent;
  el.textContent = '';
  text.split(/(\s+)/).forEach((part) => {
    if (!part) return;
    if (/^\s+$/.test(part)) { el.appendChild(document.createTextNode(' ')); return; }
    const span = document.createElement('span');
    span.className = 'motion-word';
    span.textContent = part;
    el.appendChild(span);
  });
  el.dataset.motionSplit = '1';
  return el.querySelectorAll('.motion-word');
}

function countUp(el) {
  const target = readNumber(el, 'count', parseFloat(el.textContent) || 0);
  const suffix = el.dataset.suffix || '';
  const prefix = el.dataset.prefix || '';
  const decimals = readNumber(el, 'decimals', 0);
  const obj = { v: 0 };
  return window.gsap.to(obj, {
    v: target,
    duration: 1.4,
    ease: 'power2.out',
    onUpdate() {
      el.textContent = prefix + obj.v.toLocaleString(document.documentElement.lang || undefined, {
        minimumFractionDigits: decimals, maximumFractionDigits: decimals,
      }) + suffix;
    },
  });
}

function animate(el) {
  const gsap = window.gsap;
  const kind = el.dataset.motion;
  const delay = readNumber(el, 'motionDelay', 0);
  const once = el.dataset.motionOnce !== 'false';
  const trigger = { trigger: el, start: 'top 85%', once, toggleActions: once ? 'play none none none' : 'play none none reverse' };

  if (kind === 'parallax') {
    gsap.to(el, { yPercent: readNumber(el, 'speed', 0.2) * 100, ease: 'none',
      scrollTrigger: { trigger: el.parentElement || el, start: 'top bottom', end: 'bottom top', scrub: true } });
    return;
  }
  if (kind === 'count') {
    window.ScrollTrigger.create({ ...trigger, onEnter: () => countUp(el) });
    return;
  }
  if (kind === 'words') {
    const words = splitWords(el);
    gsap.from(words, { opacity: 0, y: '0.6em', rotateX: -30, duration: 0.8, ease: EASE, stagger: 0.05, delay, scrollTrigger: trigger });
    return;
  }
  if (kind === 'stagger') {
    const children = Array.from(el.children);
    gsap.from(children, { ...fromFor(el.dataset.motionChild || 'fade-up'), duration: DUR, ease: EASE, stagger: readNumber(el, 'stagger', 0.1), delay, scrollTrigger: trigger });
    return;
  }
  gsap.from(el, { ...fromFor(kind), duration: DUR, ease: EASE, delay, scrollTrigger: trigger });
}

/** Animate every [data-motion] inside root that hasn't been processed. */
export function initMotion(root = document) {
  if (reduced || !window.gsap || !window.ScrollTrigger) return;
  window.gsap.registerPlugin(window.ScrollTrigger);
  root.querySelectorAll('[data-motion]').forEach((el) => {
    if (el.dataset.motionReady) return;
    el.dataset.motionReady = '1';
    animate(el);
  });
}

/**
 * Page-load choreography for the home hero. Called once; elements are picked
 * up via [data-hero-item] in DOM order.
 */
export function playHero(container = document) {
  if (reduced || !window.gsap) return;
  const items = container.querySelectorAll('[data-hero-item]');
  if (!items.length) return;
  const tl = window.gsap.timeline({ defaults: { ease: EASE } });
  tl.from(items, { opacity: 0, y: 28, duration: 0.8, stagger: 0.12 });
  const bg = container.querySelector('[data-hero-bg]');
  if (bg) tl.from(bg, { scale: 1.08, duration: 1.6, ease: 'power2.out' }, 0);
  return tl;
}

/** Hover lift for cards, RTL-agnostic (Y only). Uses CSS by default; GSAP adds spring. */
export function initHoverLift(root = document) {
  if (reduced || !window.gsap) return;
  root.querySelectorAll('[data-lift]').forEach((el) => {
    if (el.dataset.liftReady) return;
    el.dataset.liftReady = '1';
    el.addEventListener('mouseenter', () => window.gsap.to(el, { y: -4, duration: 0.35, ease: 'back.out(2)' }));
    el.addEventListener('mouseleave', () => window.gsap.to(el, { y: 0, duration: 0.35, ease: 'power2.out' }));
  });
}

/** Re-run after HTMX swaps so new content animates in. */
export function bindHtmx() {
  document.body.addEventListener('htmx:afterSettle', (evt) => {
    initMotion(evt.detail.elt || document);
    initHoverLift(evt.detail.elt || document);
  });
}

export default { initMotion, playHero, initHoverLift, bindHtmx };
