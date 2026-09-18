
(function () {
  var root = document.getElementById('ms-hyperbola-lab-621');

  if (!root || root.getAttribute('data-ready') === 'true') {
    return;
  }

  var canvas = root.querySelector('[data-role="canvas"]');
  var kRange = root.querySelector('[data-role="k-range"]');
  var bRange = root.querySelector('[data-role="b-range"]');
  var kOutput = root.querySelector('[data-role="k-output"]');
  var bOutput = root.querySelector('[data-role="b-output"]');
  var formulaSign = root.querySelector('[data-role="formula-sign"]');
  var formulaFraction = root.querySelector('[data-role="formula-fraction"]');
  var formulaK = root.querySelector('[data-role="formula-k"]');
  var formulaB = root.querySelector('[data-role="formula-b"]');
  var domainOutput = root.querySelector('[data-role="domain"]');
  var rangeOutput = root.querySelector('[data-role="range"]');
  var monotonicOutput = root.querySelector('[data-role="monotonic"]');
  var asymptotesOutput = root.querySelector('[data-role="asymptotes"]');
  var branchesOutput = root.querySelector('[data-role="branches"]');
  var centerOutput = root.querySelector('[data-role="center"]');
  var readout = root.querySelector('[data-role="readout"]');
  var resetButton = root.querySelector('[data-role="reset"]');
  var tableValues = root.querySelectorAll('[data-role="table-value"]');

  if (
    !canvas || !kRange || !bRange || !kOutput || !bOutput ||
    !formulaSign || !formulaFraction || !formulaK || !formulaB ||
    !domainOutput || !rangeOutput || !monotonicOutput ||
    !asymptotesOutput || !branchesOutput || !centerOutput ||
    !readout || !resetButton
  ) {
    return;
  }

  var context = canvas.getContext('2d');

  if (!context) {
    return;
  }

  var resizeFrame = null;
  var hoverX = 1;
  var xMin = -10;
  var xMax = 10;
  var yMin = -10;
  var yMax = 10;
  var singularThreshold = 0.08;

  function nearlyZero(value) {
    return Math.abs(value) < 0.000001;
  }

  function cleanNumber(value) {
    var rounded = Math.round(value * 1000000) / 1000000;
    return nearlyZero(rounded) ? 0 : rounded;
  }

  function formatFixed(value, digits) {
    return cleanNumber(value)
      .toFixed(digits)
      .replace('.', ',')
      .replace('-', '−');
  }

  function formatCompact(value, digits) {
    var text = formatFixed(value, digits);

    if (digits > 0) {
      text = text.replace(/0+$/, '').replace(/,$/, '');
    }

    return text;
  }

  function graphY(x, k, b) {
    return k / x + b;
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

  function updateFormula(k, b) {
    var kClean = cleanNumber(k);
    var bClean = cleanNumber(b);

    formulaSign.textContent = '';
    formulaFraction.style.display = 'inline-flex';
    formulaK.textContent = formatCompact(Math.abs(kClean), 1);

    if (kClean < 0) {
      formulaSign.textContent = '−';
    }

    if (nearlyZero(kClean)) {
      formulaSign.textContent = '';
      formulaFraction.style.display = 'none';
    }

    if (nearlyZero(bClean)) {
      formulaB.textContent = nearlyZero(kClean) ? '0' : '';
    } else if (nearlyZero(kClean)) {
      formulaB.textContent = formatCompact(bClean, 1);
    } else if (bClean > 0) {
      formulaB.textContent = '+ ' + formatCompact(bClean, 1);
    } else {
      formulaB.textContent = '− ' + formatCompact(Math.abs(bClean), 1);
    }
  }

  function updateProperties(k, b) {
    domainOutput.textContent = 'x ≠ 0';
    centerOutput.textContent = '(0; ' + formatCompact(b, 1) + ')';

    if (nearlyZero(k)) {
      rangeOutput.textContent = '{' + formatCompact(b, 1) + '}';
      monotonicOutput.textContent = 'Постоянна на каждом промежутке области определения';
      asymptotesOutput.textContent = 'x = 0';
      branchesOutput.textContent = 'Горизонтальная прямая y = ' + formatCompact(b, 1) + ' с разрывом при x = 0';
    } else {
      rangeOutput.textContent = 'y ≠ ' + formatCompact(b, 1);
      asymptotesOutput.textContent = 'x = 0, y = ' + formatCompact(b, 1);

      if (k > 0) {
        monotonicOutput.textContent = 'Убывает на (−∞; 0) и (0; +∞)';
        branchesOutput.textContent = 'I и III четверти относительно центра';
      } else {
        monotonicOutput.textContent = 'Возрастает на (−∞; 0) и (0; +∞)';
        branchesOutput.textContent = 'II и IV четверти относительно центра';
      }
    }
  }

  function updateTable(k, b) {
    var i;

    for (i = 0; i < tableValues.length; i += 1) {
      var x = parseFloat(tableValues[i].getAttribute('data-x'));
      tableValues[i].textContent = formatCompact(graphY(x, k, b), 2);
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

  function drawBranch(startX, endX, k, b, toCanvasX, toCanvasY) {
    var steps = 700;
    var started = false;
    var sample;

    context.beginPath();

    for (sample = 0; sample <= steps; sample += 1) {
      var x = startX + (endX - startX) * (sample / steps);
      var y = graphY(x, k, b);

      if (!isFinite(y) || y < yMin - 2 || y > yMax + 2) {
        started = false;
        continue;
      }

      var px = toCanvasX(x);
      var py = toCanvasY(y);

      if (!started) {
        context.moveTo(px, py);
        started = true;
      } else {
        context.lineTo(px, py);
      }
    }

    context.stroke();
  }

  function draw() {
    var rect = canvas.getBoundingClientRect();
    var cssWidth = Math.max(300, Math.round(rect.width || 820));
    var cssHeight = Math.max(300, Math.round(rect.height || cssWidth * 460 / 820));
    var dpr = window.devicePixelRatio || 1;
    var targetWidth = Math.round(cssWidth * dpr);
    var targetHeight = Math.round(cssHeight * dpr);

    if (canvas.width !== targetWidth || canvas.height !== targetHeight) {
      canvas.width = targetWidth;
      canvas.height = targetHeight;
    }

    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.clearRect(0, 0, cssWidth, cssHeight);

    var k = parseFloat(kRange.value);
    var b = parseFloat(bRange.value);
    var margin = { left: 58, right: 25, top: 25, bottom: 48 };
    var plotX = margin.left;
    var plotY = margin.top;
    var plotWidth = Math.max(100, cssWidth - margin.left - margin.right);
    var plotHeight = Math.max(100, cssHeight - margin.top - margin.bottom);

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

    var x;
    var y;

    for (x = xMin; x <= xMax; x += 1) {
      context.beginPath();
      context.moveTo(toCanvasX(x), plotY);
      context.lineTo(toCanvasX(x), plotY + plotHeight);
      context.strokeStyle = x % 2 === 0 ? '#dbeafe' : '#eef4fb';
      context.lineWidth = x % 2 === 0 ? 1.1 : 0.8;
      context.stroke();
    }

    for (y = yMin; y <= yMax; y += 1) {
      context.beginPath();
      context.moveTo(plotX, toCanvasY(y));
      context.lineTo(plotX + plotWidth, toCanvasY(y));
      context.strokeStyle = y % 2 === 0 ? '#dbeafe' : '#eef4fb';
      context.lineWidth = y % 2 === 0 ? 1.1 : 0.8;
      context.stroke();
    }

    var axisX = toCanvasX(0);
    var axisY = toCanvasY(0);
    var asymptoteY = toCanvasY(b);

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

    context.save();
    context.setLineDash([7, 6]);
    context.strokeStyle = '#7c3aed';
    context.lineWidth = 1.8;

    context.beginPath();
    context.moveTo(axisX, plotY);
    context.lineTo(axisX, plotY + plotHeight);
    context.stroke();

    if (!nearlyZero(k)) {
      context.beginPath();
      context.moveTo(plotX, asymptoteY);
      context.lineTo(plotX + plotWidth, asymptoteY);
      context.stroke();
    }

    context.restore();

    context.fillStyle = '#7c3aed';
    context.font = '700 12px Arial, sans-serif';
    context.textAlign = 'left';
    context.textBaseline = 'alphabetic';

    if (!nearlyZero(k)) {
      context.fillText(
        'y = ' + formatCompact(b, 1),
        plotX + 8,
        Math.max(plotY + 14, Math.min(plotY + plotHeight - 8, asymptoteY - 8))
      );
    }

    context.strokeStyle = '#2563eb';
    context.lineWidth = 4;
    context.lineCap = 'round';
    context.lineJoin = 'round';

    if (nearlyZero(k)) {
      var flatY = toCanvasY(b);
      context.beginPath();
      context.moveTo(plotX, flatY);
      context.lineTo(axisX - 4, flatY);
      context.moveTo(axisX + 4, flatY);
      context.lineTo(plotX + plotWidth, flatY);
      context.stroke();
    } else {
      drawBranch(xMin, -singularThreshold, k, b, toCanvasX, toCanvasY);
      drawBranch(singularThreshold, xMax, k, b, toCanvasX, toCanvasY);
    }

    var samplePoints = [-4, -2, -1, 1, 2, 4];
    var pointIndex;

    if (!nearlyZero(k)) {
      for (pointIndex = 0; pointIndex < samplePoints.length; pointIndex += 1) {
        x = samplePoints[pointIndex];
        y = graphY(x, k, b);

        if (isFinite(y)) {
          if (y >= yMin) {
            if (y <= yMax) {
              context.beginPath();
              context.arc(toCanvasX(x), toCanvasY(y), 5.2, 0, Math.PI * 2);
              context.fillStyle = '#ffffff';
              context.fill();
              context.strokeStyle = '#64748b';
              context.lineWidth = 2.2;
              context.stroke();
            }
          }
        }
      }
    }

    if (hoverX !== null) {
      if (Math.abs(hoverX) > singularThreshold) {
        y = graphY(hoverX, k, b);

        if (isFinite(y)) {
          if (y >= yMin) {
            if (y <= yMax) {
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
              context.arc(hoverPx, hoverPy, 6, 0, Math.PI * 2);
              context.fillStyle = '#ffffff';
              context.fill();
              context.strokeStyle = '#2563eb';
              context.lineWidth = 3;
              context.stroke();
            }
          }
        }
      }
    }

    context.restore();

    context.fillStyle = '#64748b';
    context.font = '500 12px Arial, sans-serif';
    context.textBaseline = 'middle';

    for (x = xMin; x <= xMax; x += 2) {
      if (x !== 0) {
        context.textAlign = 'center';
        context.fillText(String(x).replace('-', '−'), toCanvasX(x), axisY + 16);
      }
    }

    for (y = yMin; y <= yMax; y += 2) {
      if (y !== 0) {
        context.textAlign = 'right';
        context.fillText(String(y).replace('-', '−'), axisX - 9, toCanvasY(y));
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
    var k = parseFloat(kRange.value);
    var b = parseFloat(bRange.value);

    if (x === null) {
      readout.innerHTML = 'Наведите курсор<br>на график';
      return;
    }

    if (Math.abs(x) <= singularThreshold) {
      readout.innerHTML = 'x = 0 запрещён<br>деление на нуль';
      return;
    }

    readout.innerHTML =
      'x = ' + formatFixed(x, 2) +
      '<br>y = ' + formatFixed(graphY(x, k, b), 2);
  }

  function update() {
    var k = parseFloat(kRange.value);
    var b = parseFloat(bRange.value);

    kOutput.textContent = formatFixed(k, 1);
    bOutput.textContent = formatFixed(b, 1);
    updateFormula(k, b);
    updateProperties(k, b);
    updateTable(k, b);
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
    var cssWidth = Math.max(300, rect.width || 820);
    var marginLeft = 58;
    var marginRight = 25;
    var plotWidth = cssWidth - marginLeft - marginRight;
    var localX = event.clientX - rect.left;
    var x = xMin + ((localX - marginLeft) / plotWidth) * (xMax - xMin);

    if (x < xMin || x > xMax) {
      return null;
    }

    return Math.abs(x) <= singularThreshold ? 0 : x;
  }

  kRange.addEventListener('input', update);
  bRange.addEventListener('input', update);

  resetButton.addEventListener('click', function () {
    kRange.value = '1';
    bRange.value = '0';
    hoverX = 1;
    update();
  });

  canvas.addEventListener('pointermove', function (event) {
    hoverX = pointerToGraphX(event);
    updateReadout(hoverX);
    draw();
  });

  canvas.addEventListener('pointerleave', function () {
    hoverX = 1;
    updateReadout(hoverX);
    draw();
  });

  window.addEventListener('resize', scheduleDraw);

  root.setAttribute('data-ready', 'true');
  update();
  window.requestAnimationFrame(draw);
})();
