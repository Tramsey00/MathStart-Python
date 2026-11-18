const turns = 11;

const samplesPerTurn = 144;

function makeSpiral() {
    const sampleCount = turns * samplesPerTurn;
    const points = Array.from({ length: sampleCount + 1 }, (_, index) => {
        const t = index / sampleCount, angle = t * turns * Math.PI * 2;
        return [(630 - 280 * t) * Math.cos(angle), (278 - 193 * t) * Math.sin(angle)];
    });
    const pathFrom = (samples: number[][]) => samples.map(([x, y], index) =>
        `${index ? 'L' : 'M'}${x.toFixed(3)} ${y.toFixed(3)}`).join(' ');
    return {
        path: pathFrom(points),
        majorPaths: [0, 4, 8].map(turn => pathFrom(points.slice(turn * samplesPerTurn, (turn + 1) * samplesPerTurn + 1))),
    };
}

const { path, majorPaths } = makeSpiral();

export function OrbitGeometry() {
    return <svg className="orbit-artwork-svg" viewBox="-100 -100 1500 850" fill="none" aria-hidden="true" focusable="false">
        <ellipse className="orbit-hit-area" cx="0" cy="0" rx="680" ry="330" transform="translate(715 335) rotate(-26)" fill="transparent" />
        <g className="orbit-field"><g transform="translate(715 335) rotate(-26)">
            <path d={path} className="orbit-line" />
            {majorPaths.map(segment => <path key={segment} d={segment} className="orbit-line orbit-line-major" />)}
            <g className="orbit-traveller" style={{ offsetPath: `path("${path}")`, offsetRotate: '0deg' }}>
                <circle r="6" fill="var(--orb-warm)" stroke="var(--background)" strokeWidth="2" />
            </g>
        </g></g>
    </svg>;
}
