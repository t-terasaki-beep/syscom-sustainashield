const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const OUT = path.join(__dirname, 'shots');
fs.mkdirSync(OUT, { recursive: true });
const BASE = 'http://127.0.0.1:8765';
const pages = [
  ['hub-business', '/'],
  ['hub-residential', '/residential/'],
  ['b-atsui', '/business/atsui/'],
  ['b-denkidai', '/business/denkidai/'],
  ['b-cubicle', '/business/cubicle/'],
  ['r-ecocute', '/residential/ecocute/'],
  ['r-solar', '/residential/solar/'],
  ['r-battery', '/residential/battery/'],
  ['sotsu-fit', '/sotsu-fit/'],
  ['shanetsu', '/shanetsu-chiba/'],
  ['lp', '/lp/'],
];
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const results = [];
  for (const [name, url] of pages) {
    for (const [vw, vh, tag] of [[375, 812, 'sp'], [1280, 900, 'pc']]) {
      const ctx = await browser.newContext({ viewport: { width: vw, height: vh }, deviceScaleFactor: 1, isMobile: vw < 500, locale: 'ja-JP' });
      const page = await ctx.newPage();await require('./fontroute.js')(page);
      const errors = [];
      page.on('pageerror', e => errors.push('pageerror: ' + e.message));
      page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
      const failed = [];
      page.on('requestfailed', r => { if (r.url().startsWith(BASE)) failed.push(r.url()); });
      await page.goto(BASE + url, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(600);
      // reveal all lazy elements
      await page.evaluate(() => { document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')); window.scrollTo(0, 0); });
      const m = await page.evaluate(() => {
        const de = document.documentElement;
        const over = [];
        document.querySelectorAll('body *').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.right > window.innerWidth + 1 && r.width > 0 && getComputedStyle(el).position !== 'fixed') {
            const cs = getComputedStyle(el);
            over.push(el.tagName + (el.id ? '#' + el.id : '') + '.' + (el.className && el.className.baseVal === undefined ? String(el.className).split(' ')[0] : '') + ' right=' + Math.round(r.right));
          }
        });
        return { scrollWidth: de.scrollWidth, innerWidth: window.innerWidth, title: document.title, h1: (document.querySelector('h1') || {}).innerText, over: over.slice(0, 8), overCount: over.length,
          lineLinks: document.querySelectorAll('a[href*="line.me"]').length, telLinks: document.querySelectorAll('a[href^="tel:"]').length, forms: document.querySelectorAll('a[href*="forms.gle"], a[href$="contact.html"]').length };
      });
      await page.screenshot({ path: path.join(OUT, `${name}-${tag}.png`), fullPage: true });
      results.push({ name, tag, url, hscroll: m.scrollWidth > m.innerWidth, scrollWidth: m.scrollWidth, innerWidth: m.innerWidth, overCount: m.overCount, over: m.over, errors, failed, lineLinks: m.lineLinks, telLinks: m.telLinks, forms: m.forms, title: m.title });
      await ctx.close();
    }
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'results.json'), JSON.stringify(results, null, 2));
  for (const r of results) {
    console.log(`${r.name.padEnd(16)} ${r.tag} hscroll=${r.hscroll} (${r.scrollWidth}/${r.innerWidth}) overflow=${r.overCount} errors=${r.errors.length} failed=${r.failed.length} line=${r.lineLinks} tel=${r.telLinks} form=${r.forms}`);
    if (r.over.length) console.log('   over:', r.over.join(' | '));
    if (r.errors.length) console.log('   errors:', r.errors.slice(0, 3).join(' | '));
    if (r.failed.length) console.log('   failed:', r.failed.slice(0, 5).join(' | '));
  }
})();
