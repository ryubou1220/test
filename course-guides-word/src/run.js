const fs=require('fs');const path=require('path');const {make}=require('./lib.js');
const out=process.argv[2];(async()=>{for(const s of process.argv.slice(3)){const cfg=require('./'+s+'.js');const buf=await make(cfg);fs.writeFileSync(path.join(out,cfg.file),buf);console.log('wrote',cfg.file);}})();
