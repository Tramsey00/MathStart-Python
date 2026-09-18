
(function () {
  var root = document.getElementById('ms-linear-lab-723');

  if (!root || root.getAttribute('data-ready') === 'true') {
    return;
  }

  root.setAttribute('data-ready', 'true');

  var canvas = root.querySelector('[data-role="canvas"]');
  var kRange = root.querySelector('[data-role="k-range"]');
  var bRange = root.querySelector('[data-role="b-range"]');
  var kOutput = root.querySelector('[data-role="k-output"]');
  var bOutput = root.querySelector('[data-role="b-output"]');
  var formulaOutput = root.querySelector('[data-role="formula"]');
  var directionOutput = root.querySelector('[data-role="direction"]');
  var interceptOutput = root.querySelector('[data-role="intercept"]');
  var xInterceptOutput = root.querySelector('[data-role="x-intercept"]');
  var resetButton = root.querySelector('[data-role="reset"]');
  var context = canvas.getContext('2d');
  var resizeFrame = null;

  function nearlyZero(value) {
    return Math.abs(value) < 0.000001;
  }

  function cleanNumber(value) {
    var rounded = Math.round(value * 100) / 100;
    return nearlyZero(rounded) ? 0 : rounded;
  }

  function formatNumber(value) {
    var cleaned = cleanNumber(value);
    var text = String(cleaned);

    return text
      .replace('.', ',')
      .replace('-', '−');
  }

  function formulaText(k, b) {
    var kClean = cleanNumber(k);
    var bClean = cleanNumber(b);
    var result = 'y = ';

    if (nearlyZero(kClean)) {
      return result + formatNumber(bClean);
    }

    if (kClean === 1) {
      result += 'x';
    } else if (kClean === -1) {
      result += '−x';
    } else {
      result += formatNumber(kClean) + 'x';
    }

    if (bClean > 0) {
      result += ' + ' + formatNumber(bClean);
    } else if (bClean < 0) {
      result += ' − ' + formatNumber(Math.abs(bClean));
    }

    return result;
  }

  function directionText(k) {
    if (k > 0) {
      return 'возрастает';
    }

    if (k < 0) {
      return 'убывает';
    }

    return 'постоянна';
  }

  function xInterceptText(k, b) {
    if (nearlyZero(k)) {
      return nearlyZero(b)
        ? 'график совпадает с осью Ox'
        : 'нет пересечения';
    }

    var x = cleanNumber(-b / k);
    return '(' + formatNumber(x) + '; 0)';
  }

  function roundedRect(ctx, x, y, width, height, radius) {
    var r = Math.min(radius, width / 2, height / 2);

    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + width, y, x + width, y + height, r);
    ctx.arcTo(x + width, y + height, x, y + height, r);
    ctx.arcTo(x, y + height, x, y, r);
    ctx.arcTo(x, y, x + width, y, r);
    ctx.closePath();
  }

  function draw() {
    var rect = canvas.getBoundingClientRect();
    var cssWidth = Math.max(320, rect.width);
    var cssHeight = Math.max(230, rect.height);
    var dpr = window.devicePixelRatio || 1;

    canvas.width = Math.round(cssWidth * dpr);
    canvas.height = Math.round(cssHeight * dpr);

    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.clearRect(0, 0, cssWidth, cssHeight);

    var k = parseFloat(kRange.value);
    var b = parseFloat(bRange.value);

    var margin = {
      left: 52,
      right: 22,
      top: 22,
      bottom: 46
    };

    var plotX = margin.left;
    var plotY = margin.top;
    var plotWidth = cssWidth - margin.left - margin.right;
    var plotHeight = cssHeight - margin.top - margin.bottom;

    var xMin = -8;
    var xMax = 8;
    var yMin = -16;
    var yMax = 16;

    function toCanvasX(x) {
      return plotX + ((x - xMin) / (xMax - xMin)) * plotWidth;
    }

    function toCanvasY(y) {
      return plotY + ((yMax - y) / (yMax - yMin)) * plotHeight;
    }

    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, cssWidth, cssHeight);

    roundedRect(context, plotX, plotY, plotWidth, plotHeight, 12);
    context.fillStyle = '#fbfdff';
    context.fill();

    context.save();
    context.beginPath();
    context.rect(plotX, plotY, plotWidth, plotHeight);
    context.clip();

    context.lineWidth = 1;
    context.strokeStyle = '#e5e7eb';

    for (var gx = xMin; gx <= xMax; gx += 1) {
      var gridX = toCanvasX(gx);

      context.beginPath();
      context.moveTo(gridX, plotY);
      context.lineTo(gridX, plotY + plotHeight);
      context.stroke();
    }

    for (var gy = yMin; gy <= yMax; gy += 2) {
      var gridY = toCanvasY(gy);

      context.beginPath();
      context.moveTo(plotX, gridY);
      context.lineTo(plotX + plotWidth, gridY);
      context.stroke();
    }

    var axisX = toCanvasX(0);
    var axisY = toCanvasY(0);

    context.strokeStyle = '#374151';
    context.lineWidth = 2.5;

    context.beginPath();
    context.moveTo(plotX, axisY);
    context.lineTo(plotX + plotWidth, axisY);
    context.stroke();

    context.beginPath();
    context.moveTo(axisX, plotY);
    context.lineTo(axisX, plotY + plotHeight);
    context.stroke();

    context.strokeStyle = '#2563eb';
    context.lineWidth = 4;
    context.lineCap = 'round';

    context.beginPath();
    context.moveTo(
      toCanvasX(xMin),
      toCanvasY(k * xMin + b)
    );
    context.lineTo(
      toCanvasX(xMax),
      toCanvasY(k * xMax + b)
    );
    context.stroke();

    var interceptX = toCanvasX(0);
    var interceptY = toCanvasY(b);

    context.fillStyle = '#7c3aed';
    context.beginPath();
    context.arc(interceptX, interceptY, 6.5, 0, Math.PI * 2);
    context.fill();

    if (!nearlyZero(k)) {
      var xIntercept = cleanNumber(-b / k);

      if (xIntercept >= xMin && xIntercept <= xMax) {
        context.fillStyle = '#15803d';
        context.beginPath();
        context.arc(
          toCanvasX(xIntercept),
          axisY,
          7,
          0,
          Math.PI * 2
        );
        context.fill();
      }
    }

    context.restore();

    context.fillStyle = '#6b7280';
    context.font = '600 11px Arial, sans-serif';
    context.textAlign = 'center';
    context.textBaseline = 'top';

    for (var tx = xMin; tx <= xMax; tx += 1) {
      context.fillText(
        formatNumber(tx),
        toCanvasX(tx),
        plotY + plotHeight + 10
      );
    }

    context.textAlign = 'right';
    context.textBaseline = 'middle';

    for (var ty = yMin; ty <= yMax; ty += 2) {
      context.fillText(
        formatNumber(ty),
        plotX - 9,
        toCanvasY(ty)
      );
    }

    context.fillStyle = '#374151';
    context.font = '800 14px Arial, sans-serif';
    context.textAlign = 'right';
    context.textBaseline = 'top';

    context.fillText(
      'x',
      plotX + plotWidth,
      plotY + plotHeight + 28
    );

    context.textAlign = 'left';
    context.textBaseline = 'top';

    context.fillText(
      'y',
      plotX + 7,
      plotY + 4
    );
  }

  function update() {
    var k = parseFloat(kRange.value);
    var b = parseFloat(bRange.value);

    kOutput.textContent = formatNumber(k);
    bOutput.textContent = formatNumber(b);

    formulaOutput.textContent = formulaText(k, b);
    directionOutput.textContent = directionText(k);

    interceptOutput.textContent =
      '(0; ' + formatNumber(b) + ')';

    xInterceptOutput.textContent = xInterceptText(k, b);

    draw();
  }

  function scheduleDraw() {
    if (resizeFrame) {
      window.cancelAnimationFrame(resizeFrame);
    }

    resizeFrame = window.requestAnimationFrame(function () {
      draw();
    });
  }

  kRange.addEventListener('input', update);
  bRange.addEventListener('input', update);

  resetButton.addEventListener('click', function () {
    kRange.value = '1';
    bRange.value = '0';

    update();
  });

  if ('ResizeObserver' in window) {
    var observer = new ResizeObserver(scheduleDraw);
    observer.observe(canvas.parentElement);
  } else {
    window.addEventListener('resize', scheduleDraw);
  }

  update();
})();
