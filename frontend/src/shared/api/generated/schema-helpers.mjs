// JSON Schema lengths count Unicode code points, including unpaired surrogates.
export default function unicodeLength(text){let length=0;for(const point of text){void point;length++;}return length;}
