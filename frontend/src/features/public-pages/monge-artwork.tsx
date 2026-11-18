import { useEffect, useRef } from 'react';
import { MONGE_VIEWBOX, initialMongeFrame, mountMongeArtwork } from './monge-motion.js';
import motionModule from './monge-motion.js?url&no-inline';
import './monge-artwork.css';

function lineProps({ start, end }: typeof initialMongeFrame.axis) {
    return { x1: start.x, y1: start.y, x2: end.x, y2: end.y };
}

export function MongeArtwork() {
    const artwork = useRef<HTMLElement>(null);
    useEffect(() => {
        if (artwork.current) return mountMongeArtwork(artwork.current);
    }, []);

    return <figure className="monge-artwork" ref={artwork} data-monge-module={motionModule}>
        <button className="monge-pause" type="button" data-monge-pause="" aria-label="Построение Монжа" disabled>
            <svg className="monge-artwork-svg" viewBox={MONGE_VIEWBOX} fill="none"
                role="img" focusable="false" aria-label="Построение Монжа: три окружности, их общие внешние касательные и три точки пересечения на одной прямой">
                <g data-monge-scene="" transform="rotate(-26 380 310)">
                    <g className="monge-tangents">{initialMongeFrame.tangents.map((line, index) =>
                        <line key={index} data-monge-tangent="" {...lineProps(line)} />)}</g>
                    <g className="monge-circles" data-monge-circles="">{initialMongeFrame.circles.map((circle, index) =>
                        <circle key={index} cx={circle.x} cy={circle.y} r={circle.r} />)}</g>
                    <line className="monge-axis" data-monge-axis="" {...lineProps(initialMongeFrame.axis)} />
                    <g className="monge-points" data-monge-points="">{initialMongeFrame.intersections.map((point, index) =>
                        <circle key={index} cx={point.x} cy={point.y} r="4.5" />)}</g>
                </g>
            </svg>
        </button>
    </figure>;
}
