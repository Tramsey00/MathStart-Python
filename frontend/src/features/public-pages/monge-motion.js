// Geometry and timing recovered from MS-T009. This module also runs in the
// standalone 404 document, so it deliberately has no framework imports.
/** @typedef {{ x: number, y: number }} Point */
/** @typedef {Point & { r: number }} Circle */
/** @typedef {{ start: Point, end: Point }} Segment */

export const MONGE_VIEWBOX = '45 15 590 490';
const pairs = [[0, 1], [0, 2], [1, 2]];
const motionDuration = 24_000;
const buildDuration = 2_600;
const fadeDuration = 650;
const sceneDuration = buildDuration + motionDuration + fadeDuration;
const pauseKey = 'mathstart-monge-paused';

/** @param {Circle} a @param {Circle} b */
function externalTangents(a, b) {
    const dx = b.x - a.x, dy = b.y - a.y, distance = Math.hypot(dx, dy);
    const difference = a.r - b.r;
    if (Math.abs(difference) < 1e-6 || distance <= Math.abs(difference) + 1e-6) {
        throw new RangeError('Monge artwork requires distinct radii and two external tangents.');
    }
    // The two unit normals satisfy n·(B−A) = rA−rB. Each contact is C+r·n.
    const ux = dx / distance, uy = dy / distance;
    const along = difference / distance, across = Math.sqrt(1 - along * along);
    const intersection = {
        x: (a.r * b.x - b.r * a.x) / difference,
        y: (a.r * b.y - b.r * a.y) / difference,
    };
    const tangents = [1, -1].map(side => {
        const nx = along * ux - side * across * uy, ny = along * uy + side * across * ux;
        const contactA = { x: a.x + a.r * nx, y: a.y + a.r * ny };
        const contactB = { x: b.x + b.r * nx, y: b.y + b.r * ny };
        const distanceSquared = (/** @type {Point} */ p) => (p.x - intersection.x) ** 2 + (p.y - intersection.y) ** 2;
        const farContact = distanceSquared(contactA) >= distanceSquared(contactB) ? contactA : contactB;
        return { start: farContact, end: intersection, contacts: [contactA, contactB] };
    });
    return { tangents, intersection };
}

/** @param {number} elapsed */
function mongeFrame(elapsed) {
    const phase = elapsed % motionDuration / motionDuration * 2 * Math.PI;
    const wave = Math.sin(phase);
    const circles = [
        { x: 190 - 8 * wave, y: 220 + 24 * wave, r: 112 },
        { x: 370 + 12 * Math.sin(phase + .7), y: 330 - 30 * wave, r: 58 },
        { x: 505 + 8 * Math.sin(phase - .5), y: 270 + 14 * Math.sin(phase + .4), r: 28 },
    ];
    const constructions = pairs.map(([a, b]) => externalTangents(circles[a], circles[b]));
    const intersections = constructions.map(pair => pair.intersection);
    // H_AC lies between H_AB and H_BC. Its position still comes from its own pair.
    const axis = { start: intersections[0], end: intersections[2] };
    const tangents = constructions.flatMap(pair => pair.tangents);
    return { circles, tangents, intersections, axis };
}

export const initialMongeFrame = mongeFrame(0);

/** @param {number} time @param {number} start @param {number} duration */
function smoothProgress(time, start, duration) {
    const t = Math.max(0, Math.min(1, (time - start) / duration));
    return t * t * (3 - 2 * t);
}

/** @param {Element} element @param {Point} point */
function setPoint(element, { x, y }) {
    element.setAttribute('cx', String(x));
    element.setAttribute('cy', String(y));
}

/** @param {Element} element @param {Segment} line @param {number} reveal */
function setLine(element, { start, end }, reveal) {
    element.setAttribute('x1', String(start.x));
    element.setAttribute('y1', String(start.y));
    element.setAttribute('x2', String(start.x + (end.x - start.x) * reveal));
    element.setAttribute('y2', String(start.y + (end.y - start.y) * reveal));
}

