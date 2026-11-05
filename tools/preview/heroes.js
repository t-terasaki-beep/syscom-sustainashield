const { chromium } = require('playwright'); const path=require('path');
const BASE='http://127.0.0.1:8765';
const pages=[['hub-business','/','#komarigoto h2'],['hub-residential','/residential/','h1'],['b-atsui','/business/atsui/','h1'],['b-denkidai','/business/denkidai/','h1'],['b-cubicle','/business/cubicle/','h1'],['r-ecocute','/residential/ecocute/','h1'],['r-solar','/residential/solar/','h1'],['r-battery','/residential/battery/','h1']];
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox']});
for(const [n,u,sel] of pages){for(const w of [375,1280]){const c=await b.newContext({viewport:{width:w,height:900}});const p=await c.newPage();await require('./fontroute.js')(p);await p.goto(BASE+u,{waitUntil:'load'});await p.evaluate(()=>{document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'))});await p.waitForTimeout(400);
const m=await p.evaluate((sel)=>{const h=document.querySelector(sel);const r=h.getBoundingClientRect();const lh=parseFloat(getComputedStyle(h).lineHeight);return {lines:Math.round(r.height/lh),fs:getComputedStyle(h).fontSize,w:Math.round(r.width),top:Math.round(r.top+window.scrollY)}},sel);
console.log(n.padEnd(16),w,'lines='+m.lines,'fs='+m.fs,'w='+m.w);
await p.screenshot({path:path.join(__dirname,'shots',`h-${n}-${w}.png`),clip:{x:0,y:Math.max(0,m.top-120),width:w,height:w<500?520:420},fullPage:true});await c.close();}}
await b.close();})();
