
(function(){
  var root=document.getElementById('ms-negative-power-lab-936');
  if(!root||root.getAttribute('data-initialized')==='true'){return;}
  root.setAttribute('data-initialized','true');
  var canvas=root.querySelector('[data-role="canvas"]');
  var range=root.querySelector('[data-role="n-range"]');
  var output=root.querySelector('[data-role="n-output"]');
  var formulaN=root.querySelector('[data-role="formula-n"]');
  var parity=root.querySelector('[data-role="parity"]');
  var symmetry=root.querySelector('[data-role="symmetry"]');
  var domain=root.querySelector('[data-role="domain"]');
  var valueRange=root.querySelector('[data-role="range"]');
  var monotonicity=root.querySelector('[data-role="monotonicity"]');
  var quarters=root.querySelector('[data-role="quarters"]');
  var reset=root.querySelector('[data-role="reset"]');
  var readout=root.querySelector('[data-role="readout"]');
  var tableValues=root.querySelectorAll('[data-role="table-value"]');
  if(!canvas||!range||!canvas.getContext){return;}
  var ctx=canvas.getContext('2d');
  if(!ctx){return;}
  var xMin=-4,xMax=4,yMin=-6,yMax=6,hoverX=null,resizeFrame=0;

  function value(x,n){
    if(x===0){return NaN;}
    return Math.pow(x,n);
  }
  function prettyInt(number){return String(number).replace('-', '−');}
  function fmt(number,digits){
    if(!isFinite(number)){return 'не определено';}
    if(Math.abs(number)<1e-12){number=0;}
    var abs=Math.abs(number),text;
    if(abs>=10000){
      text=number.toExponential(2);
    }else if(abs>0){
      if(abs<0.0001){
        text=number.toExponential(2);
      }else{
        text=number.toFixed(digits);
      }
    }else{
      text=number.toFixed(digits);
    }
    text=text.replace(/(\.\d*?[1-9])0+$|\.0+$/,'$1').replace('.',',').replace('-', '−');
    return text;
  }
  function roundedRect(x,y,w,h,r){
    var radius=Math.min(r,w/2,h/2);
    ctx.beginPath();ctx.moveTo(x+radius,y);ctx.arcTo(x+w,y,x+w,y+h,radius);ctx.arcTo(x+w,y+h,x,y+h,radius);ctx.arcTo(x,y+h,x,y,radius);ctx.arcTo(x,y,x+w,y,radius);ctx.closePath();
  }
  function arrow(x,y,direction){
    ctx.beginPath();
    if(direction==='right'){ctx.moveTo(x,y);ctx.lineTo(x-9,y-5);ctx.lineTo(x-9,y+5);}
    else{ctx.moveTo(x,y);ctx.lineTo(x-5,y+9);ctx.lineTo(x+5,y+9);}
    ctx.closePath();ctx.fill();
  }
  function point(px,py,color,radius){
    ctx.beginPath();ctx.arc(px,py,radius,0,Math.PI*2);ctx.fillStyle='#fff';ctx.fill();ctx.strokeStyle=color;ctx.lineWidth=2.6;ctx.stroke();
  }
  function drawBranch(n,start,end,steps,toX,toY){
    var started=false,i;
    ctx.beginPath();
    for(i=0;i<=steps;i+=1){
      var x=start+(end-start)*(i/steps),y=value(x,n);
      if(!isFinite(y)||y<yMin-1||y>yMax+1){started=false;continue;}
      if(!started){ctx.moveTo(toX(x),toY(y));started=true;}
      else{ctx.lineTo(toX(x),toY(y));}
    }
    ctx.stroke();
  }
  function draw(){
    var rect=canvas.getBoundingClientRect();
    var cssWidth=Math.max(300,Math.round(rect.width||820));
    var cssHeight=Math.max(300,Math.round(rect.height||480));
    var dpr=window.devicePixelRatio||1;
    var targetWidth=Math.round(cssWidth*dpr),targetHeight=Math.round(cssHeight*dpr);
    if(canvas.width!==targetWidth||canvas.height!==targetHeight){canvas.width=targetWidth;canvas.height=targetHeight;}
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,cssWidth,cssHeight);
    var n=parseInt(range.value,10);
    var margin={left:58,right:25,top:25,bottom:46};
    var plotX=margin.left,plotY=margin.top,plotWidth=Math.max(100,cssWidth-margin.left-margin.right),plotHeight=Math.max(100,cssHeight-margin.top-margin.bottom);
    function toX(x){return plotX+((x-xMin)/(xMax-xMin))*plotWidth;}
    function toY(y){return plotY+((yMax-y)/(yMax-yMin))*plotHeight;}
    ctx.fillStyle='#fff';ctx.fillRect(0,0,cssWidth,cssHeight);
    roundedRect(plotX,plotY,plotWidth,plotHeight,10);ctx.fillStyle='#fff';ctx.fill();ctx.strokeStyle='#dbeafe';ctx.lineWidth=1;ctx.stroke();
    ctx.save();ctx.beginPath();ctx.rect(plotX,plotY,plotWidth,plotHeight);ctx.clip();
    var x,y;
    for(x=-4;x<=4.001;x+=.5){ctx.beginPath();ctx.moveTo(toX(x),plotY);ctx.lineTo(toX(x),plotY+plotHeight);ctx.strokeStyle=Math.abs(x-Math.round(x))<.001?'#dbeafe':'#eef4fb';ctx.lineWidth=Math.abs(x-Math.round(x))<.001?1.1:.8;ctx.stroke();}
    for(y=-6;y<=6;y+=1){ctx.beginPath();ctx.moveTo(plotX,toY(y));ctx.lineTo(plotX+plotWidth,toY(y));ctx.strokeStyle=y%2===0?'#dbeafe':'#eef4fb';ctx.lineWidth=y%2===0?1.1:.8;ctx.stroke();}
    var axisX=toX(0),axisY=toY(0);
    ctx.save();ctx.setLineDash([7,6]);ctx.strokeStyle='#64748b';ctx.fillStyle='#64748b';ctx.lineWidth=1.9;
    ctx.beginPath();ctx.moveTo(plotX,axisY);ctx.lineTo(plotX+plotWidth,axisY);ctx.stroke();
    ctx.beginPath();ctx.moveTo(axisX,plotY+plotHeight);ctx.lineTo(axisX,plotY);ctx.stroke();ctx.restore();
    ctx.fillStyle='#475569';arrow(plotX+plotWidth,axisY,'right');arrow(axisX,plotY,'up');
    ctx.strokeStyle='#2563eb';ctx.lineWidth=4;ctx.lineCap='round';ctx.lineJoin='round';
    drawBranch(n,xMin,-0.015,1800,toX,toY);
    drawBranch(n,0.015,xMax,1800,toX,toY);
    point(toX(1),toY(1),'#16a34a',5.5);
    point(toX(-1),toY(value(-1,n)),'#7c3aed',5.5);
    if(hoverX!==null){
      if(Math.abs(hoverX)>.018){
        var hoverY=value(hoverX,n);
        if(isFinite(hoverY)){
          if(hoverY>=yMin){
            if(hoverY<=yMax){
              var hoverPx=toX(hoverX),hoverPy=toY(hoverY);
              ctx.save();
              ctx.setLineDash([5,5]);
              ctx.strokeStyle='#93c5fd';
              ctx.lineWidth=1.2;
              ctx.beginPath();
              ctx.moveTo(hoverPx,plotY);
              ctx.lineTo(hoverPx,plotY+plotHeight);
              ctx.stroke();
              ctx.beginPath();
              ctx.moveTo(plotX,hoverPy);
              ctx.lineTo(plotX+plotWidth,hoverPy);
              ctx.stroke();
              ctx.restore();
              point(hoverPx,hoverPy,'#2563eb',6);
            }
          }
        }
      }
    }
    ctx.restore();
    ctx.fillStyle='#64748b';ctx.font='500 12px Arial,sans-serif';ctx.textBaseline='middle';
    for(x=-4;x<=4;x+=1){if(x!==0){ctx.textAlign='center';ctx.fillText(prettyInt(x),toX(x),axisY+16);}}
    for(y=-6;y<=6;y+=2){if(y!==0){ctx.textAlign='right';ctx.fillText(prettyInt(y),axisX-9,toY(y));}}
    ctx.textAlign='right';ctx.fillText('0',axisX-9,axisY+16);
    ctx.fillStyle='#334155';ctx.font='700 15px Arial,sans-serif';ctx.textAlign='right';ctx.fillText('x',plotX+plotWidth-3,axisY-11);ctx.textAlign='left';ctx.fillText('y',axisX+10,plotY+11);
    ctx.font='700 11px Arial,sans-serif';ctx.fillStyle='#2563eb';ctx.textAlign='left';ctx.fillText('асимптота x=0',axisX+9,plotY+28);ctx.textAlign='right';ctx.fillText('асимптота y=0',plotX+plotWidth-10,axisY-13);
  }
  function updateReadout(x){
    if(x===null){readout.innerHTML='Наведите курсор<br>на график';return;}
    if(Math.abs(x)<.018){readout.innerHTML='x = 0<br>y не определено';return;}
    var y=value(x,parseInt(range.value,10));
    readout.innerHTML='x = '+fmt(x,2)+'<br>y = '+fmt(y,3);
  }
  function updateTable(n){
    var i;
    for(i=0;i<tableValues.length;i+=1){
      var x=parseFloat(tableValues[i].getAttribute('data-x'));
      tableValues[i].textContent=x===0?'не определено':fmt(value(x,n),5);
    }
  }
  function update(){
    var n=parseInt(range.value,10),even=Math.abs(n)%2===0;
    output.textContent=prettyInt(n);formulaN.textContent=prettyInt(n);
    parity.textContent=even?'Чётный отрицательный':'Нечётный отрицательный';
    symmetry.textContent=even?'Относительно оси Oy':'Относительно начала координат';
    domain.textContent='ℝ \\ {0}';
    valueRange.textContent=even?'(0; +∞)':'ℝ \\ {0}';
    monotonicity.textContent=even?'Возрастает на (−∞; 0), убывает на (0; +∞)':'Убывает на (−∞; 0) и (0; +∞)';
    quarters.textContent=even?'I и II четверти':'I и III четверти';
    updateTable(n);updateReadout(hoverX);draw();
  }
  function pointerToGraphX(event){
    var rect=canvas.getBoundingClientRect(),width=Math.max(300,rect.width||820),plotWidth=width-58-25;
    var x=xMin+((event.clientX-rect.left-58)/plotWidth)*(xMax-xMin);
    if(x<xMin||x>xMax){return null;}
    if(Math.abs(x)<.018){return 0;}
    return x;
  }
  function scheduleDraw(){
    if(resizeFrame){window.cancelAnimationFrame(resizeFrame);}
    resizeFrame=window.requestAnimationFrame(draw);
  }
  range.addEventListener('input',update);
  reset.addEventListener('click',function(){range.value='-2';hoverX=.8;update();});
  canvas.addEventListener('pointermove',function(event){hoverX=pointerToGraphX(event);updateReadout(hoverX);draw();});
  canvas.addEventListener('pointerleave',function(){hoverX=null;updateReadout(null);draw();});
  window.addEventListener('resize',scheduleDraw);
  root.setAttribute('data-ready','true');update();window.requestAnimationFrame(draw);
})();
