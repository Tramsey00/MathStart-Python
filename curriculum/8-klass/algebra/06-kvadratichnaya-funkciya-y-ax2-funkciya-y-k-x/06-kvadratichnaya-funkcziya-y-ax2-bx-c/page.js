
(function () {
  var root = document.getElementById('ms-quadratic-lab-660');

  if (!root || root.getAttribute('data-ready') === 'true') {
    return;
  }

  var canvas = root.querySelector('[data-role="canvas"]');
  var aRange = root.querySelector('[data-role="a-range"]');
  var bRange = root.querySelector('[data-role="b-range"]');
  var cRange = root.querySelector('[data-role="c-range"]');
  var aOutput = root.querySelector('[data-role="a-output"]');
  var bOutput = root.querySelector('[data-role="b-output"]');
  var cOutput = root.querySelector('[data-role="c-output"]');
  var formulaText = root.querySelector('[data-role="formula-text"]');
  var graphTypeOutput = root.querySelector('[data-role="graph-type"]');
  var directionOutput = root.querySelector('[data-role="direction"]');
  var vertexOutput = root.querySelector('[data-role="vertex"]');
  var symmetryOutput = root.querySelector('[data-role="symmetry"]');
  var discriminantOutput = root.querySelector('[data-role="discriminant"]');
  var rootsOutput = root.querySelector('[data-role="roots"]');
  var yInterceptOutput = root.querySelector('[data-role="y-intercept"]');
  var rangeOutput = root.querySelector('[data-role="range"]');
  var readout = root.querySelector('[data-role="readout"]');
  var resetButton = root.querySelector('[data-role="reset"]');
  var tableValues = root.querySelectorAll('[data-role="table-value"]');

  if (!canvas || !aRange || !bRange || !cRange || !aOutput || !bOutput ||
      !cOutput || !formulaText || !graphTypeOutput || !directionOutput ||
      !vertexOutput || !symmetryOutput || !discriminantOutput || !rootsOutput ||
      !yInterceptOutput || !rangeOutput || !readout || !resetButton) {
    return;
  }

  var context = canvas.getContext('2d');
  if (!context) {
    return;
  }

  var resizeFrame = null;
  var hoverX = 2;
  var xMin = -10;
  var xMax = 10;
  var yMin = -10;
  var yMax = 10;

  function nearlyZero(value) {
    return Math.abs(value) < 0.000001;
  }

  function allConditions() {
    var index;

    for (index = 0; index < arguments.length; index += 1) {
      if (!arguments[index]) {
        return false;
      }
    }

    return true;
  }

  function cleanNumber(value) {
    var rounded = Math.round(value * 1000000) / 1000000;
    return nearlyZero(rounded) ? 0 : rounded;
  }

  function formatFixed(value, digits) {
    return cleanNumber(value).toFixed(digits).replace('.', ',').replace('-', '−');
  }

  function formatCompact(value, digits) {
    var text = formatFixed(value, digits);
    if (digits > 0) {
      text = text.replace(/0+$/, '').replace(/,$/, '');
    }
    return text;
  }

  function graphY(x, a, b, c) {
    return a * x * x + b * x + c;
  }

  function addTerm(parts, value, variable) {
    var v = cleanNumber(value);
    if (nearlyZero(v)) {
      return;
    }
    var abs = Math.abs(v);
    var body = (allConditions(variable, nearlyZero(abs - 1)) ? '' : formatCompact(abs, 1)) + variable;
    if (!parts.length) {
      parts.push((v < 0 ? '−' : '') + body);
    } else {
      parts.push((v < 0 ? '− ' : '+ ') + body);
    }
  }

  function polynomialText(a, b, c) {
    var parts = [];
    addTerm(parts, a, 'x²');
    addTerm(parts, b, 'x');
    addTerm(parts, c, '');
    return parts.length ? parts.join(' ') : '0';
  }

  function getData(a, b, c) {
    var data = {
      quadratic: !nearlyZero(a),
      linear: allConditions(nearlyZero(a), !nearlyZero(b)),
      d: null,
      vx: null,
      vy: null,
      roots: []
    };

    if (data.quadratic) {
      data.d = cleanNumber(b * b - 4 * a * c);
      data.vx = cleanNumber(-b / (2 * a));
      data.vy = cleanNumber(graphY(data.vx, a, b, c));

      if (data.d > 0.000001) {
        var sqrtD = Math.sqrt(data.d);
        var r1 = cleanNumber((-b - sqrtD) / (2 * a));
        var r2 = cleanNumber((-b + sqrtD) / (2 * a));
        data.roots = r1 < r2 ? [r1, r2] : [r2, r1];
      } else if (Math.abs(data.d) <= 0.000001) {
        data.roots = [data.vx];
      }
    } else if (data.linear) {
      data.roots = [cleanNumber(-c / b)];
    }

    return data;
  }

  function updateProperties(a, b, c) {
    var data = getData(a, b, c);
    yInterceptOutput.textContent = '(0; ' + formatCompact(c, 2) + ')';

    if (data.quadratic) {
      graphTypeOutput.textContent = 'Парабола';
      directionOutput.textContent = a > 0 ? 'Вверх' : 'Вниз';
      vertexOutput.textContent = 'V(' + formatCompact(data.vx, 2) + '; ' + formatCompact(data.vy, 2) + ')';
      symmetryOutput.textContent = 'x = ' + formatCompact(data.vx, 2);
      discriminantOutput.textContent = 'D = ' + formatCompact(data.d, 2);

      if (data.roots.length === 2) {
        rootsOutput.textContent = 'x₁ = ' + formatCompact(data.roots[0], 2) + ', x₂ = ' + formatCompact(data.roots[1], 2);
      } else if (data.roots.length === 1) {
        rootsOutput.textContent = 'x = ' + formatCompact(data.roots[0], 2);
      } else {
        rootsOutput.textContent = 'Действительных корней нет';
      }

      rangeOutput.textContent = a > 0
        ? '[' + formatCompact(data.vy, 2) + '; +∞)'
        : '(−∞; ' + formatCompact(data.vy, 2) + ']';
    } else if (data.linear) {
      graphTypeOutput.textContent = 'Линейная функция';
      directionOutput.textContent = b > 0 ? 'Прямая возрастает' : 'Прямая убывает';
      vertexOutput.textContent = 'Вершины нет';
      symmetryOutput.textContent = 'Оси симметрии нет';
      discriminantOutput.textContent = 'Не применяется';
      rootsOutput.textContent = 'x = ' + formatCompact(data.roots[0], 2);
      rangeOutput.textContent = 'R';
    } else {
      graphTypeOutput.textContent = 'Постоянная функция';
      directionOutput.textContent = 'Горизонтальная прямая';
      vertexOutput.textContent = 'Вершины нет';
      symmetryOutput.textContent = 'Оси симметрии нет';
      discriminantOutput.textContent = 'Не применяется';
      rootsOutput.textContent = nearlyZero(c) ? 'Любое действительное x' : 'Корней нет';
      rangeOutput.textContent = '{' + formatCompact(c, 2) + '}';
    }
  }

  function updateTable(a, b, c) {
    var i;
    for (i = 0; i < tableValues.length; i += 1) {
      var x = parseFloat(tableValues[i].getAttribute('data-x'));
      tableValues[i].textContent = formatCompact(graphY(x, a, b, c), 2);
    }
  }

  function roundedRect(ctx, x, y, width, height, radius) {
    var r = Math.min(radius, width / 2, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + width, y, x + width, y + height, r);
    ctx.arcTo(x + width, y + height, x, y + height, r);
    ctx.arcTo(x, y + height, x, y, r);
    ctx.arcTo(x, y, x + r, y, r);
    ctx.closePath();
  }

  function arrow(x, y, direction) {
    context.beginPath();
    if (direction === 'right') {
      context.moveTo(x, y);
      context.lineTo(x - 9, y - 5);
      context.lineTo(x - 9, y + 5);
    } else {
      context.moveTo(x, y);
      context.lineTo(x - 5, y + 9);
      context.lineTo(x + 5, y + 9);
    }
    context.closePath();
    context.fill();
  }

  function point(px, py, color, radius) {
    context.beginPath();
    context.arc(px, py, radius, 0, Math.PI * 2);
    context.fillStyle = '#ffffff';
    context.fill();
    context.strokeStyle = color;
    context.lineWidth = 2.6;
    context.stroke();
  }

  function drawCurve(a, b, c, toX, toY) {
    var steps = 1000;
    var started = false;
    var i;
    context.beginPath();
    for (i = 0; i <= steps; i += 1) {
      var x = xMin + (xMax - xMin) * (i / steps);
      var y = graphY(x, a, b, c);
      if (!isFinite(y) || y < yMin - 3 || y > yMax + 3) {
        started = false;
        continue;
      }
      if (!started) {
        context.moveTo(toX(x), toY(y));
        started = true;
      } else {
        context.lineTo(toX(x), toY(y));
      }
    }
    context.stroke();
  }

  function draw() {
    var rect = canvas.getBoundingClientRect();
    var cssWidth = Math.max(300, Math.round(rect.width || 820));
    var cssHeight = Math.max(300, Math.round(rect.height || 500));
    var dpr = window.devicePixelRatio || 1;
    var targetWidth = Math.round(cssWidth * dpr);
    var targetHeight = Math.round(cssHeight * dpr);

    if (canvas.width !== targetWidth || canvas.height !== targetHeight) {
      canvas.width = targetWidth;
      canvas.height = targetHeight;
    }

    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.clearRect(0, 0, cssWidth, cssHeight);

    var a = parseFloat(aRange.value);
    var b = parseFloat(bRange.value);
    var c = parseFloat(cRange.value);
    var data = getData(a, b, c);
    var margin = { left: 58, right: 25, top: 25, bottom: 48 };
    var plotX = margin.left;
    var plotY = margin.top;
    var plotWidth = Math.max(100, cssWidth - margin.left - margin.right);
    var plotHeight = Math.max(100, cssHeight - margin.top - margin.bottom);

    function toX(x) {
      return plotX + ((x - xMin) / (xMax - xMin)) * plotWidth;
    }
    function toY(y) {
      return plotY + ((yMax - y) / (yMax - yMin)) * plotHeight;
    }

    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, cssWidth, cssHeight);
    roundedRect(context, plotX, plotY, plotWidth, plotHeight, 10);
    context.fillStyle = '#ffffff';
    context.fill();
    context.strokeStyle = '#dbeafe';
    context.lineWidth = 1;
    context.stroke();

    context.save();
    context.beginPath();
    context.rect(plotX, plotY, plotWidth, plotHeight);
    context.clip();

    var x, y;
    for (x = xMin; x <= xMax; x += 1) {
      context.beginPath();
      context.moveTo(toX(x), plotY);
      context.lineTo(toX(x), plotY + plotHeight);
      context.strokeStyle = x % 2 === 0 ? '#dbeafe' : '#eef4fb';
      context.lineWidth = x % 2 === 0 ? 1.1 : 0.8;
      context.stroke();
    }
    for (y = yMin; y <= yMax; y += 1) {
      context.beginPath();
      context.moveTo(plotX, toY(y));
      context.lineTo(plotX + plotWidth, toY(y));
      context.strokeStyle = y % 2 === 0 ? '#dbeafe' : '#eef4fb';
      context.lineWidth = y % 2 === 0 ? 1.1 : 0.8;
      context.stroke();
    }

    var axisX = toX(0);
    var axisY = toY(0);
    context.strokeStyle = '#475569';
    context.fillStyle = '#475569';
    context.lineWidth = 1.8;
    context.beginPath();
    context.moveTo(plotX, axisY);
    context.lineTo(plotX + plotWidth, axisY);
    context.stroke();
    arrow(plotX + plotWidth, axisY, 'right');
    context.beginPath();
    context.moveTo(axisX, plotY + plotHeight);
    context.lineTo(axisX, plotY);
    context.stroke();
    arrow(axisX, plotY, 'up');

    if (allConditions(data.quadratic, data.vx >= xMin, data.vx <= xMax)) {
      context.save();
      context.setLineDash([7, 6]);
      context.strokeStyle = '#7c3aed';
      context.lineWidth = 1.7;
      context.beginPath();
      context.moveTo(toX(data.vx), plotY);
      context.lineTo(toX(data.vx), plotY + plotHeight);
      context.stroke();
      context.restore();
      context.fillStyle = '#7c3aed';
      context.font = '700 12px Arial, sans-serif';
      context.textAlign = 'left';
      context.fillText('x = ' + formatCompact(data.vx, 2), toX(data.vx) + 8, plotY + 17);
    }

    context.strokeStyle = '#2563eb';
    context.lineWidth = 4;
    context.lineCap = 'round';
    context.lineJoin = 'round';
    drawCurve(a, b, c, toX, toY);

    if (allConditions(
      data.quadratic,
      data.vx >= xMin,
      data.vx <= xMax,
      data.vy >= yMin,
      data.vy <= yMax
    )) {
      point(toX(data.vx), toY(data.vy), '#111827', 6);
    }

    var i;
    for (i = 0; i < data.roots.length; i += 1) {
      if (allConditions(data.roots[i] >= xMin, data.roots[i] <= xMax)) {
        point(toX(data.roots[i]), toY(0), '#16a34a', 5.5);
      }
    }

    if (allConditions(c >= yMin, c <= yMax)) {
      point(toX(0), toY(c), '#f97316', 5.5);
    }

    if (hoverX !== null) {
      var hoverY = graphY(hoverX, a, b, c);
      if (allConditions(isFinite(hoverY), hoverY >= yMin, hoverY <= yMax)) {
        var hoverPx = toX(hoverX);
        var hoverPy = toY(hoverY);
        context.save();
        context.setLineDash([5, 5]);
        context.strokeStyle = '#93c5fd';
        context.lineWidth = 1.2;
        context.beginPath();
        context.moveTo(hoverPx, plotY);
        context.lineTo(hoverPx, plotY + plotHeight);
        context.stroke();
        context.beginPath();
        context.moveTo(plotX, hoverPy);
        context.lineTo(plotX + plotWidth, hoverPy);
        context.stroke();
        context.restore();
        point(hoverPx, hoverPy, '#2563eb', 6);
      }
    }

    context.restore();
    context.fillStyle = '#64748b';
    context.font = '500 12px Arial, sans-serif';
    context.textBaseline = 'middle';
    for (x = xMin; x <= xMax; x += 2) {
      if (x !== 0) {
        context.textAlign = 'center';
        context.fillText(String(x).replace('-', '−'), toX(x), axisY + 16);
      }
    }
    for (y = yMin; y <= yMax; y += 2) {
      if (y !== 0) {
        context.textAlign = 'right';
        context.fillText(String(y).replace('-', '−'), axisX - 9, toY(y));
      }
    }
    context.textAlign = 'right';
    context.fillText('0', axisX - 9, axisY + 16);
    context.fillStyle = '#334155';
    context.font = '700 15px Arial, sans-serif';
    context.textAlign = 'right';
    context.fillText('x', plotX + plotWidth - 3, axisY - 11);
    context.textAlign = 'left';
    context.fillText('y', axisX + 10, plotY + 11);
  }

  function updateReadout(x) {
    if (x === null) {
      readout.innerHTML = 'Наведите курсор<br>на график';
      return;
    }
    var y = graphY(x, parseFloat(aRange.value), parseFloat(bRange.value), parseFloat(cRange.value));
    readout.innerHTML = 'x = ' + formatFixed(x, 2) + '<br>y = ' + formatFixed(y, 2);
  }

  function update() {
    var a = parseFloat(aRange.value);
    var b = parseFloat(bRange.value);
    var c = parseFloat(cRange.value);
    aOutput.textContent = formatFixed(a, 1);
    bOutput.textContent = formatFixed(b, 1);
    cOutput.textContent = formatFixed(c, 1);
    formulaText.textContent = polynomialText(a, b, c);
    updateProperties(a, b, c);
    updateTable(a, b, c);
    updateReadout(hoverX);
    draw();
  }

  function scheduleDraw() {
    if (resizeFrame) {
      window.cancelAnimationFrame(resizeFrame);
    }
    resizeFrame = window.requestAnimationFrame(draw);
  }

  function pointerToGraphX(event) {
    var rect = canvas.getBoundingClientRect();
    var width = Math.max(300, rect.width || 820);
    var plotWidth = width - 58 - 25;
    var x = xMin + ((event.clientX - rect.left - 58) / plotWidth) * (xMax - xMin);
    return x < xMin || x > xMax ? null : x;
  }

  aRange.addEventListener('input', update);
  bRange.addEventListener('input', update);
  cRange.addEventListener('input', update);

  resetButton.addEventListener('click', function () {
    aRange.value = '1';
    bRange.value = '-4';
    cRange.value = '3';
    hoverX = 2;
    update();
  });

  canvas.addEventListener('pointermove', function (event) {
    hoverX = pointerToGraphX(event);
    updateReadout(hoverX);
    draw();
  });

  canvas.addEventListener('pointerleave', function () {
    hoverX = 2;
    updateReadout(hoverX);
    draw();
  });

  window.addEventListener('resize', scheduleDraw);
  root.setAttribute('data-ready', 'true');
  update();
  window.requestAnimationFrame(draw);
})();
