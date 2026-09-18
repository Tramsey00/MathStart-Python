(function () {
  'use strict';
  const root = document.getElementById('power-lab-v2');
  if (!root || root.getAttribute('data-ready') === 'true') return;
  const api = window.MathStartMath, plot = root.querySelector('[data-role="plot"]');
  const presets = Array.from(root.querySelectorAll('[data-n]'));
  const index = root.querySelector('#power-index-v2'), argument = root.querySelector('#power-x-v2');
  const reference = root.querySelector('[data-role="reference"]');
  const output = name => root.querySelector('[data-output="' + name + '"]');
  const fmt = value => Math.abs(value) < 1e-10 ? '0' : Number(value.toFixed(4)).toString().replace('.', ',').replace('-', '−');
  const fraction = (a, b) => '<span class="v2-frac"><span>' + a + '</span><span>' + b + '</span></span>';
  const exponent = (a, b) => b === 1 ? fmt(a) : (a < 0 ? '−' : '') + fraction(Math.abs(a), b);
  let n = 2, d = 1, x = 1, hoverX = null, frame = null;
  const lo = -3, hi = 3, top = 25, bottom = 452, left = 58;
  let width = 640, right = 615;
  const px = value => left + (value - lo) * (right - left) / (hi - lo);
  const py = value => bottom - (value - lo) * (bottom - top) / (hi - lo);

  function axes() {
    const ox = px(0), oy = py(0);
    let svg = '<defs><clipPath id="power-v2-clip"><rect x="' + left + '" y="' + top + '" width="' + (right - left) + '" height="' + (bottom - top) + '"/></clipPath></defs>';
    svg += '<rect x="' + left + '" y="' + top + '" width="' + (right - left) + '" height="' + (bottom - top) + '" rx="10" fill="#ffffff" stroke="#dbeafe"/>';
    if (d !== 1) svg += '<rect x="' + left + '" y="' + top + '" width="' + (ox - left) + '" height="' + (bottom - top) + '" fill="#f4f6fa" clip-path="url(#power-v2-clip)"/>';
    for (let k = -3; k <= 3; k += 0.5) {
      const major = Number.isInteger(k);
      svg += '<path d="M' + left + ' ' + py(k) + ' H' + right + ' M' + px(k) + ' ' + top + ' V' + bottom + '" fill="none" stroke="' + (major ? '#dbeafe' : '#eef4fb') + '" stroke-width="' + (major ? '1.1' : '0.8') + '"/>';
    }
    svg += '<path d="M' + left + ' ' + oy + ' H' + right + ' M' + ox + ' ' + bottom + ' V' + top + '" stroke="#475569" stroke-width="1.8" fill="none"/>';
    svg += '<path d="M' + right + ' ' + oy + ' l-9 -5 v10z M' + ox + ' ' + top + ' l-5 9 h10z" fill="#475569"/>';
    if (reference.checked) svg += '<path d="M' + left + ' ' + bottom + ' L' + right + ' ' + top + '" fill="none" stroke="#7c3aed" stroke-width="1.7" stroke-dasharray="7 6"/>';
    return svg;
  }

  function labels() {
    const ox = px(0), oy = py(0);
    let svg = '<g fill="#64748b" font-family="Arial, sans-serif" font-size="12" font-weight="500">';
    for (let k = -3; k <= 3; k++) {
      if (k === 0) continue;
      svg += '<text x="' + px(k) + '" y="' + (oy + 19) + '" text-anchor="middle">' + fmt(k) + '</text>';
      svg += '<text x="' + (ox - 9) + '" y="' + (py(k) + 4) + '" text-anchor="end">' + fmt(k) + '</text>';
    }
    svg += '<text x="' + (ox - 9) + '" y="' + (oy + 19) + '" text-anchor="end">0</text></g>';
    svg += '<g fill="#334155" font-family="Arial, sans-serif" font-size="15" font-weight="700"><text x="' + (right - 3) + '" y="' + (oy - 11) + '" text-anchor="end">x</text><text x="' + (ox + 10) + '" y="' + (top + 12) + '">y</text></g>';
    return svg;
  }

  function draw() {
    width = Math.max(300, Math.round(plot.getBoundingClientRect().width || 640));
    right = width - 25;
    plot.setAttribute('viewBox', '0 0 ' + width + ' 500');
    let svg = axes();
    for (const branch of api.powerBranches(n, d)) {
      const path = branch.map(([a, b], i) => (i ? 'L' : 'M') + px(a).toFixed(3) + ',' + py(b).toFixed(3)).join(' ');
      svg += '<path data-curve="' + n + ',' + d + '" d="' + path + '" clip-path="url(#power-v2-clip)" stroke="#2563eb" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" fill="none"/>';
    }
    if (n === 0) svg += '<circle data-role="excluded-point" cx="' + px(0) + '" cy="' + py(1) + '" r="5.5" fill="white" stroke="#2563eb" stroke-width="2.6"/>';
    const pointX = hoverX === null ? x : hoverX;
    const y = api.powerValue(pointX, n, d);
    let message = 'При x = ' + fmt(pointX) + ': ';
    if (y === null) {
      message += '<strong>функция не определена.</strong> ' + (pointX === 0 ? 'Нулевое основание здесь запрещено.' : 'Для этого дробного показателя требуется ' + (n < 0 ? 'положительное' : 'неотрицательное') + ' основание.');
      output('readout').innerHTML = 'x = ' + fmt(pointX) + '<br>y не определён';
    } else {
      message += 'y = <strong>' + fmt(y) + '</strong>.';
      output('readout').innerHTML = 'x = ' + fmt(pointX) + '<br>y = ' + fmt(y);
      if (y >= lo && y <= hi) {
        svg += '<path d="M' + px(pointX) + ' ' + top + ' V' + bottom + ' M' + left + ' ' + py(y) + ' H' + right + '" stroke="#93c5fd" stroke-width="1.2" stroke-dasharray="5 5" fill="none"/>';
        svg += '<circle data-role="point" data-x="' + pointX + '" data-y="' + y + '" cx="' + px(pointX) + '" cy="' + py(y) + '" r="5.5" fill="#fff" stroke="#f97316" stroke-width="2.6"/>';
      } else message += ' Точка находится за пределами окна графика.';
    }
    svg += labels();
    plot.innerHTML = svg;
    plot.setAttribute('data-n', n);
    plot.setAttribute('data-d', d);
    plot.setAttribute('aria-label', 'График y равно x в степени ' + n + (d === 1 ? '' : ' делённое на ' + d));
    output('point').innerHTML = message;
    output('point').setAttribute('data-valid', String(y !== null));
    output('argument').textContent = fmt(x);
    root.querySelector('[data-role="reference-legend"]').hidden = !reference.checked;
  }

  function setExponent(i) {
    i = Math.max(0, Math.min(presets.length - 1, i));
    n = Number(presets[i].dataset.n);
    d = Number(presets[i].dataset.d);
    index.value = i;
    hoverX = null;
    index.setAttribute('aria-valuetext', n + (d === 1 ? '' : ' делённое на ' + d));
    presets.forEach((button, j) => button.setAttribute('aria-pressed', String(i === j)));
    output('formula').innerHTML = '<span>y =</span><span class="v2-power"><span class="ms-power-base">x</span><sup>' + exponent(n, d) + '</sup></span>';
    output('exponent').innerHTML = exponent(n, d);
    const props = api.powerProperties(n, d);
    root.querySelectorAll('[data-prop]').forEach(element => { element.textContent = props[element.dataset.prop]; });
    root.querySelectorAll('[data-role="table-value"]').forEach(element => {
      const value = api.powerValue(Number(element.dataset.x), n, d);
      element.textContent = value === null ? 'не определено' : fmt(value);
    });
    draw();
  }

  presets.forEach((button, i) => button.addEventListener('click', () => setExponent(i)));
  index.addEventListener('input', () => setExponent(Number(index.value)));
  argument.addEventListener('input', () => { x = Number(argument.value); hoverX = null; draw(); });
  reference.addEventListener('change', draw);
  root.querySelector('[data-action="reset"]').addEventListener('click', () => {
    x = 1;
    argument.value = 1;
    reference.checked = false;
    setExponent(9);
  });
  plot.addEventListener('pointermove', event => {
    const rect = plot.getBoundingClientRect();
    const candidate = lo + (event.clientX - rect.left - left) * (hi - lo) / (right - left);
    hoverX = candidate < lo || candidate > hi ? null : Math.round(candidate * 100) / 100;
    if (frame === null) frame = window.requestAnimationFrame(() => { frame = null; draw(); });
  });
  plot.addEventListener('pointerleave', () => { hoverX = null; draw(); });
  if (typeof ResizeObserver === 'function') {
    new ResizeObserver(() => {
      if (Math.round(plot.getBoundingClientRect().width) !== width) draw();
    }).observe(plot.parentElement);
  }
  setExponent(9);
  root.setAttribute('data-ready', 'true');
})();
