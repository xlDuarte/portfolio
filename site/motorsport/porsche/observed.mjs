export const WHEELS=['FL','FR','RL','RR'];
export const CHANNELS=[...WHEELS.map(w=>'load_'+w+'_N'),...WHEELS.map(w=>'temp_'+w+'_C'),'ax_ms2','ay_ms2','damper_velocity_mms','speed_kmh'];

export function parseAcquisition(text){
  const lines=text.replace(/^\uFEFF/,'').trim().split(/\r?\n/);
  if(lines.length<3||lines.length>50001)throw Error('Use entre 2 e 50.000 amostras.');
  const delimiter=lines[0].includes(';')?';':',';
  const names=lines.shift().split(delimiter).map(s=>s.trim());
  if(names[0]!=='time_s'||names.length<2||new Set(names).size!==names.length)throw Error('O cabeçalho deve iniciar com time_s e conter canais únicos.');
  const unknown=names.slice(1).filter(n=>!CHANNELS.includes(n));
  if(unknown.length)throw Error('Canais desconhecidos: '+unknown.join(', '));
  let previous=-Infinity;
  const rows=lines.map((line,i)=>{
    const cells=line.split(delimiter).map(s=>s.trim());
    if(cells.length!==names.length||cells.some(s=>!s))throw Error('Campos ausentes na linha '+(i+2));
    const values=cells.map(s=>Number(delimiter===';'?s.replace(',','.'):s));
    if(values.some(v=>!Number.isFinite(v))||values[0]<=previous)throw Error('Valor inválido ou tempo fora de ordem na linha '+(i+2));
    previous=values[0];
    const row=Object.fromEntries(names.map((n,j)=>[n,values[j]]));
    if(names.some(n=>(n.startsWith('load_')||n==='speed_kmh')&&row[n]<0))throw Error('Carga e velocidade devem ser não negativas na linha '+(i+2));
    return row;
  });
  return {names:names.slice(1),rows,start:rows[0].time_s,end:rows.at(-1).time_s};
}

export function indexAt(rows,time){
  let lo=0,hi=rows.length-1;
  while(lo<hi){const mid=Math.ceil((lo+hi)/2);if(rows[mid].time_s<=time)lo=mid;else hi=mid-1;}
  return lo;
}

export function wheelBalance(row){
  const loads=WHEELS.map(w=>row['load_'+w+'_N']);
  if(!loads.every(Number.isFinite))return null;
  const total=loads.reduce((a,b)=>a+b,0);
  return {total,front:total>0?100*(loads[0]+loads[1])/total:null,cross:total>0?100*(loads[0]+loads[3])/total:null};
}

export function statistics(rows,names){
  if(!rows.length)return {};
  return Object.fromEntries(names.map(name=>{
    let min=Infinity,max=-Infinity,sum=0;
    for(const row of rows){const value=row[name];min=Math.min(min,value);max=Math.max(max,value);sum+=value;}
    return [name,{min,max,mean:sum/rows.length}];
  }));
}

export function sampleForPlot(rows,limit=900){
  if(rows.length<=limit)return rows;
  const step=Math.ceil((rows.length-1)/(limit-1));
  const result=rows.filter((_,i)=>i%step===0);
  if(result.at(-1)!==rows.at(-1))result.push(rows.at(-1));
  return result;
}
