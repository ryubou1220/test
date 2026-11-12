const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1600,height:2560},deviceScaleFactor:1});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
for(const id of ['A','B','C']){await p.locator('#'+id).screenshot({path:process.argv[3]+'/cover_'+id+'.png'});}
await b.close();})();
