const { chromium } = require('playwright'); const path=require('path');
const V={
 gold:`:root{--orange:#C9A227;--orange-deep:#B08E1E} .btn-gold{color:#102F40 !important} .gnav .cta-mini{background:#C9A227 !important;color:#102F40 !important} .kd-face .b1{background:#C9A227 !important;color:#102F40 !important}`,
 green:`:root{--orange:#1F6B4A;--orange-deep:#175339} .gnav .cta-mini{background:#1F6B4A !important} .kd-face .b1{background:#1F6B4A !important}`,
 navy:``
};
const jobs=[['b-atsui','/business/atsui/',1280,0,640],['b-atsui','/business/atsui/',1280,5400,220],['hub-residential','/residential/',375,0,1000]];
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox']});
for(const [vn,css] of Object.entries(V)){for(const [n,u,w,y,h] of jobs){const c=await b.newContext({viewport:{width:w,height:800}});const p=await c.newPage();await require('./fontroute.js')(p);await p.goto('http://127.0.0.1:8765'+u,{waitUntil:'load'});if(css)await p.addStyleTag({content:css});await p.evaluate(()=>{document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'))});await p.waitForTimeout(600);
const H=await p.evaluate(()=>document.documentElement.scrollHeight);const yy=Math.min(y,Math.max(0,H-h));
await p.screenshot({path:path.join(__dirname,'shots',`var-${vn}-${n}-${w}-${y}.png`),clip:{x:0,y:yy,width:w,height:Math.min(h,H-yy)},fullPage:true});await c.close();}}
await b.close();})();
