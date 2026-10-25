// Presentation only: preserve authored values; never calculate or simplify them.
const element = (tag, children, attrs = {}) => ({ kind: 'element', tag, attrs, children });
const hasClass = (node, name) => (node.attrs?.class ?? '').split(/\s+/).includes(name);
const textOf = node => node.kind === 'text' ? node.text : (node.children ?? []).map(textOf).join('');
const row = children => {
  if (!Array.isArray(children) || !children.length) throw new Error('Mathematical part must not be empty');
  return children.length === 1 ? children[0] : element('mrow', children);
};

export function mathToken(tag, text) {
  if (!['mn', 'mi', 'mo', 'mtext'].includes(tag)) throw new Error('Unsupported mathematical token');
  return element(tag, [{ kind: 'text', text: String(text) }]);
}
export function mathExpression(children, { display = 'inline', label, attrs = {} } = {}) {
  const classes = new Set([...(attrs.class ?? '').split(/\s+/).filter(Boolean), 'lesson-math']);
  return element('math', children, { ...attrs, class: [...classes].join(' '), display,
    ...(label ? { 'aria-label': label } : {}) });
}
export function fractionNode(numerator, denominator) {
  return element('mfrac', [row(numerator), row(denominator)]);
}
export function rootNode(radicand, index) {
  return index ? element('mroot', [row(radicand), row(index)]) : element('msqrt', [row(radicand)]);
}
export function powerNode(base, exponent) {
  return element('msup', [row(base), row(exponent)]);
}
export function mixedNumberNode(whole, numerator, denominator, attrs = {}) {
  const value = String(whole).trim();
  if (!/^[−-]?(?:\d+|\p{L})$/u.test(value)) throw new Error('Mixed number needs an explicit whole part');
  const negative = /^[−-]/.test(value);
  const integer = value.replace(/^[−-]/, '');
  return mathExpression([element('mrow', [
    ...(negative ? [mathToken('mo', '−')] : []), simpleToken(integer),
    element('mspace', [], { width: '0.16em' }),
    fractionNode([simpleToken(numerator)], [simpleToken(denominator)]),
  ])], { attrs: { ...attrs, class: `${attrs.class ?? ''} lesson-math--mixed`.trim() } });
}
function simpleToken(value) {
  const text = String(value).trim();
  if (/^[−-]?\d+(?:[.,]\d+)?$/.test(text)) return mathToken('mn', text);
  if (/^\p{L}$/u.test(text)) return mathToken('mi', text);
  throw new Error('Composite legacy term needs explicit authored MathML');
}
export function normalizeMathNotation(nodes) {
  return nodes.map(node => {
    if (node.kind === 'text' || node.tag === 'svg') return node;
    if (node.kind === 'selfCheck') return { ...node,
      question: normalizeMathNotation(node.question), answer: normalizeMathNotation(node.answer) };
    if (!node.children) return node;
    if (hasClass(node, 'ms-mixed')) {
      const fraction = node.children.find(child => hasClass(child, 'ms-frac'));
      const numerator = fraction?.children.find(child => hasClass(child, 'ms-num'));
      const denominator = fraction?.children.find(child => hasClass(child, 'ms-den'));
      if (!fraction || !numerator || !denominator) throw new Error('Incomplete legacy mixed number');
      const whole = node.children.filter(child => child !== fraction).map(textOf).join('').trim();
      return mixedNumberNode(whole, textOf(numerator), textOf(denominator), { ...node.attrs,
        class: (node.attrs.class ?? '').split(/\s+/).filter(name => name !== 'ms-mixed').join(' ') });
    }
    if (hasClass(node, 'ms-frac')) {
      const numerator = node.children.find(child => hasClass(child, 'ms-num'));
      const denominator = node.children.find(child => hasClass(child, 'ms-den'));
      if (!numerator || !denominator) throw new Error('Incomplete legacy fraction');
      const attrs = { ...node.attrs };
      attrs.class = (attrs.class ?? '').split(/\s+/).filter(name => name !== 'ms-frac').join(' ');
      return mathExpression([fractionNode([simpleToken(textOf(numerator))], [simpleToken(textOf(denominator))])], { attrs });
    }
    const children = normalizeMathNotation(node.children);
    return node.tag === 'math'
      ? mathExpression(children, { attrs: node.attrs, display: node.attrs.display ?? 'inline' })
      : { ...node, children };
  });
}
