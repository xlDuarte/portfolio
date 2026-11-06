import {WHEELS,CHANNELS,parseAcquisition,indexAt,wheelBalance,statistics,sampleForPlot} from './observed.mjs';

const root=document.querySelector('#demo'),$=s=>root.querySelector(s);
const labels={FL:'Dianteira esquerda',FR:'Dianteira direita',RL:'Traseira esquerda',RR:'Traseira direita'};
const colors=['#c8202b','#a47624','#246b8e','#625983'];
const fmt=(v,n=1)=>Number.isFinite(v)?v.toLocaleString('pt-BR',{maximumFractionDigits:n}):'—';
const unit=n=>n.endsWith('_N')?'N':n.endsWith('_C')?'°C':n.endsWith('_ms2')?'m/s²':n.endsWith('_mms')?'mm/s':'km/h';
root.innerHTML=`
<div class="workspace-heading"><div><p class="eyebrow">110 / ACQUISITION WORKSPACE</p><h2>Uma sessão. Quatro rodas.</h2></div><span class="badge">PORSCHE CUP / ENGINEERING</span></div>
<p class="workspace-intro">Inspecione cargas, temperaturas e acelerações no mesmo instante. Importe a aquisição do carro para iniciar a análise.</p>
<div class="workspace">
<aside class="controls">
 <fieldset><legend><b>01</b> Aquisição</legend><label>Arquivo CSV<input id="csv" type="file" accept=".csv,text/csv"></label><small>Até 5 MB ou 50 mil amostras. O arquivo é processado neste navegador.</small><button id="template">Baixar cabeçalho CSV</button></fieldset>
 <fieldset><legend><b>02</b> Trecho</legend><label>Início · segundos<input id="start" type="number" step="any" disabled></label><label>Fim · segundos<input id="end" type="number" step="any" disabled></label><button id="apply" disabled>Aplicar trecho</button><button id="full" disabled>Sessão completa</button><small id="range-info">Selecione uma aquisição.</small></fieldset>
 <fieldset><legend><b>03</b> Reprodução</legend><label>Velocidade<select id="rate"><option value="0.25">0,25×</option><option value="1" selected>1×</option><option value="2">2×</option><option value="5">5×</option></select></label><div class="actions"><button id="play" disabled aria-pressed="false">Reproduzir</button><button id="reset" disabled>Início</button></div></fieldset>
 <fieldset><legend><b>04</b> Exportar</legend><button id="export" disabled>Trecho em CSV</button><button id="summary" disabled>Resumo em JSON</button></fieldset>
 <details><summary>Formato e unidades</summary><p>Primeira coluna <code>time_s</code>. Use vírgula com decimal ponto, ou ponto e vírgula com decimal vírgula. Canais opcionais, preenchidos em todas as linhas.</p><code class="channel-list">${CHANNELS.join('\n')}</code></details>
</aside>
<div class="results">
 <div class="acquisition-status"><span id="source">Nenhuma aquisição carregada</span><p id="status" role="status">Os painéis estão prontos para receber medições.</p></div>
 <div class="kpis"><div><span>CARGA TOTAL</span><strong id="total">—</strong><small>Soma das quatro rodas</small></div><div><span>EIXO DIANTEIRO</span><strong id="front">—</strong><small>Percentual da carga total</small></div><div><span>CARGA CRUZADA</span><strong id="cross">—</strong><small>DE + TD / total</small></div><div><span>VELOCIDADE</span><strong id="speed">—</strong><small>Canal medido · km/h</small></div></div>
 <section class="scrubber"><label for="seek">Instante selecionado <output id="clock">—</output></label><input id="seek" type="range" min="0" max="1" step="any" value="0" disabled><p>Exibição da última amostra anterior ao cursor. Os gráficos mostram o trecho selecionado.</p></section>
 <div class="panel-grid">
  <section class="panel"><div class="panel-head"><h3>01 / Cargas por roda</h3><span class="unit">NEWTONS</span></div><div class="wheel-loads">${WHEELS.map((w,i)=>`<div><span>${labels[w]}</span><strong id="load-${w}">—</strong><div class="load-track"><i id="bar-${w}" style="--wheel:${colors[i]}"></i></div></div>`).join('')}</div><div id="loads-chart" class="chart"></div><p class="caption">A divisão por eixo e a carga cruzada exigem os quatro canais. A carga total inclui todas as contribuições presentes na medição.</p></section>
  <section class="panel"><div class="panel-head"><h3>02 / Temperatura dos pneus</h3><span class="unit">CELSIUS</span></div><div class="tire-map">${WHEELS.map(w=>`<button class="tire" data-wheel="${w}" aria-pressed="${w==='FL'}"><span>${labels[w]}</span><strong id="temp-${w}">—</strong><small id="delta-${w}">Canal ausente</small></button>`).join('')}<div class="car-axis" aria-hidden="true">↑<br>911<br>CUP</div></div><div id="temps-chart" class="chart"></div><p class="caption">Cor relativa ao mínimo e máximo medidos no trecho. Um canal por roda. A localização e o tipo do sensor dependem da aquisição.</p></section>
  <section class="panel"><div class="panel-head"><h3>03 / Dinâmica longitudinal e lateral</h3><span class="unit">m/s²</span></div><div class="dynamic-readings"><span>Longitudinal <b id="ax">—</b></span><span>Lateral <b id="ay">—</b></span></div><div id="gg-chart" class="chart"></div><p class="caption">Diagrama de acelerações ax × ay. A convenção de sinais e a remoção da gravidade devem ser confirmadas na aquisição.</p></section>
  <section class="panel"><div class="panel-head"><h3>04 / Evolução temporal</h3></div><label>Canal<select id="channel" disabled></select></label><div id="signal-chart" class="chart"></div><p id="signal-stats" class="caption">Mínimo, média amostral e máximo do trecho.</p></section>
 </div>
 <section class="panel session-summary"><h3>Resumo do trecho</h3><div class="table-scroll"><table><thead><tr><th>Canal</th><th>Unidade</th><th>Mínimo</th><th>Média amostral</th><th>Máximo</th></tr></thead><tbody id="statistics"><tr><td colspan="5">Aguardando aquisição.</td></tr></tbody></table></div><p class="caption">As estatísticas usam todas as amostras. Os gráficos reduzem a quantidade de pontos e podem omitir picos estreitos. A exportação preserva todas as amostras do trecho.</p></section>
</div></div>`;

