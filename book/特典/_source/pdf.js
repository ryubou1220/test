const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
for(const [src,out] of [[process.argv[2],process.argv[3]],[process.argv[4],process.argv[5]]]){
 await p.goto('file://'+src);await p.pdf({path:out,format:'A4',printBackground:true,preferCSSPageSize:true});}
await b.close();})();
