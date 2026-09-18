
(function(){
  var root=document.getElementById('ms-power-lab-935');
  if(!root||root.getAttribute('data-initialized')==='true'){return;}
  root.setAttribute('data-initialized','true');
  var canvas=root.querySelector('[data-role="canvas"]');
  var range=root.querySelector('[data-role="n-range"]');
  var output=root.querySelector('[data-role="n-output"]');
  var formulaN=root.querySelector('[data-role="formula-n"]');
  var parity=root.querySelector('[data-role="parity"]');
  var symmetry=root.querySelector('[data-role="symmetry"]');
  var valueRange=root.querySelector('[data-role="range"]');
  var monotonicity=root.querySelector('[data-role="monotonicity"]');
  var reset=root.querySelector('[data-role="reset"]');
  var readout=root.querySelector('[data-role="readout"]');
  var tableValues=root.querySelectorAll('[data-role="table-value"]');
  if(!canvas||!range||!canvas.getContext){return;}
  var ctx=canvas.getContext('2d');
  if(!ctx){return;}
  var xMin=-2.25,xMax=2.25,yMin=-7,yMax=7,hoverX=null,resizeFrame=0;

  function value(x,n){return Math.pow(x,n);}
  function fmt(number,digits){
    if(!isFinite(number)){return '—';}
    if(Math.abs(number)<1e-10){number=0;}
    var abs=Math.abs(number);
    var text=abs>=1000?number.toExponential(2):number.toFixed(digits);
    text=text.replace(/\.0+$|(?<=\.[0-9]*?)0+$/,'').replace('.',',').replace('-', '−');
    return text;
  }
  function roundedRect(x,y,w,h,r){
    var radius=Math.min(r,w/2,h/2);ctx.beginPath();ctx.moveTo(x+radius,y);ctx.arcTo(x+w,y,x+w,y+h,radius);ctx.arcTo(x+w,y+h,x,y+h,radius);ctx.arcTo(x,y+h,x,y,radius);ctx.arcTo(x,y,x+w,y,radius);ctx.closePath();
  }
  function arrow(x,y,direction){
    ctx.beginPath();
    if(direction==='right'){ctx.moveTo(x,y);ctx.lineTo(x-9,y-5);ctx.lineTo(x-9,y+5);}else{ctx.moveTo(x,y);ctx.lineTo(x-5,y+9);ctx.lineTo(x+5,y+9);}
    ctx.closePath();ctx.fill();
  }
  function point(px,py,color,radius){ctx.beginPath();ctx.arc(px,py,radius,0,Math.PI*2);ctx.fillStyle='#fff';ctx.fill();ctx.strokeStyle=color;ctx.lineWidth=2.6;ctx.stroke();}
  function drawCurve(n,toX,toY){
    var steps=1500,started=false,i;
    ctx.beginPath();
    for(i=0;i<=steps;i+=1){
      var x=xMin+(xMax-xMin)*(i/steps),y=value(x,n);
      if(!isFinite(y)||y<yMin-1||y>yMax+1){started=false;continue;}
      if(!started){ctx.moveTo(toX(x),toY(y));started=true;}else{ctx.lineTo(toX(x),toY(y));}
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
    ctx.fillStyle='#fff';ctx.fillRect(0,0,cssWidth,cssHeight);roundedRect(plotX,plotY,plotWidth,plotHeight,10);ctx.fillStyle='#fff';ctx.fill();ctx.strokeStyle='#dbeafe';ctx.lineWidth=1;ctx.stroke();
    ctx.save();ctx.beginPath();ctx.rect(plotX,plotY,plotWidth,plotHeight);ctx.clip();
    var x,y;
    for(x=-2;x<=2.001;x+=0.5){ctx.beginPath();ctx.moveTo(toX(x),plotY);ctx.lineTo(toX(x),plotY+plotHeight);ctx.strokeStyle=Math.abs(x-Math.round(x))<.001?'#dbeafe':'#eef4fb';ctx.lineWidth=Math.abs(x-Math.round(x))<.001?1.1:.8;ctx.stroke();}
    for(y=-7;y<=7;y+=1){ctx.beginPath();ctx.moveTo(plotX,toY(y));ctx.lineTo(plotX+plotWidth,toY(y));ctx.strokeStyle=y%2===0?'#dbeafe':'#eef4fb';ctx.lineWidth=y%2===0?1.1:.8;ctx.stroke();}
    var axisX=toX(0),axisY=toY(0);ctx.strokeStyle='#475569';ctx.fillStyle='#475569';ctx.lineWidth=1.8;ctx.beginPath();ctx.moveTo(plotX,axisY);ctx.lineTo(plotX+plotWidth,axisY);ctx.stroke();arrow(plotX+plotWidth,axisY,'right');ctx.beginPath();ctx.moveTo(axisX,plotY+plotHeight);ctx.lineTo(axisX,plotY);ctx.stroke();arrow(axisX,plotY,'up');
    ctx.strokeStyle='#2563eb';ctx.lineWidth=4;ctx.lineCap='round';ctx.lineJoin='round';drawCurve(n,toX,toY);
    point(toX(0),toY(0),'#16a34a',5.5);point(toX(1),toY(1),'#16a34a',5.5);point(toX(-1),toY(n%2===0?1:-1),'#7c3aed',5.5);
    if(hoverX!==null){
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
    ctx.restore();ctx.fillStyle='#64748b';ctx.font='500 12px Arial,sans-serif';ctx.textBaseline='middle';
    for(x=-2;x<=2;x+=1){if(x!==0){ctx.textAlign='center';ctx.fillText(String(x).replace('-','−'),toX(x),axisY+16);}}
    for(y=-6;y<=6;y+=2){if(y!==0){ctx.textAlign='right';ctx.fillText(String(y).replace('-','−'),axisX-9,toY(y));}}
    ctx.textAlign='right';ctx.fillText('0',axisX-9,axisY+16);ctx.fillStyle='#334155';ctx.font='700 15px Arial,sans-serif';ctx.textAlign='right';ctx.fillText('x',plotX+plotWidth-3,axisY-11);ctx.textAlign='left';ctx.fillText('y',axisX+10,plotY+11);
  }
  function updateReadout(x){
    if(x===null){readout.innerHTML='Наведите курсор<br>на график';return;}
    var y=value(x,parseInt(range.value,10));
    readout.innerHTML='x = '+fmt(x,2)+'<br>y = '+fmt(y,2);
  }
  function updateTable(n){
    var i;for(i=0;i<tableValues.length;i+=1){var x=parseFloat(tableValues[i].getAttribute('data-x'));tableValues[i].textContent=fmt(value(x,n),4);}
  }
  function update(){
    var n=parseInt(range.value,10),even=n%2===0;
    output.textContent=String(n);formulaN.textContent=String(n);parity.textContent=even?'Чётный':'Нечётный';symmetry.textContent=even?'Относительно оси Oy':'Относительно начала координат';valueRange.textContent=even?'[0; +∞)':'ℝ';monotonicity.textContent=even?'Убывает до 0, затем возрастает':'Возрастает на всей ℝ';updateTable(n);updateReadout(hoverX);draw();
  }
  function pointerToGraphX(event){var rect=canvas.getBoundingClientRect(),width=Math.max(300,rect.width||820),plotWidth=width-58-25,x=xMin+((event.clientX-rect.left-58)/plotWidth)*(xMax-xMin);return x<xMin||x>xMax?null:x;}
  function scheduleDraw(){if(resizeFrame){window.cancelAnimationFrame(resizeFrame);}resizeFrame=window.requestAnimationFrame(draw);}
  range.addEventListener('input',update);
  reset.addEventListener('click',function(){range.value='2';hoverX=.8;update();});
  canvas.addEventListener('pointermove',function(event){hoverX=pointerToGraphX(event);updateReadout(hoverX);draw();});
  canvas.addEventListener('pointerleave',function(){hoverX=null;updateReadout(null);draw();});
  window.addEventListener('resize',scheduleDraw);
  root.setAttribute('data-ready','true');update();window.requestAnimationFrame(draw);
})();
