type Point = { x: number; y: number };
type Segment = { start: Point; end: Point };

export const MONGE_VIEWBOX: string;
export const mongeContactOwners: readonly number[];
export const initialMongeFrame: {
    circles: readonly (Point & { r: number })[];
    tangents: readonly Segment[];
    intersections: readonly Point[];
    contacts: readonly Point[];
    axis: Segment;
};
export function mountMongeArtwork(artwork: HTMLElement): (() => void) | undefined;