/** @param {HTMLElement} artwork @returns {(() => void) | undefined} */
export function mountMongeArtwork(artwork) {
    const drawing = artwork.querySelector('svg');
    const scene = artwork.querySelector('[data-monge-scene]');
    const circleGroup = artwork.querySelector('[data-monge-circles]');
    const pointGroup = artwork.querySelector('[data-monge-points]');
    const axis = artwork.querySelector('[data-monge-axis]');
    const toggle = artwork.querySelector('button[data-monge-pause]');
    if (!drawing || !scene || !circleGroup || !pointGroup || !axis || !toggle
        || typeof IntersectionObserver !== 'function' || typeof matchMedia !== 'function') return;
    const circles = circleGroup.querySelectorAll('circle');
    const points = pointGroup.querySelectorAll('circle');
    const tangents = scene.querySelectorAll('[data-monge-tangent]');
    const media = matchMedia('(prefers-reduced-motion: reduce)');
    let elapsed = 0, started = false, paused = false, visible = false, disposed = false;
    let frameId, previousTime;
    try { paused = localStorage.getItem(pauseKey) === 'true'; } catch { /* Optional storage. */ }

    function draw() {
        const complete = media.matches || !started;
        const phase = smoothProgress(elapsed, buildDuration, motionDuration) * motionDuration;
        const geometry = mongeFrame(phase);
        scene.setAttribute('opacity', String(complete ? 1 : 1 - smoothProgress(elapsed, buildDuration + motionDuration, fadeDuration)));
        circleGroup.setAttribute('opacity', String(complete ? 1 : smoothProgress(elapsed, 0, 900)));
        pointGroup.setAttribute('opacity', String(complete ? 1 : smoothProgress(elapsed, 1_800, 350)));
        const tangentReveal = complete ? 1 : smoothProgress(elapsed, 750, 1_100);
        circles.forEach((circle, index) => setPoint(circle, geometry.circles[index]));
        points.forEach((point, index) => setPoint(point, geometry.intersections[index]));
        tangents.forEach((tangent, index) => setLine(tangent, geometry.tangents[index], tangentReveal));
        setLine(axis, geometry.axis, complete ? 1 : smoothProgress(elapsed, 2_050, 550));
    }

    function stop() {
        if (frameId !== undefined) cancelAnimationFrame(frameId);
        frameId = previousTime = undefined;
    }
    function reconcile() {
        if (disposed || paused || media.matches || !visible || document.hidden) stop();
        else if (frameId === undefined) frameId = requestAnimationFrame(tick);
    }
    function tick(now) {
        frameId = undefined;
        if (!disposed && !paused && !media.matches && visible && !document.hidden) {
            if (previousTime !== undefined) elapsed = (elapsed + now - previousTime) % sceneDuration;
            previousTime = now;
            started = true;
            draw();
        }
        reconcile();
    }
    function updateControl() {
        toggle.disabled = media.matches;
        toggle.setAttribute('aria-label', media.matches ? 'Построение Монжа' : 'Пауза анимации построения Монжа');
        if (media.matches) toggle.removeAttribute('aria-pressed');
        else toggle.setAttribute('aria-pressed', String(paused));
    }
    function togglePause() {
        if (media.matches) return;
        paused = !paused;
        try { localStorage.setItem(pauseKey, String(paused)); } catch { /* Optional storage. */ }
        updateControl();
        reconcile();
    }
    function motionPreference() {
        updateControl();
        draw();
        reconcile();
    }

    const observer = new IntersectionObserver(([entry]) => {
        visible = entry.isIntersecting;
        reconcile();
    });
    observer.observe(drawing);
    media.addEventListener('change', motionPreference);
    document.addEventListener('visibilitychange', reconcile);
    toggle.addEventListener('click', togglePause);
    updateControl();
    return () => {
        disposed = true;
        stop();
        observer.disconnect();
        media.removeEventListener('change', motionPreference);
        document.removeEventListener('visibilitychange', reconcile);
        toggle.removeEventListener('click', togglePause);
        toggle.disabled = true;
        toggle.setAttribute('aria-label', 'Построение Монжа');
        toggle.removeAttribute('aria-pressed');
    };
}
