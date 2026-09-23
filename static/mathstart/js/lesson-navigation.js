(function () {
  'use strict';
  const root = document.querySelector('.ms-lesson-page');
  if (!root || root.dataset.navigationReady === 'true') return;
  root.addEventListener('click', function (event) {
    if (root.dataset.lessonLayout === 'themed' &&
        !window.matchMedia('(min-width: 901px)').matches) return;
    const link = event.target.closest('a[href^="#"]');
    if (!link || !root.contains(link) || event.button !== 0 ||
        event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const hash = link.getAttribute('href');
    if (hash.length < 2) return;
    let id;
    try { id = decodeURIComponent(hash.slice(1)); } catch (_) { return; }
    const section = document.getElementById(id);
    if (!section || !root.contains(section)) return;
    event.preventDefault();
    event.stopPropagation();
    if (location.hash !== hash) history.pushState(null, '', hash);
    const heading = section.querySelector('h2') || section;
    heading.setAttribute('tabindex', '-1');
    heading.focus({preventScroll: true});
    section.scrollIntoView({
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',
      block: 'start'
    });
  });
  root.dataset.navigationReady = 'true';
})();
