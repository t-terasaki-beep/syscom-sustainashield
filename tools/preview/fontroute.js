// Google Fonts をローカルの @fontsource で代替（スクリーンショット用・本番には影響しない）
const fs=require('fs'), path=require('path');
const ROOT=path.join(__dirname,'pw','node_modules','@fontsource');
const MAP={'Shippori Mincho B1':'shippori-mincho-b1','Zen Kaku Gothic New':'zen-kaku-gothic-new','Noto Serif JP':'noto-serif-jp'};
module.exports=async function(page){
  await page.route('**/fonts.googleapis.com/**',async route=>{
    const u=new URL(route.request().url()); let css='';
    for(const fam of u.searchParams.getAll('family')){
      const [name,spec]=fam.split(':'); const pkg=MAP[name.replace(/\+/g,' ')]; if(!pkg) continue;
      const weights=(spec||'wght@400').replace('wght@','').split(';');
      for(const w of weights){const f=path.join(ROOT,pkg,`${w}.css`); if(!fs.existsSync(f)) continue;
        css+=fs.readFileSync(f,'utf8').replace(/\.\/files\//g,`/__fonts/${pkg}/files/`)+'\n';}
    }
    await route.fulfill({status:200,contentType:'text/css',body:css});
  });
  await page.route('**/__fonts/**',async route=>{
    const u=new URL(route.request().url()); const f=path.join(ROOT,u.pathname.replace('/__fonts/',''));
    if(fs.existsSync(f)) await route.fulfill({status:200,contentType:'font/woff2',body:fs.readFileSync(f)}); else await route.fulfill({status:404,body:''});
  });
  await page.route('**/fonts.gstatic.com/**',r=>r.fulfill({status:404,body:''}));
};
