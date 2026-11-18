const {chromium}=require('playwright');const fs=require('fs');
const [,, worker, nworkers, fps]=process.argv;const FPS=+fps||30;
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',e=>console.error('PAGEERR',e.message));
 await p.goto('file:///tmp/claude-0/work/index.html');await p.evaluate(()=>document.fonts.ready);
 await p.evaluate(()=>Promise.all(['700 40px Cairo','800 40px Cairo','40px AmiriQ','700 40px Aref'].map(f=>document.fonts.load(f,'بسم'))));
 const total=await p.evaluate(()=>TOTAL);const N=Math.ceil(total*FPS);
 fs.mkdirSync(process.env.OUT||'frames',{recursive:true});
 const only=process.env.ONLY?process.env.ONLY.split(',').map(Number):null;
 for(let f=+worker;f<N;f+=+nworkers){
  if(only&&!only.includes(f))continue;
  await p.evaluate(t=>{render(t);scrollTo(0,0)},f/FPS);
  await p.screenshot({path:`${process.env.OUT||'frames'}/f${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});
 }
 await b.close();
})();
