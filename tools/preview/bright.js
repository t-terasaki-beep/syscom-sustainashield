const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
const css=fs.readFileSync(path.join(__dirname,'bright.css'),'utf8').replace(/@import[^;]+;/,'');
const sticky=`<div class="sticky-cta"><a class="s1" href="#soudan">相談する</a><a class="s2" href="#soudan">LINEで送る</a><a class="s3" href="tel:+81-90-9326-4456" aria-label="電話">☎</a></div>`;
const jobs=[['b-atsui','/business/atsui/'],['hub-residential','/residential/']];
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox']});
for(const [n,u] of jobs){const c=await b.newContext({viewport:{width:375,height:812},isMobile:true,deviceScaleFactor:1});const p=await c.newPage();await require('./fontroute.js')(p);await p.goto('http://127.0.0.1:8765'+u,{waitUntil:'load'});
await p.addStyleTag({content:css});await p.evaluate((s)=>{document.body.insertAdjacentHTML('beforeend',s)},sticky);await p.waitForTimeout(700);
const H=await p.evaluate(()=>document.documentElement.scrollHeight);
for(let y=0,i=0;y<H&&i<4;y+=2200,i++){await p.screenshot({path:path.join(__dirname,'shots',`bright-${n}-${i}.png`),clip:{x:0,y,width:375,height:Math.min(2200,H-y)},fullPage:true});}
// 固定ボタンはビューポート撮影で
await p.screenshot({path:path.join(__dirname,'shots',`bright-${n}-viewport.png`)});
await c.close();}
await b.close();})();
