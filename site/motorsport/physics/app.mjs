import {activeAero,aero,ers,lap,sensitivity,wingCAD,telemetry} from './models.mjs';
import {numericCSV} from '../porsche/engineering.mjs';
import {loadRace} from '../data/load.mjs';
const $=s=>document.querySelector(s),mode=document.body.dataset.mode,fmt=x=>Number(x).toLocaleString('pt-BR',{maximumFractionDigits:3});
let observed=null,dataset=null,result=null,reference=null,version=0,race=null,source='',dataSource='';
const fields={aero:['front_deg','rear_deg','cd','cl_down'],lap:['length_m','curvature_1pm']};
function status(s){$('#status').textContent=s;}
function clear(clearReference=false){result=null;for(const id of ['json','csv','pin'])$('#'+id).disabled=true;$('#kpis').replaceChildren();$('#charts').replaceChildren();$('#table').replaceChildren();$('#sensitivity').replaceChildren();if(clearReference){reference=null;$('#comparison').textContent='Nenhuma referência fixada.';}}
function params(){const f=$('#parameters');if(!f.reportValidity())throw Error('Preencha os parâmetros.');return Object.fromEntries([...new FormData(f)].map(([k,v])=>[k,Number(v)]));}
function download(text,name,type='text/plain'){const url=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function asCSV(rows){const keys=Object.keys(rows[0]);return keys.join(',')+'\n'+rows.map(r=>keys.map(k=>r[k]??'').join(',')).join('\n')+'\n';}
function table(el,rows){el.replaceChildren();if(!rows.length)return;const t=document.createElement('table'),head=t.createTHead().insertRow();Object.keys(rows[0]).forEach(k=>{const th=document.createElement('th');th.textContent=k;head.append(th);});const body=t.createTBody();for(const row of rows.slice(0,500)){const tr=body.insertRow();for(const v of Object.values(row)){const td=tr.insertCell();td.textContent=typeof v==='number'?fmt(v):String(v??'—');}}el.append(t);if(rows.length>500){const note=document.createElement('p');note.textContent='Exibindo 500 linhas. A exportação inclui todas as amostras.';el.append(note);}}
function kpis(items){$('#kpis').replaceChildren(...items.map(([label,value,unit])=>{const el=document.createElement('div');el.className='kpi';const title=document.createElement('small'),number=document.createElement('strong');title.textContent=label;number.textContent=fmt(value)+' '+unit;el.append(title,number);return el;}));}
function plot(title,series,xlabel,ylabel){
 const section=document.createElement('section'),h=document.createElement('h3');h.textContent=title;section.append(h);
 const all=series.flatMap(s=>s.data),xs=all.map(p=>p[0]),ys=all.map(p=>p[1]);
 const xmin=xs.reduce((a,b)=>Math.min(a,b),Infinity),xmax=xs.reduce((a,b)=>Math.max(a,b),-Infinity),ymin=ys.reduce((a,b)=>Math.min(a,b),0),ymax=ys.reduce((a,b)=>Math.max(a,b),-Infinity);
 const colors=['#02d2e3','#ffbd69','#ee7596','#93d88b','#bea5ff'];
 const paths=series.map((s,i)=>{const stride=Math.max(1,Math.ceil(s.data.length/1000)),pts=s.data.filter((_,j)=>j%stride===0||j===s.data.length-1);return '<polyline fill="none" stroke="'+colors[i%colors.length]+'" stroke-width="2" points="'+pts.map(p=>(65+(p[0]-xmin)/(xmax-xmin||1)*610)+','+(235-(p[1]-ymin)/(ymax-ymin||1)*200)).join(' ')+'"/>';}).join('');
 const chart=document.createElement('div');chart.innerHTML='<svg viewBox="0 0 720 280" role="img"><path d="M65 30V235H680" fill="none" stroke="#526d7b"/><text x="5" y="40">'+fmt(ymax)+'</text><text x="5" y="235">'+fmt(ymin)+'</text><text x="65" y="260">'+fmt(xmin)+'</text><text x="620" y="260">'+fmt(xmax)+'</text>'+paths+'</svg>';chart.firstChild.setAttribute('aria-label',title+'; eixo horizontal '+xlabel+'; vertical '+ylabel);section.append(chart);
 const legend=document.createElement('p');legend.textContent=xlabel+' / '+ylabel+' · '+series.map((s,i)=>s.name+' ('+['ciano','âmbar','rosa','verde','lilás'][i%5]+')').join(' · ');section.append(legend);$('#charts').append(section);
}
function calculate(){
 clear();try{
  const p=params();if(!$('#provenance').value.trim())throw Error('Identifique a origem dos dados.');
  if(mode!=='lap'&&!observed)throw Error('Carregue telemetria real ou importe um CSV.');
  if(mode!=='ers'&&!dataset)throw Error('Importe o CSV '+(mode==='aero'?'de configurações':'da pista')+'.');
  let output,profile,metric;
  if(mode==='aero'){
   if(dataset.length>100||dataset.length*observed.length>500000)throw Error('Limite de 100 configurações e 500.000 pares configuração/amostra. Reduza o intervalo ou o número de configurações.');
   output=aero(observed,p,dataset);profile=output.flatMap((r,i)=>r.profile.map(v=>({configuration:i+1,...v})));const active=activeAero(observed,p,dataset);metric=active.drag_energy_mj;output={configurations:output,active};profile=active.profile;
   kpis([['Configurações',output.configurations.length,''],['Arrasto · política ativa',metric,'MJ'],['Mudanças de estado',output.active.switches,'']]);
   plot('Carga aerodinâmica · primeiras 5 configurações',output.configurations.slice(0,5).map((r,i)=>({name:'Config. '+(i+1),data:r.profile.map(x=>[x.time_s,x.downforce_n])})),'tempo (s)','carga (N)');
   plot('Potência dissipada no arrasto',output.configurations.slice(0,5).map((r,i)=>({name:'Config. '+(i+1),data:r.profile.map(x=>[x.time_s,x.drag_power_kw])})),'tempo (s)','potência (kW)');
   plot('Comando ativo · carga resultante',[{name:'Política ativa',data:output.active.profile.map(x=>[x.time_s,x.downforce_n])}],'tempo (s)','carga (N)');table($('#table'),output.configurations.map(({profile,...r},i)=>({configuration:i+1,...r})));
  }else if(mode==='ers'){
   output=ers(observed,p);profile=output.profile;metric=output.recovered_mj;
   kpis([['Energia recuperada',output.recovered_mj,'MJ'],['Energia entregue às rodas',output.deployed_wheel_mj,'MJ'],['SoC final',profile.at(-1).soc_pct,'%'],['Erro de balanço',output.balance_error_mj,'MJ']]);
   plot('Estado de carga estimado',[{name:'SoC do modelo',data:profile.map(x=>[x.time_s,x.soc_pct])}],'tempo (s)','SoC (%)');
   plot('Energia acumulada',[{name:'Recuperada na bateria',data:profile.map(x=>[x.time_s,x.recovered_mj])},{name:'Entregue às rodas',data:profile.map(x=>[x.time_s,x.deployed_mj])},{name:'Frenagem por atrito',data:profile.map(x=>[x.time_s,x.friction_mj])}],'tempo (s)','energia (MJ)');table($('#table'),profile);
  }else{
   output=lap(dataset,p);profile=output.profile;metric=output.laptime_s;
   kpis([['Tempo de volta estimado',metric,'s'],['Distância',output.distance_m,'m'],['Velocidade média',output.distance_m/metric*3.6,'km/h']]);
   const series=[{name:'Cenário atual',data:profile.map(x=>[x.distance_m,x.speed_kmh])}];if(reference)series.push({name:'Referência A',data:reference.profile.map(x=>[x.distance_m,x.speed_kmh])});plot('Perfil de velocidade',series,'distância (m)','velocidade (km/h)');table($('#table'),profile);
   // Sensitivity errors are recorded per variation, preserving the valid baseline.
   output.sensitivity=[];for(const key of ['mass','power_kw','mu','cd_area','cl_area','brake_g'])for(const factor of [.9,1.1]){try{const t=lap(dataset,{...p,[key]:p[key]*factor}).laptime_s;output.sensitivity.push({parameter:key,change_pct:Math.round((factor-1)*100),laptime_s:t,delta_s:t-metric});}catch(e){output.sensitivity.push({parameter:key,change_pct:Math.round((factor-1)*100),laptime_s:null,delta_s:null,error:e.message});}}
   const heading=document.createElement('h3');heading.textContent='Sensibilidade individual · ±10%';$('#sensitivity').append(heading);const t=document.createElement('div');t.className='table-wrap';$('#sensitivity').append(t);table(t,output.sensitivity.map(r=>({parameter:r.parameter,change_pct:r.change_pct,laptime_s:r.laptime_s,delta_s:r.delta_s,status:r.error||'Convergente'})));
  }
  result={mode,created_at:new Date().toISOString(),provenance:$('#provenance').value,telemetry_source:source,input_file:dataSource,origin:'model-derived-from-observed-or-user-imported-inputs',parameters:p,method:document.querySelector('main>section.panel p:not(.eyebrow)').textContent,output,profile,metric,reference:reference?{metric:reference.metric,parameters:reference.parameters}:null};
  for(const id of ['json','csv','pin'])$('#'+id).disabled=false;
  $('#comparison').textContent=reference?'B − A: '+fmt(metric-reference.metric)+(mode==='lap'?' s de tempo de volta':mode==='ers'?' MJ recuperados':' MJ de arrasto com política ativa'):'Calcule e fixe um resultado para comparar.';
  status('Cálculo concluído. Resultados estimados; parâmetros e origem incluídos no relatório.');
 }catch(e){clear();status(e.message);}
}
$('#parameters').onsubmit=e=>{e.preventDefault();calculate();};
$('#parameters').oninput=()=>{clear();status('Parâmetros alterados. Recalcule o cenário.');};
$('#provenance').oninput=()=>{clear(true);status('Origem alterada. Recalcule.');};
$('#pin').onclick=()=>{reference={metric:result.metric,parameters:{...result.parameters},profile:result.profile};$('#comparison').textContent='Referência A fixada. Altere parâmetros e calcule B.';};
$('#json').onclick=()=>download(JSON.stringify(result,null,2),'f1-'+mode+'-report.json','application/json');
$('#csv').onclick=()=>download(asCSV(result.profile),'f1-'+mode+'-series.csv','text/csv');
if($('#template'))$('#template').onclick=()=>download(fields[mode].join(',')+'\n',mode+'-header.csv','text/csv');
if($('#telemetry-template'))$('#telemetry-template').onclick=()=>download('time_s,speed_kmh,brake\n','telemetry-header.csv','text/csv');
async function importFile(input,kind){const token=++version;clear(true);if(kind==='telemetry'){observed=null;source='';}else{dataset=null;dataSource='';}const file=input.files[0];if(!file)return;try{if(file.size>5e6)throw Error('Limite de 5 MB.');const content=await file.text();if(token!==version)return;const data=numericCSV(content,kind==='telemetry'?['time_s','speed_kmh','brake']:fields[mode]);if(kind==='telemetry'){observed=telemetry(data);source=file.name;}else{dataset=data;dataSource=file.name;}$('#data-info').textContent=data.length+' linhas importadas de '+file.name+'. Origem não verificada.';status('Dados carregados. Identifique a origem e calcule.');}catch(e){status(e.message);}}
if($('#dataset'))$('#dataset').onchange=()=>importFile($('#dataset'),'dataset');
if($('#telemetry'))$('#telemetry').onchange=()=>importFile($('#telemetry'),'telemetry');
if($('#cad'))$('#cad').onclick=()=>{try{download(wingCAD(params()),'active-wings.scad');status('Geometria conceitual exportada. Abra no OpenSCAD; valide dimensões e malha antes do CFD.');}catch(e){status(e.message);}};
async function real(){
 const token=++version;clear(true);observed=null;$('#real').disabled=true;status('Carregando a sessão histórica…');
 try{race=await loadRace();if(token!==version)return;const select=$('#driver');if(!select.options.length){for(const n of race.replay_window.drivers){const driver=race.drivers.find(x=>x.driver_number===n),o=document.createElement('option');o.value=String(n);o.textContent=driver?.full_name||String(n);select.append(o);}}
 const rows=race.telemetry[select.value];if(!rows?.length)throw Error('Piloto sem telemetria.');
 const start=Date.parse(rows[0].date);observed=telemetry(rows.map(r=>({time_s:(Date.parse(r.date)-start)/1000,speed_kmh:r.speed,brake:r.brake?1:0})));
 source='OpenF1 / session 9472 / driver '+select.value;$('#provenance').value=source;$('#data-info').textContent=observed.length+' amostras reais · '+fmt(observed.at(-1).time_s)+' s · recorte, não volta completa.';status('Telemetria histórica carregada. Revise as hipóteses antes de calcular.');
 }catch(e){if(token===version)status(e.message);}finally{$('#real').disabled=false;}
}
if($('#real')){$('#real').onclick=real;$('#driver').onchange=real;real();}
