
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
  var readout = root.querySelector('[data-role="readout"]');
  var context = canvas.getContext('2d');
  var resizeFrame = null;
  var hoverX = null;
  var xMin = -8;
  var xMax = 8;
  var yMin = -16;
  var yMax = 16;

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

  function drawArrowHead(x, y, direction) {
    context.beginPath();
    context.moveTo(x, y);
    if (direction === 'right') {
      context.lineTo(x - 9, y - 5);
      context.lineTo(x - 9, y + 5);
    } else {
      context.lineTo(x - 5, y + 9);
      context.lineTo(x + 5, y + 9);
    }
    context.closePath();
    context.fill();
  }

  function draw() {
    var rect = canvas.getBoundingClientRect();
    var cssWidth = Math.max(180, rect.width);
    var cssHeight = Math.max(230, rect.height);
    var dpr = window.devicePixelRatio || 1;

    canvas.width = Math.round(cssWidth * dpr);
    canvas.height = Math.round(cssHeight * dpr);

    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.clearRect(0, 0, cssWidth, cssHeight);

    var k = parseFloat(kRange.value);
    var b = parseFloat(bRange.value);

    var margin = {
      left: 58,
      right: 25,
      top: 25,
      bottom: 48
    };

    var plotX = margin.left;
    var plotY = margin.top;
    var plotWidth = cssWidth - margin.left - margin.right;
    var plotHeight = cssHeight - margin.top - margin.bottom;

    function toCanvasX(x) {
      return plotX + ((x - xMin) / (xMax - xMin)) * plotWidth;
    }

    function toCanvasY(y) {
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

    context.lineWidth = 1;
    context.strokeStyle = '#e5e7eb';

    for (var gx = xMin; gx <= xMax; gx += 1) {
      var gridX = toCanvasX(gx);

      context.beginPath();
      context.moveTo(gridX, plotY);
      context.lineTo(gridX, plotY + plotHeight);
      context.strokeStyle = gx % 2 === 0 ? '#dbeafe' : '#eef4fb';
      context.lineWidth = gx % 2 === 0 ? 1.1 : 0.8;
      context.stroke();
    }

    for (var gy = yMin; gy <= yMax; gy += 1) {
      var gridY = toCanvasY(gy);

      context.beginPath();
      context.moveTo(plotX, gridY);
      context.lineTo(plotX + plotWidth, gridY);
      context.strokeStyle = gy % 2 === 0 ? '#dbeafe' : '#eef4fb';
      context.lineWidth = gy % 2 === 0 ? 1.1 : 0.8;
      context.stroke();
    }

    var axisX = toCanvasX(0);
    var axisY = toCanvasY(0);

    context.strokeStyle = '#475569';
    context.fillStyle = '#475569';
    context.lineWidth = 1.8;

    context.beginPath();
    context.moveTo(plotX, axisY);
    context.lineTo(plotX + plotWidth, axisY);
    context.stroke();
    drawArrowHead(plotX + plotWidth, axisY, 'right');

    context.beginPath();
    context.moveTo(axisX, plotY);
    context.lineTo(axisX, plotY + plotHeight);
    context.stroke();
    drawArrowHead(axisX, plotY, 'up');

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

    context.beginPath();
    context.arc(interceptX, interceptY, 7.5, 0, Math.PI * 2);
    context.fillStyle = '#ffffff';
    context.fill();
    context.strokeStyle = '#7c3aed';
    context.lineWidth = 2.6;
    context.stroke();

    if (!nearlyZero(k)) {
      var xIntercept = cleanNumber(-b / k);

      if (xIntercept >= xMin && xIntercept <= xMax) {
        context.fillStyle = '#ffffff';
        context.beginPath();
        context.arc(
          toCanvasX(xIntercept),
          axisY,
          5.5,
          0,
          Math.PI * 2
        );
        context.fill();
        context.strokeStyle = '#16a34a';
        context.lineWidth = 2.6;
        context.stroke();
      }
    }

    if (hoverX !== null) {
      var hoverY = k * hoverX + b;
      if (hoverY >= yMin && hoverY <= yMax) {
        var hoverPx = toCanvasX(hoverX);
        var hoverPy = toCanvasY(hoverY);
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
        context.beginPath();
        context.arc(hoverPx, hoverPy, 6, 0, Math.PI * 2);
        context.fillStyle = '#ffffff';
        context.fill();
        context.strokeStyle = '#2563eb';
        context.lineWidth = 3;
        context.stroke();
      }
    }

    context.restore();

    context.fillStyle = '#64748b';
    context.font = '500 12px Arial, sans-serif';
    context.textBaseline = 'middle';
    for (var tx = xMin; tx <= xMax; tx += 2) {
      if (tx !== 0) {
        context.textAlign = 'center';
        context.fillText(formatNumber(tx), toCanvasX(tx), axisY + 16);
      }
    }
    context.textAlign = 'right';
    for (var ty = yMin; ty <= yMax; ty += 2) {
      if (ty !== 0) {
        context.fillText(formatNumber(ty), axisX - 9, toCanvasY(ty));
      }
    }
    context.fillText('0', axisX - 9, axisY + 16);
    context.fillStyle = '#334155';
    context.font = '700 15px Arial, sans-serif';
    context.textAlign = 'right';
    context.fillText('x', plotX + plotWidth - 3, axisY - 11);
    context.textAlign = 'left';
    context.fillText('y', axisX + 10, plotY + 11);
  }

  function updateReadout() {
    if (hoverX === null) {
      readout.innerHTML = 'Наведите курсор<br>на график';
      return;
    }
    var y = parseFloat(kRange.value) * hoverX + parseFloat(bRange.value);
    function coordinate(value) {
      return cleanNumber(value).toFixed(2).replace('.', ',').replace('-', '−');
    }
    readout.innerHTML = 'x = ' + coordinate(hoverX) + '<br>y = ' + coordinate(y);
  }

  function pointerToGraphX(event) {
    var rect = canvas.getBoundingClientRect();
    var plotWidth = Math.max(180, rect.width) - 58 - 25;
    var x = xMin + ((event.clientX - rect.left - 58) / plotWidth) * (xMax - xMin);
    return x < xMin || x > xMax ? null : x;
  }

  function showPointer(event) {
    hoverX = pointerToGraphX(event);
    updateReadout();
    draw();
  }

  function clearPointer() {
    hoverX = null;
    updateReadout();
    draw();
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
    updateReadout();
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
  canvas.addEventListener('pointermove', showPointer);
  canvas.addEventListener('pointerdown', showPointer);
  canvas.addEventListener('pointerleave', function (event) {
    if (event.pointerType !== 'touch') {
      clearPointer();
    }
  });
  canvas.addEventListener('pointercancel', clearPointer);

  resetButton.addEventListener('click', function () {
    kRange.value = '1';
    bRange.value = '0';
    hoverX = null;
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
