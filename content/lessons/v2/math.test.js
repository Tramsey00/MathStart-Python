const {test}=require('node:test');
const assert=require('node:assert/strict');
const {powerValue,powerBranches,circlePoint}=require('./math.js');
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-10,`${a} != ${b}`);

test('Undefined arguments remain excluded, including the zero exponent',()=>{
  for(const n of [-3,-2,-1,0]) assert.equal(powerValue(0,n),null);
  for(const [n,d] of [[1,2],[2,3],[3,2],[-1,2]]) assert.equal(powerValue(-1,n,d),null);
  close(powerValue(-2,3),-8);
  close(powerValue(-2,-3),-1/8);
  close(powerValue(-3,0),1);
  close(powerValue(0,1,2),0);
});

test('Worked fractional-power values and their order agree with exact arithmetic',()=>{
  close(powerValue(4,-3,2),1/8);
  close(powerValue(.25,-3,2),8);
  close(powerValue(9,3,2),27);
  close(powerValue(.25,1,2),1/2);
  close(powerValue(.25,3,2),1/8);
  assert.ok(powerValue(.25,1,2)>powerValue(.25,3,2));
  assert.ok(powerValue(4,1,2)<powerValue(4,3,2));
});

test('Reciprocal curves have separate branches and do not draw across zero',()=>{
  for(const n of [-3,-2,-1]) {
    const branches=powerBranches(n);
    assert.equal(branches.length,2);
    assert.ok(branches[0].every(([x])=>x<0));
    assert.ok(branches[1].every(([x])=>x>0));
    for(const branch of branches) for(const [x,y] of branch) close(y*x**(-n),1);
  }
  const root=powerBranches(1,2);
  assert.equal(root.length,1);
  assert.deepEqual(root[0][0],[0,0]);
  for(const [x,y] of root[0]) close(y*y,x);
});

test('All interactive circle positions have unit radius and period two pi',()=>{
  for(let step=-48;step<=48;step++) {
    const point=circlePoint(step),next=circlePoint(step+24);
    close(point.x**2+point.y**2,1);
    close(point.x,next.x);close(point.y,next.y);
    assert.equal(step,24*point.turns+point.remainder);
    assert.ok(point.normalized>=0&&point.normalized<24);
  }
});

test('Standard coordinates, signed rotations and reflections match geometry',()=>{
  close(circlePoint(2).x,Math.sqrt(3)/2);close(circlePoint(2).y,1/2);
  close(circlePoint(3).x,Math.sqrt(2)/2);close(circlePoint(3).y,Math.sqrt(2)/2);
  assert.equal(circlePoint(-6).x,0);assert.equal(circlePoint(-6).y,-1);
  assert.equal(circlePoint(34).quadrant,'II четверть');
  assert.equal(circlePoint(-33).quadrant,'III четверть');
  for(let k=0;k<24;k++) {
    const p=circlePoint(k), ox=circlePoint(-k),oy=circlePoint(12-k),o=circlePoint(k+12);
    close(p.x,ox.x);close(-p.y,ox.y);
    close(-p.x,oy.x);close(p.y,oy.y);
    close(-p.x,o.x);close(-p.y,o.y);
  }
});
