const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{const fps=30;const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+__dirname+'/ep1.html');await p.evaluate(()=>warmFonts());
const tot=await p.evaluate(()=>TOTAL);const n=Math.round(tot*fps);
const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-preset','medium','-movflags','+faststart',__dirname+'/ep1_silent.mp4'],{stdio:['pipe','ignore','inherit']});
for(let i=0;i<n;i++){await p.evaluate(t=>renderAt(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:92});
 if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%300===0)console.log('frame',i,'/',n);}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done');})();
