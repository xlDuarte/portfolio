const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const {spawn}=require('node:child_process');
(async()=>{
 const server=spawn('python',['-m','http.server','8765','--directory','site'],{stdio:'ignore'});
 let browser;
 try{
  for(let i=0;i<30;i++){try{await fetch('http://127.0.0.1:8765');break;}catch{await new Promise(r=>setTimeout(r,100));}}
  browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8765/motorsport/insights/');
  await page.waitForFunction(()=>document.querySelector('#status').textContent==='Fontes carregadas. Selecione uma análise.');
  assert.equal(await page.locator('#podium-result tbody tr').count(),20);
  assert.match(await page.locator('#corner-source').textContent(),/OpenF1/);
  await page.locator('#file-a').setInputFiles({name:'test.csv',mimeType:'text/csv',buffer:Buffer.from('time_s,distance_m,speed_kmh\n0,0,36\n1,10,36\n2,20,36')});
  await page.waitForFunction(()=>document.querySelector('#corner-result').textContent.includes('Nova volta'));
  await page.locator('#start').fill('0');await page.locator('#end').fill('20');await page.locator('#compare').click();
  assert.match(await page.locator('#corner-source').textContent(),/test.csv/);
  await page.locator('#corner-reset').click();
  await page.locator('nav a[href="#championship"]').click();await page.locator('#points-0').fill('0');await page.locator('#recalculate').click();assert((await page.locator('#championship-result tbody tr').count())>=20);
  await page.locator('nav a[href="#trajectory"]').click();await page.locator('#optimize').click();await page.waitForSelector('#trajectory-result svg');assert.equal(await page.locator('#export-path').isEnabled(),true);
  await page.locator('nav a[href="#live"]').click();
  await page.route('https://api.openf1.org/**',route=>route.fulfill({status:401,body:'{}'}));await page.locator('#refresh').click();await page.waitForFunction(()=>document.querySelector('#live-result').textContent.includes('indisponível'));assert.match(await page.locator('#status').textContent(),/401/);
  await page.locator('#historical').click();assert.match(await page.locator('#live-result').textContent(),/Histórico/);
  await page.setViewportSize({width:390,height:844});for(const id of ['corners','podium','championship','live','trajectory']){await page.locator(`nav a[href="#${id}"]`).click();const overflow=await page.evaluate(()=>[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&!e.closest('.table')).map(e=>({tag:e.tagName,id:e.id,width:e.getBoundingClientRect().width,text:e.textContent.slice(0,80)})));if(overflow.length)console.log('Overflow candidates',id,overflow);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`overflow ${id}`);}
  assert.deepEqual(errors,[]);console.log('Passed: five panels, real data initialization, CSV import/reset, championship edits, optimizer/export, API error/no fallback, mobile widths.');
 }finally{await browser?.close();server.kill();}
})().catch(e=>{console.error(e);process.exitCode=1;});
