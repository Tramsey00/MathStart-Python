"""Power-function laboratory in the site's established graph layout."""

from .layout import F


PRESETS = [(-3, 1), (-2, 1), (-1, 1), (-1, 2), (0, 1), (1, 2),
           (2, 3), (1, 1), (3, 2), (2, 1), (3, 1), (4, 1)]


def exponent(n, d):
    return str(n).replace('-', '−') if d == 1 else ('−' if n < 0 else '') + F(abs(n), d)


def laboratory():
    buttons = ''.join(
        f'<button type="button" class="ms-power-preset" data-n="{n}" data-d="{d}" '
        f'aria-label="Показатель {str(n).replace("-", "минус ")}'
        f'{"" if d == 1 else " делённое на " + str(d)}" '
        f'aria-pressed="{str((n, d) == (2, 1)).lower()}">'
        f'<span class="v2-power"><span class="ms-power-base">x</span><sup>{exponent(n, d)}</sup></span>'
        '</button>' for n, d in PRESETS
    )
    values = [(-2, '4'), (-1, '1'), (0, '0'), (0.25, '0,0625'), (1, '1'), (2, '4')]
    value_cells = ''.join(
        f'<div class="ms-live-table-cell"><strong>x = {str(x).replace("-", "−").replace(".", ",")}</strong>'
        f'<span data-role="table-value" data-x="{x}">{y}</span></div>' for x, y in values
    )
    return f'''<div class="ms-graph-lab" id="power-lab-v2" data-ms-power-lab="true">
      <div class="ms-graph-lab-head">
        <div class="ms-live-formula" data-output="formula" aria-live="polite">y = x²</div>
        <button class="ms-reset-graph" type="button" data-action="reset">Вернуть y = x²</button>
      </div>
      <div class="ms-power-presets" role="group" aria-label="Быстрый выбор показателя степени">{buttons}</div>
      <div class="ms-graph-layout">
        <div class="ms-power-graph-main">
          <div class="ms-graph-canvas-card">
            <svg class="ms-power-plot" viewBox="0 0 640 500" role="img" aria-label="Интерактивный график степенной функции" data-role="plot"><text x="58" y="80" font-size="15">Для интерактива включите JavaScript.</text></svg>
            <div class="ms-graph-readout" data-output="readout">x = 1<br>y = 1</div>
          </div>
          <div class="ms-live-table" aria-label="Значения выбранной функции">{value_cells}</div>
          <div class="ms-qgraph-legend">
            <span class="ms-qgraph-legend-item"><span class="ms-qgraph-legend-line"></span>график функции</span>
            <span class="ms-qgraph-legend-item"><span class="ms-qgraph-legend-point ms-qgraph-legend-y"></span>выбранная точка</span>
            <span class="ms-qgraph-legend-item" data-role="reference-legend" hidden><span class="ms-power-reference-line"></span>прямая y = x</span>
          </div>
          <div class="ms-power-point-message" data-output="point" aria-live="polite">При x = 1: y = 1.</div>
          <div class="ms-graph-hint">Наведите курсор на график, чтобы увидеть координаты. Ползунок x задаёт точку, к которой интерактив вернётся после ухода курсора. Показан фрагмент графика от −3 до 3 по обеим осям.</div>
        </div>
        <div class="ms-graph-controls">
          <div class="ms-slider-card">
            <div class="ms-slider-head"><label class="ms-slider-name" for="power-index-v2">Показатель p</label><output class="ms-slider-value" data-output="exponent">2</output></div>
            <input class="ms-range" id="power-index-v2" type="range" min="0" max="11" value="9" step="1"/>
            <div class="ms-range-scale"><span>−3</span><span>12 функций</span><span>4</span></div>
          </div>
          <div class="ms-slider-card">
            <div class="ms-slider-head"><label class="ms-slider-name" for="power-x-v2">Аргумент x</label><output class="ms-slider-value" data-output="argument">1</output></div>
            <input class="ms-range" id="power-x-v2" type="range" min="-3" max="3" step="0.25" value="1"/>
            <div class="ms-range-scale"><span>−3</span><span>0</span><span>3</span></div>
            <label class="ms-power-reference"><input type="checkbox" data-role="reference"/> Сравнить с прямой y = x</label>
          </div>
          <div class="ms-live-properties" aria-live="polite">
            <div class="ms-live-property"><strong>Область определения D(f)</strong><span data-prop="domain">ℝ</span></div>
            <div class="ms-live-property"><strong>Множество значений E(f)</strong><span data-prop="range">[0; +∞)</span></div>
            <div class="ms-live-property"><strong>Чётность</strong><span data-prop="parity">Чётная</span></div>
            <div class="ms-live-property"><strong>Монотонность</strong><span data-prop="monotonic">Убывает до нуля, возрастает после нуля</span></div>
            <div class="ms-live-property"><strong>Нули функции</strong><span data-prop="zeros">x = 0</span></div>
            <div class="ms-live-property"><strong>Наибольшее и наименьшее значения</strong><span data-prop="extreme">Наименьшее: 0 при x = 0</span></div>
          </div>
        </div>
      </div>
    </div>'''
