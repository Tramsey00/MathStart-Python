// Fit diagrams to the lesson column; retain a readable full-size view.
  document.querySelectorAll('svg.ms-svg').forEach((svg, index) => {
    const width = svg.viewBox.baseVal.width;
    if (!width || !svg.closest('.ms-figure')) return;
    let wrap = svg.parentElement;
    if (!wrap.classList.contains('ms-svg-wrap')) {
      wrap = document.createElement('div');
      wrap.className = 'ms-svg-wrap';
      svg.before(wrap);
      wrap.append(svg);
    }
    wrap.style.setProperty('--diagram-width', width + 'px');
    if (!wrap.id) wrap.id = 'ms-reader-diagram-' + index;
    wrap.setAttribute('tabindex', '0');
    wrap.setAttribute('role', 'region');
    wrap.setAttribute('aria-label', svg.getAttribute('aria-label') || 'Учебный рисунок');
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'ms-diagram-toggle';
    button.textContent = 'Увеличить рисунок';
    button.setAttribute('aria-controls', wrap.id);
    button.setAttribute('aria-expanded', 'false');
    button.addEventListener('click', () => {
      const expanded = wrap.classList.toggle('ms-diagram-expanded');
      button.setAttribute('aria-expanded', String(expanded));
      button.textContent = expanded ? 'Показать рисунок целиком' : 'Увеличить рисунок';
      if (!expanded) wrap.scrollLeft = 0;
    });
    wrap.after(button);
    const resize = () => { button.hidden = wrap.clientWidth >= width; };
    resize();
    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(wrap);
  });
