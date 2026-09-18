
(function () {
  var root = document.getElementById('ms-root-lab-832');

  if (!root || root.getAttribute('data-ready') === 'true') {
    return;
  }

  var canvas = root.querySelector('[data-role="canvas"]');
  var kRange = root.querySelector('[data-role="k-range"]');
  var aRange = root.querySelector('[data-role="a-range"]');
  var kOutput = root.querySelector('[data-role="k-output"]');
  var aOutput = root.querySelector('[data-role="a-output"]');
  var formulaK = root.querySelector('[data-role="formula-k"]');
  var formulaA = root.querySelector('[data-role="formula-a"]');
  var domainOutput = root.querySelector('[data-role="domain"]');
  var rangeOutput = root.querySelector('[data-role="range"]');
  var monotonicOutput = root.querySelector('[data-role="monotonic"]');
  var startPointOutput = root.querySelector('[data-role="start-point"]');
  var readout = root.querySelector('[data-role="readout"]');
  var resetButton = root.querySelector('[data-role="reset"]');
  var tableValues = root.querySelectorAll('[data-role="table-value"]');

  if (
    !canvas ||
    !kRange ||
    !aRange ||
    !kOutput ||
    !aOutput ||
    !formulaK ||
    !formulaA ||
    !domainOutput ||
    !rangeOutput ||
    !monotonicOutput ||
    !startPointOutput ||
    !readout ||
    !resetButton
  ) {
    return;
  }

  var context = canvas.getContext('2d');

  if (!context) {
    return;
  }

  root.setAttribute('data-ready', 'true');

  var resizeFrame = null;
  var hoverX = null;

  var xMin = -2;
  var xMax = 18;
  var yMin = -8;
  var yMax = 8;

  function nearlyZero(value) {
    return Math.abs(value) < 0.000001;
  }

  function cleanNumber(value) {
    var rounded = Math.round(value * 1000000) / 1000000;
    return nearlyZero(rounded) ? 0 : rounded;
  }

  function formatFixed(value, digits) {
    var cleaned = cleanNumber(value);

    return cleaned
      .toFixed(digits)
      .replace('.', ',')
      .replace('-', '−');
  }

  function formatCompact(value, digits) {
    var text = formatFixed(value, digits);

    if (digits > 0) {
      text = text
        .replace(/0+$/, '')
        .replace(/,$/, '');
    }

    return text;
  }

  function graphY(x, k, a) {
    return k * Math.sqrt(Math.max(0, x)) + a;
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

  function updateFormula(k, a) {
    var kClean = cleanNumber(k);
    var aClean = cleanNumber(a);

    if (kClean === 1) {
      formulaK.textContent = '';
    } else if (kClean === -1) {
      formulaK.textContent = '−';
    } else {
      formulaK.textContent = formatCompact(kClean, 1) + '·';
    }

    if (nearlyZero(aClean)) {
      formulaA.textContent = '';
    } else if (aClean > 0) {
      formulaA.textContent = '+ ' + formatCompact(aClean, 1);
    } else {
      formulaA.textContent = '− ' + formatCompact(Math.abs(aClean), 1);
    }
  }

  function updateProperties(k, a) {
    domainOutput.textContent = '[0; +∞)';
    startPointOutput.textContent =
      '(0; ' + formatCompact(a, 1) + ')';

    if (k > 0.000001) {
      rangeOutput.textContent =
        '[' + formatCompact(a, 1) + '; +∞)';
      monotonicOutput.textContent = 'Возрастает';
    } else if (k < -0.000001) {
      rangeOutput.textContent =
        '(−∞; ' + formatCompact(a, 1) + ']';
      monotonicOutput.textContent = 'Убывает';
    } else {
      rangeOutput.textContent =
        '{' + formatCompact(a, 1) + '}';
      monotonicOutput.textContent = 'Постоянна';
    }
  }

  function updateTable(k, a) {
    var i;

    for (i = 0; i < tableValues.length; i += 1) {
      var x = parseFloat(tableValues[i].getAttribute('data-x'));
      var y = graphY(x, k, a);

      tableValues[i].textContent = formatCompact(y, 2);
    }
  }

  function drawArrowHead(x, y, direction) {
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

  function draw() {
    var rect = canvas.getBoundingClientRect();
    var cssWidth = Math.max(280, rect.width || 820);
    var cssHeight = Math.max(260, rect.height || 460);
    var dpr = window.devicePixelRatio || 1;

    var targetWidth = Math.round(cssWidth * dpr);
    var targetHeight = Math.round(cssHeight * dpr);

    if (
      canvas.width !== targetWidth ||
      canvas.height !== targetHeight
    ) {
      canvas.width = targetWidth;
      canvas.height = targetHeight;
    }

    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.clearRect(0, 0, cssWidth, cssHeight);

    var k = parseFloat(kRange.value);
    var a = parseFloat(aRange.value);

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
      return plotX +
        ((x - xMin) / (xMax - xMin)) * plotWidth;
    }

    function toCanvasY(y) {
      return plotY +
        ((yMax - y) / (yMax - yMin)) * plotHeight;
    }

    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, cssWidth, cssHeight);

    roundedRect(
      context,
      plotX,
      plotY,
      plotWidth,
      plotHeight,
      10
    );
    context.fillStyle = '#ffffff';
    context.fill();
    context.strokeStyle = '#dbeafe';
    context.lineWidth = 1;
    context.stroke();

    context.save();
    context.beginPath();
    context.rect(plotX, plotY, plotWidth, plotHeight);
    context.clip();

    var x;
    var y;

    for (x = Math.ceil(xMin); x <= Math.floor(xMax); x += 1) {
      context.beginPath();
      context.moveTo(toCanvasX(x), plotY);
      context.lineTo(toCanvasX(x), plotY + plotHeight);
      context.strokeStyle =
        x % 2 === 0 ? '#dbeafe' : '#eef4fb';
      context.lineWidth =
        x % 2 === 0 ? 1.1 : 0.8;
      context.stroke();
    }

    for (y = Math.ceil(yMin); y <= Math.floor(yMax); y += 1) {
      context.beginPath();
      context.moveTo(plotX, toCanvasY(y));
      context.lineTo(plotX + plotWidth, toCanvasY(y));
      context.strokeStyle =
        y % 2 === 0 ? '#dbeafe' : '#eef4fb';
      context.lineWidth =
        y % 2 === 0 ? 1.1 : 0.8;
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
    context.moveTo(axisX, plotY + plotHeight);
    context.lineTo(axisX, plotY);
    context.stroke();
    drawArrowHead(axisX, plotY, 'up');

    context.strokeStyle = '#2563eb';
    context.lineWidth = 4;
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.beginPath();

    var samples = 420;

    for (var sample = 0; sample <= samples; sample += 1) {
      x = xMax * sample / samples;
      y = graphY(x, k, a);

      if (sample === 0) {
        context.moveTo(toCanvasX(x), toCanvasY(y));
      } else {
        context.lineTo(toCanvasX(x), toCanvasY(y));
      }
    }

    context.stroke();

    var samplePoints = [0, 1, 4, 9, 16];

    for (var pointIndex = 0; pointIndex < samplePoints.length; pointIndex += 1) {
      x = samplePoints[pointIndex];
      y = graphY(x, k, a);

      if (y >= yMin && y <= yMax) {
        context.beginPath();
        context.arc(
          toCanvasX(x),
          toCanvasY(y),
          5.2,
          0,
          Math.PI * 2
        );
        context.fillStyle = '#ffffff';
        context.fill();
        context.strokeStyle = '#64748b';
        context.lineWidth = 2.2;
        context.stroke();
      }
    }

    if (hoverX !== null) {
      y = graphY(hoverX, k, a);

      if (y >= yMin && y <= yMax) {
        var hoverPx = toCanvasX(hoverX);
        var hoverPy = toCanvasY(y);

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
        context.arc(
          hoverPx,
          hoverPy,
          6,
          0,
          Math.PI * 2
        );
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

    for (x = Math.ceil(xMin); x <= Math.floor(xMax); x += 2) {
      if (x !== 0) {
        context.textAlign = 'center';
        context.fillText(
          String(x).replace('-', '−'),
          toCanvasX(x),
          axisY + 16
        );
      }
    }

    for (y = Math.ceil(yMin); y <= Math.floor(yMax); y += 2) {
      if (y !== 0) {
        context.textAlign = 'right';
        context.fillText(
          String(y).replace('-', '−'),
          axisX - 9,
          toCanvasY(y)
        );
      }
    }

    context.textAlign = 'right';
    context.fillText('0', axisX - 9, axisY + 16);

    context.fillStyle = '#334155';
    context.font = '700 15px Arial, sans-serif';

    context.textAlign = 'right';
    context.fillText(
      'x',
      plotX + plotWidth - 3,
      axisY - 11
    );

    context.textAlign = 'left';
    context.fillText(
      'y',
      axisX + 10,
      plotY + 11
    );
  }

  function updateReadout(x) {
    var k = parseFloat(kRange.value);
    var a = parseFloat(aRange.value);
    var y = graphY(x, k, a);

    readout.innerHTML =
      'x = ' + formatFixed(x, 2) +
      '<br>y = ' + formatFixed(y, 2);
  }

  function update() {
    var k = parseFloat(kRange.value);
    var a = parseFloat(aRange.value);

    kOutput.textContent = formatFixed(k, 1);
    aOutput.textContent = formatFixed(a, 1);

    updateFormula(k, a);
    updateProperties(k, a);
    updateTable(k, a);

    if (hoverX === null) {
      readout.innerHTML =
        'x = 0,00<br>y = ' + formatFixed(a, 2);
    } else {
      updateReadout(hoverX);
    }

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

  function pointerToGraphX(event) {
    var rect = canvas.getBoundingClientRect();
    var cssWidth = rect.width || 820;
    var marginLeft = 58;
    var marginRight = 25;
    var plotWidth = cssWidth - marginLeft - marginRight;
    var localX = event.clientX - rect.left;
    var x =
      xMin +
      ((localX - marginLeft) / plotWidth) *
      (xMax - xMin);

    if (x < 0 || x > xMax) {
      return null;
    }

    return x;
  }

  kRange.addEventListener('input', update);
  aRange.addEventListener('input', update);

  resetButton.addEventListener('click', function () {
    kRange.value = '1';
    aRange.value = '0';
    hoverX = null;
    update();
  });

  canvas.addEventListener('pointermove', function (event) {
    hoverX = pointerToGraphX(event);

    if (hoverX === null) {
      readout.innerHTML =
        'x = 0,00<br>y = ' +
        formatFixed(parseFloat(aRange.value), 2);
    } else {
      updateReadout(hoverX);
    }

    draw();
  });

  canvas.addEventListener('pointerleave', function () {
    hoverX = null;
    readout.innerHTML =
      'x = 0,00<br>y = ' +
      formatFixed(parseFloat(aRange.value), 2);
    draw();
  });

  if ('ResizeObserver' in window) {
    var observer = new ResizeObserver(scheduleDraw);
    observer.observe(canvas.parentElement);
  } else {
    window.addEventListener('resize', scheduleDraw);
  }

  update();
})();
