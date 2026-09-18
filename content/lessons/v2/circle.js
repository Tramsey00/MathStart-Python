(function () {
  'use strict';
  const root=document.getElementById('circle-lab-v2');
  if(!root) return;
  const api=window.MathStartMath, plot=root.querySelector('[data-role="plot"]');
  const slider=root.querySelector('#circle-angle-v2');
  const presets=Array.from(root.querySelectorAll('[data-step]'));
  const output=name=>root.querySelector('[data-output="'+name+'"]');
  const fmt=v=>Math.abs(v)<1e-10?'0':Number(v.toFixed(4)).toString().replace('.',',').replace('-','−');
  const fraction=(a,b)=>'<span class="v2-frac"><span>'+a+'</span><span>'+b+'</span></span>';
  const radical=a=>'<span class="v2-root"><span class="v2-root-sign">√</span><span class="v2-radicand">'+a+'</span></span>';
  function angle(k) {
    if(k===0) return '0';
    const divisor=api.gcd(k,12), numerator=Math.abs(k/divisor), denominator=12/divisor;
    const top=(numerator===1?'':numerator)+'π';
    return (k<0?'−':'')+(denominator===1?top:fraction(top,denominator));
  }
  function coordinate(v) {
    const sign=v<0?'−':'', magnitude=Math.abs(v);
    if(magnitude<1e-10) return '0';
    if(Math.abs(magnitude-1)<1e-10) return sign+'1';
    if(Math.abs(magnitude-.5)<1e-10) return sign+fraction(1,2);
    if(Math.abs(magnitude-Math.SQRT1_2)<1e-10) return sign+fraction(radical(2),2);
    if(Math.abs(magnitude-Math.sqrt(3)/2)<1e-10) return sign+fraction(radical(3),2);
    return fmt(v);
  }
  const ox=218,oy=188,r=130,px=x=>ox+r*x,py=y=>oy-r*y;
  let step=4;
  function draw() {
    const point=api.circlePoint(step), X=px(point.x),Y=py(point.y);
    let svg='<path d="M39 188 H393 M218 361 V20" fill="none" stroke="#8090a7" stroke-width="1.3"/><path d="M393 188 l-6 -3 v6z M218 20 l-3 6 h6z" fill="#8090a7"/><text x="401" y="193" font-size="14" fill="#526b8b">x</text><text x="229" y="24" font-size="14" fill="#526b8b">y</text><text x="205" y="207" font-size="12" fill="#8291a6">O</text>';
    svg+='<circle cx="218" cy="188" r="130" fill="none" stroke="#bdcfe9" stroke-width="1.7"/>';
    for(const k of [0,2,3,4,6,8,9,10,12,14,15,16,18,20,21,22]) {
      const t=api.circlePoint(k);
      svg+='<circle cx="'+px(t.x)+'" cy="'+py(t.y)+'" r="2.5" fill="#a0b9de"/>';
    }
    svg+='<g fill="#647a9a" font-size="12"><text x="362" y="211">A(1; 0)</text><text x="235" y="53">B(0; 1)</text><text x="75" y="175" text-anchor="end">C(−1; 0)</text><text x="235" y="333">D(0; −1)</text></g>';
    svg+='<g fill="#a0adc0" font-size="12"><text x="276" y="129">I</text><text x="151" y="129">II</text><text x="150" y="254">III</text><text x="274" y="254">IV</text></g>';
    if(point.remainder!==0) {
      const a=point.remainder*Math.PI/12, count=Math.max(8,Math.ceil(Math.abs(a)*24));
      const points=Array.from({length:count+1},(_,i)=>{
        const t=a*i/count;
        return (i?'L':'M')+px(Math.cos(t)).toFixed(3)+','+py(Math.sin(t)).toFixed(3);
      });
      svg+='<path data-role="arc" d="'+points.join(' ')+'" fill="none" stroke="#3973d9" stroke-width="3" stroke-linecap="round"/>';
      const direction=Math.sign(point.remainder),dx=-Math.sin(a)*direction,dy=-Math.cos(a)*direction;
      svg+='<path d="M'+X+','+Y+' L'+(X-dx*11-dy*4)+','+(Y-dy*11+dx*4)+' L'+(X-dx*11+dy*4)+','+(Y-dy*11-dx*4)+' Z" fill="#3973d9"/>';
    }
    svg+='<path d="M'+X+' 188 V'+Y+' H218" fill="none" stroke="#d99a48" stroke-width="1.4" stroke-dasharray="4 4"/><path d="M218 188 L'+X+' '+Y+'" fill="none" stroke="#698fd3" stroke-width="1.5"/>';
    svg+='<circle data-role="point" data-x="'+point.x+'" data-y="'+point.y+'" cx="'+X+'" cy="'+Y+'" r="5" fill="white" stroke="#2c65d5" stroke-width="2.4"/>';
    const mx=X+(point.x<0?-13:13),my=Y+(point.y<0?21:-12);
    svg+='<text x="'+mx+'" y="'+my+'" text-anchor="'+(point.x<0?'end':'start')+'" font-size="14" font-weight="600" fill="#2b5ba9">M</text>';
    plot.innerHTML=svg;
    plot.setAttribute('data-step',step);
    plot.setAttribute('aria-label','Точка M: поворот '+(step*15)+' градусов, '+point.quadrant.toLowerCase());
    output('angle').innerHTML=angle(step);
    output('normalized').innerHTML=angle(point.normalized);
    output('quadrant').textContent=point.quadrant;
    output('degrees').textContent=fmt(step*15)+'°';
    output('turns').textContent=fmt(point.turns);
    output('direction').textContent=step===0?'Без поворота':step>0?'Против часовой стрелки':'По часовой стрелке';
    const exact=point.normalized%2===0||point.normalized%3===0;
    output('coordinates').innerHTML='<strong>M'+(exact?'':' ≈')+' ('+coordinate(point.x)+'; '+coordinate(point.y)+')</strong>'+(exact?' · точные координаты':' · округлено до 4 знаков');
    slider.value=step;
    slider.setAttribute('aria-valuetext',(step*15)+' градусов');
    presets.forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.step)===step)));
    root.querySelector('[data-action="add"]').disabled=step+24>Number(slider.max);
    root.querySelector('[data-action="subtract"]').disabled=step-24<Number(slider.min);
  }
  presets.forEach(b=>b.addEventListener('click',()=>{step=Number(b.dataset.step);draw();}));
  slider.addEventListener('input',()=>{step=Number(slider.value);draw();});
  for(const [action,delta] of [['subtract',-24],['add',24]]) {
    root.querySelector('[data-action="'+action+'"]').addEventListener('click',()=>{
      const candidate=step+delta;
      if(candidate>=Number(slider.min)&&candidate<=Number(slider.max)) {step=candidate;draw();}
    });
  }
  root.querySelector('[data-action="reset"]').addEventListener('click',()=>{step=4;draw();});
  draw();
  root.setAttribute('data-ready','true');
})();
