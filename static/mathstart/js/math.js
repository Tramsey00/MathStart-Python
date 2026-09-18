(function (root) {
  'use strict';
  const gcd = (a,b) => b ? gcd(b,a%b) : Math.abs(a);
  function powerValue(x,n,d=1) {
    if (!Number.isFinite(x) || (d!==1 && x<0) || (x===0 && n<=0)) return null;
    return Math.pow(x,n/d);
  }
  function powerBranches(n,d=1) {
    const p=n/d, negative=d===1;
    function branch(sign) {
      const values=[];
      for(let i=0;i<=500;i++) {
        const t=i/500, x=sign*3*Math.pow(t,p>0&&p<1?3:1);
        const y=powerValue(x,n,d);
        if(y!==null&&Number.isFinite(y)&&Math.abs(y)<200) values.push([x,y]);
      }
      return values;
    }
    return negative ? [branch(-1),branch(1)] : [branch(1)];
  }
  function powerProperties(n,d=1) {
    const p=n/d, integer=d===1, even=integer&&n%2===0;
    if(p===0) return {domain:'ℝ ∖ {0}',range:'{1}',parity:'Чётная',monotonic:'Постоянна на D(f)',zeros:'Нет',extreme:'Наибольшее и наименьшее: 1',kind:'Нулевой показатель'};
    if(p>0&&integer) return {domain:'ℝ',range:even?'[0; +∞)':'ℝ',parity:even?'Чётная':'Нечётная',monotonic:even?'Убывает на (−∞; 0]; возрастает на [0; +∞)':'Возрастает на ℝ',zeros:'x = 0',extreme:even?'Наименьшее: 0 при x = 0':'Нет наибольшего и наименьшего',kind:'Натуральный показатель'};
    if(p<0&&integer) return {domain:'ℝ ∖ {0}',range:even?'(0; +∞)':'ℝ ∖ {0}',parity:even?'Чётная':'Нечётная',monotonic:even?'Возрастает на (−∞; 0); убывает на (0; +∞)':'Убывает на (−∞; 0) и на (0; +∞)',zeros:'Нет',extreme:'Нет наибольшего и наименьшего',kind:'Отрицательный целый показатель'};
    return {domain:p>0?'[0; +∞)':'(0; +∞)',range:p>0?'[0; +∞)':'(0; +∞)',parity:'Ни чётная, ни нечётная',monotonic:p>0?'Возрастает на [0; +∞)':'Убывает на (0; +∞)',zeros:p>0?'x = 0':'Нет',extreme:p>0?'Наименьшее: 0 при x = 0':'Нет наибольшего и наименьшего',kind:p>0?'Положительный дробный показатель':'Отрицательный дробный показатель'};
  }
  function circlePoint(step) {
    const normalized=((step%24)+24)%24, a=normalized*Math.PI/12;
    let x=Math.cos(a),y=Math.sin(a);
    if(Math.abs(x)<1e-12) x=0;
    if(Math.abs(y)<1e-12) y=0;
    return {x,y,normalized,turns:Math.trunc(step/24),remainder:step%24,
      quadrant:x===0||y===0?'На координатной оси':x>0?(y>0?'I четверть':'IV четверть'):(y>0?'II четверть':'III четверть')};
  }
  const api={gcd,powerValue,powerBranches,powerProperties,circlePoint};
  if(typeof module!=='undefined'&&module.exports) module.exports=api;
  else root.MathStartMath=Object.freeze(api);
})(typeof window!=='undefined'?window:this);
