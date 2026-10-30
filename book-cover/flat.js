const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async()=>{const b=await chromium.launch();
for (const [src,out] of process.argv.slice(2).reduce((a,v,i,arr)=>i%2?a:[...a,[arr[i],arr[i+1]]],[])) {
 const p=await b.newPage({viewport:{width:1400,height:1980},deviceScaleFactor:2});
 await p.goto('file://'+src);
 await p.addStyleTag({content:`.scene{perspective:none}.book{transform:none!important;left:0!important;top:0!important}
  .spine,.top,.shadow,.glow,.spark{display:none}.front{transform:none!important;border-radius:0!important;box-shadow:none!important}`});
 await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.locator('.front').screenshot({path:out});await p.close();}
await b.close();})();