let data=null,rows=[],stats={},filename='',time=0,playing=false,previousFrame=null,selected='FL',frameId=null,importVersion=0;
const controls=['start','end','apply','full','play','reset','export','summary','seek','channel'];
function stop(){playing=false;previousFrame=null;cancelAnimationFrame(frameId);frameId=null;$('#play').textContent='Reproduzir';$('#play').setAttribute('aria-pressed','false');}
function download(text,name,type){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function blank(target,message='Canal indisponível nesta aquisição.'){ $(target).innerHTML=`<div class="empty-panel">${message}</div>`; }
function resetData(){stop();data=null;rows=[];stats={};controls.forEach(id=>$('#'+id).disabled=true);$('#channel').replaceChildren();$('#source').textContent='Nenhuma aquisição carregada';$('#statistics').innerHTML='<tr><td colspan="5">Aguardando aquisição.</td></tr>';$('#signal-stats').textContent='';$('#range-info').textContent='Selecione uma aquisição.';$('#clock').textContent='—';['total','front','cross','speed','ax','ay',...WHEELS.map(w=>'load-'+w),...WHEELS.map(w=>'temp-'+w)].forEach(id=>$('#'+id).textContent='—');WHEELS.forEach(w=>{$('#bar-'+w).style.width='0%';$('#temp-'+w).parentElement.style.background='';$('#delta-'+w).textContent='Canal ausente';});['loads-chart','temps-chart','gg-chart','signal-chart'].forEach(id=>blank('#'+id,'Importe uma aquisição para visualizar.'));delete root.dataset.ready;}
function available(names){return names.filter(n=>data.names.includes(n));}
function lineChart(target,names){
 if(!names.length){blank(target);return;}
 const extrema=names.flatMap(n=>[stats[n].min,stats[n].max]),lo=Math.min(...extrema),hi=Math.max(...extrema),span=hi-lo||1;
 const start=rows[0].time_s,duration=rows.at(-1).time_s-start||1,points=sampleForPlot(rows);
 const y=v=>210-(v-lo)/span*170;
 $(target).innerHTML=`<svg viewBox="0 0 600 260" role="img" aria-label="Série temporal dos canais ${names.join(', ')}"><path d="M55 25V210H580" fill="none" stroke="#cbd0d3"/><text x="4" y="35">${fmt(hi)}</text><text x="4" y="210">${fmt(lo)}</text>${names.map((n,i)=>`<polyline fill="none" stroke="${colors[i]}" stroke-width="2" points="${points.map(r=>`${55+(r.time_s-start)/duration*525},${y(r[n])}`).join(' ')}"/>`).join('')}<line class="time-cursor" x1="55" x2="55" y1="25" y2="210" stroke="#1b1e22" stroke-dasharray="4 4"/><text x="55" y="235">${fmt(start,2)} s</text><text x="500" y="235">${fmt(rows.at(-1).time_s,2)} s</text></svg><div class="chart-legend">${names.map((n,i)=>`<span style="--wheel:${colors[i]}">${n}</span>`).join('')}</div>`;
}
function drawGG(){
 if(!data.names.includes('ax_ms2')||!data.names.includes('ay_ms2')){blank('#gg-chart','São necessários os canais ax_ms2 e ay_ms2.');return;}
 const bound=Math.max(Math.abs(stats.ax_ms2.min),Math.abs(stats.ax_ms2.max),Math.abs(stats.ay_ms2.min),Math.abs(stats.ay_ms2.max),1);
 $('#gg-chart').dataset.bound=bound;
 $('#gg-chart').innerHTML=`<svg viewBox="0 0 600 260" role="img" aria-label="Diagrama de aceleração lateral versus longitudinal"><path d="M190 130H410M300 20V240" stroke="#cbd0d3"/><circle cx="300" cy="130" r="100" fill="none" stroke="#e2e3e4"/>${sampleForPlot(rows,600).map(r=>`<circle cx="${300+r.ay_ms2/bound*100}" cy="${130-r.ax_ms2/bound*100}" r="2" fill="#888" opacity=".45"/>`).join('')}<circle id="gg-current" r="5" fill="#c8202b"/><text x="415" y="135">ay +${fmt(bound)}</text><text x="305" y="20">ax +${fmt(bound)}</text></svg>`;
}
function renderInstant(){
 if(!rows.length)return;
 const row=rows[indexAt(rows,time)],balance=wheelBalance(row);
 $('#clock').textContent=fmt(row.time_s,3)+' s';$('#seek').value=time;
 $('#total').textContent=balance?fmt(balance.total/1000,2)+' kN':'—';$('#front').textContent=balance?.front!=null?fmt(balance.front)+' %':'—';$('#cross').textContent=balance?.cross!=null?fmt(balance.cross)+' %':'—';$('#speed').textContent=fmt(row.speed_kmh);$('#ax').textContent=fmt(row.ax_ms2,2);$('#ay').textContent=fmt(row.ay_ms2,2);
 const temps=available(WHEELS.map(w=>'temp_'+w+'_C')),min=temps.length?Math.min(...temps.map(n=>stats[n].min)):0,max=temps.length?Math.max(...temps.map(n=>stats[n].max)):1;
 const peak=Math.max(1,...available(WHEELS.map(w=>'load_'+w+'_N')).map(n=>stats[n].max));
 for(const w of WHEELS){const load=row['load_'+w+'_N'],temp=row['temp_'+w+'_C'];$('#load-'+w).textContent=Number.isFinite(load)?fmt(load)+' N':'—';$('#bar-'+w).style.width=(Number.isFinite(load)?load/peak*100:0)+'%';$('#temp-'+w).textContent=Number.isFinite(temp)?fmt(temp)+' °C':'—';$('#temp-'+w).parentElement.style.background=Number.isFinite(temp)?`hsl(${210-210*(temp-min)/(max-min||1)} 65% 91%)`:'';$('#delta-'+w).textContent=Number.isFinite(temp)?'Δ início '+fmt(temp-rows[0]['temp_'+w+'_C'])+' °C':'Canal ausente';}
 const fraction=(time-rows[0].time_s)/(rows.at(-1).time_s-rows[0].time_s||1);
 root.querySelectorAll('.time-cursor').forEach(el=>{el.setAttribute('x1',55+fraction*525);el.setAttribute('x2',55+fraction*525);});
 const dot=$('#gg-current');if(dot){const bound=Number($('#gg-chart').dataset.bound);dot.setAttribute('cx',300+row.ay_ms2/bound*100);dot.setAttribute('cy',130-row.ax_ms2/bound*100);}
}
function renderChannel(){const name=$('#channel').value;lineChart('#signal-chart',[name]);const s=stats[name];$('#signal-stats').textContent=`${name} · mínimo ${fmt(s.min)} · média amostral ${fmt(s.mean)} · máximo ${fmt(s.max)} ${unit(name)}`;renderInstant();}
function applyRange(start,end){
 if(!data)return;
 if(!Number.isFinite(start)||!Number.isFinite(end)||start>=end||start<data.start||end>data.end)throw Error('Use um intervalo crescente dentro da sessão.');
 const subset=data.rows.filter(r=>r.time_s>=start&&r.time_s<=end);if(subset.length<2)throw Error('O trecho deve conter pelo menos duas amostras.');
 stop();rows=subset;stats=statistics(rows,data.names);time=rows[0].time_s;
 $('#start').value=start;$('#end').value=end;$('#seek').min=rows[0].time_s;$('#seek').max=rows.at(-1).time_s;
 $('#range-info').textContent=`${rows.length.toLocaleString('pt-BR')} amostras · ${fmt(rows.at(-1).time_s-rows[0].time_s,3)} s`;
 $('#statistics').innerHTML=data.names.map(n=>`<tr><td>${n}</td><td>${unit(n)}</td><td>${fmt(stats[n].min,2)}</td><td>${fmt(stats[n].mean,2)}</td><td>${fmt(stats[n].max,2)}</td></tr>`).join('');
 lineChart('#loads-chart',available(WHEELS.map(w=>'load_'+w+'_N')));lineChart('#temps-chart',available(['temp_'+selected+'_C']));drawGG();renderChannel();renderInstant();
}
$('#csv').onchange=async()=>{const version=++importVersion;resetData();delete root.dataset.error;const file=$('#csv').files[0];if(!file){$('#status').textContent='Nenhum arquivo selecionado.';return;}try{if(file.size>5e6)throw Error('Arquivo maior que 5 MB.');const text=await file.text();if(version!==importVersion)return;const parsed=parseAcquisition(text);data=parsed;filename=file.name;$('#channel').replaceChildren(...data.names.map(n=>{const o=document.createElement('option');o.value=n;o.textContent=n+' · '+unit(n);return o;}));controls.forEach(id=>$('#'+id).disabled=false);applyRange(data.start,data.end);$('#source').textContent=filename+' · '+data.names.length+' canais';$('#status').textContent='Aquisição fornecida pelo usuário. Origem e calibração dos sensores não verificadas.';root.dataset.ready='true';}catch(error){if(version!==importVersion)return;resetData();root.dataset.error='true';$('#status').textContent=error.message;}};
$('#apply').onclick=()=>{try{if(!$('#start').value||!$('#end').value)throw Error('Preencha os dois limites.');applyRange(Number($('#start').value),Number($('#end').value));$('#status').textContent='Trecho atualizado.';}catch(error){$('#status').textContent=error.message;}};
$('#full').onclick=()=>applyRange(data.start,data.end);
$('#seek').oninput=()=>{stop();time=Number($('#seek').value);renderInstant();};
$('#reset').onclick=()=>{stop();time=rows[0].time_s;renderInstant();};
function frame(now){if(!playing)return;if(previousFrame!==null)time=Math.min(rows.at(-1).time_s,time+(now-previousFrame)/1000*Number($('#rate').value));previousFrame=now;renderInstant();if(time>=rows.at(-1).time_s){stop();return;}frameId=requestAnimationFrame(frame);}
$('#play').onclick=()=>{if(playing){stop();return;}if(time>=rows.at(-1).time_s)time=rows[0].time_s;playing=true;$('#play').textContent='Pausar';$('#play').setAttribute('aria-pressed','true');frameId=requestAnimationFrame(frame);};
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
$('#channel').onchange=renderChannel;
root.querySelectorAll('[data-wheel]').forEach(b=>b.onclick=()=>{selected=b.dataset.wheel;root.querySelectorAll('[data-wheel]').forEach(button=>button.setAttribute('aria-pressed',String(button===b)));if(data){lineChart('#temps-chart',available(['temp_'+selected+'_C']));renderInstant();}});
$('#template').onclick=()=>download(['time_s',...CHANNELS].join(',')+'\n','porsche-acquisition-header.csv','text/csv');
$('#export').onclick=()=>download(['time_s',...data.names].join(',')+'\n'+rows.map(r=>[r.time_s,...data.names.map(n=>r[n])].join(',')).join('\n')+'\n','porsche-selected-window.csv','text/csv');
$('#summary').onclick=()=>download(JSON.stringify({source:filename,provenance:'user-upload-unverified',start:rows[0].time_s,end:rows.at(-1).time_s,samples:rows.length,statistics:stats,mean_method:'arithmetic sample mean'},null,2),'porsche-session-summary.json','application/json');
resetData();
