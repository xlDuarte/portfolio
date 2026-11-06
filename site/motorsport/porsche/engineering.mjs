// Independent analysis methods. Inputs are measured channels or explicit scenario assumptions.
export const G=9.80665;
export const mean=a=>a.reduce((s,v)=>s+v,0)/a.length;
export function positive(value,name){if(!Number.isFinite(value)||value<=0)throw Error(name+' deve ser maior que zero.');return value;}
export function nonnegative(value,name){if(!Number.isFinite(value)||value<0)throw Error(name+' deve ser não negativo.');return value;}
export function numericCSV(text,required){
 const lines=text.replace(/^\uFEFF/,'').trim().split(/\r?\n/);
 if(lines.length<3||lines.length>50001)throw Error('Use de 2 a 50.000 linhas de dados.');
 const separator=lines[0].includes(';')?';':',';
 const headers=lines.shift().split(separator).map(s=>s.trim());
 if(new Set(headers).size!==headers.length||headers.some(h=>!/^[a-z][a-z0-9_]*$/.test(h)))throw Error('Cabeçalhos inválidos ou duplicados.');
 if(required.some(h=>!headers.includes(h)))throw Error('Colunas obrigatórias: '+required.join(', '));
 const rows=lines.map((line,i)=>{
  const cells=line.split(separator).map(v=>v.trim());
  if(cells.length!==headers.length||cells.some(v=>v===''))throw Error('Campos ausentes na linha '+(i+2));
  const values=cells.map(v=>Number(separator===';'?v.replace(',','.'):v));
  if(!values.every(Number.isFinite))throw Error('Valor não numérico na linha '+(i+2));
  return Object.fromEntries(headers.map((h,j)=>[h,values[j]]));
 });
 return rows;
}
export function increasing(rows,key){if(rows.some((r,i)=>i>0&&r[key]<=rows[i-1][key]))throw Error(key+' deve ser estritamente crescente.');}
export function percentile(values,p){const a=[...values].sort((x,y)=>x-y);return a[Math.floor((a.length-1)*p)];}
export function regression(x,y){
 if(x.length<3||x.length!==y.length)throw Error('Regressão exige pelo menos três pares.');
 const mx=mean(x),my=mean(y),xx=x.reduce((s,v)=>s+(v-mx)**2,0);
 if(xx<1e-12)throw Error('O eixo independente precisa variar.');
 const slope=x.reduce((s,v,i)=>s+(v-mx)*(y[i]-my),0)/xx,intercept=my-slope*mx;
 const error=x.reduce((s,v,i)=>s+(y[i]-intercept-slope*v)**2,0),yy=y.reduce((s,v)=>s+(v-my)**2,0);
 return {slope,intercept,r2:yy>0?1-error/yy:null,n:x.length};
}
export function acquisitionQuality(rows){
 increasing(rows,'time_s');
 const dt=rows.slice(1).map((r,i)=>r.time_s-rows[i].time_s),median=percentile(dt,.5);
 return {duration_s:rows.at(-1).time_s-rows[0].time_s,samples:rows.length,median_hz:1/median,
  min_interval_s:Math.min(...dt),max_interval_s:Math.max(...dt),p95_interval_s:percentile(dt,.95),gaps_above_3x_median:dt.filter(d=>d>3*median).length};
}
function interpolate(rows,d,key){
 let lo=0,hi=rows.length-1;while(hi-lo>1){const mid=Math.floor((hi+lo)/2);if(rows[mid].distance_m<=d)lo=mid;else hi=mid;}
 const a=rows[lo],b=rows[hi],f=(d-a.distance_m)/(b.distance_m-a.distance_m);return a[key]+f*(b[key]-a[key]);
}
export function lapComparison(a,b,sectors=3){
 [a,b].forEach(rows=>{increasing(rows,'time_s');increasing(rows,'distance_m');rows.forEach(r=>nonnegative(r.speed_kmh,'Velocidade'));});
 if(!Number.isInteger(sectors)||sectors<1||sectors>20)throw Error('Use entre 1 e 20 setores.');
 const start=Math.max(a[0].distance_m,b[0].distance_m),end=Math.min(a.at(-1).distance_m,b.at(-1).distance_m);
 if(end<=start)throw Error('As voltas não têm distância em comum.');
 const ta=interpolate(a,start,'time_s'),tb=interpolate(b,start,'time_s');
 const curve=Array.from({length:401},(_,i)=>{const d=start+(end-start)*i/400;return {distance_m:d,delta_s:(interpolate(b,d,'time_s')-tb)-(interpolate(a,d,'time_s')-ta),speed_a:interpolate(a,d,'speed_kmh'),speed_b:interpolate(b,d,'speed_kmh')};});
 const split=Array.from({length:sectors},(_,i)=>{const x=start+(end-start)*i/sectors,y=start+(end-start)*(i+1)/sectors;const timeA=interpolate(a,y,'time_s')-interpolate(a,x,'time_s'),timeB=interpolate(b,y,'time_s')-interpolate(b,x,'time_s');return {sector:i+1,start_m:x,end_m:y,a_s:timeA,b_s:timeB,loss_b_s:timeB-timeA};});
 return {common_start_m:start,common_end_m:end,a_s:interpolate(a,end,'time_s')-ta,b_s:interpolate(b,end,'time_s')-tb,delta_b_minus_a_s:curve.at(-1).delta_s,sectors:split,priorities_b:split.filter(s=>s.loss_b_s>0).sort((a,b)=>b.loss_b_s-a.loss_b_s),curve};
}
export function driverMetrics(rows,wheelbase){
 acquisitionQuality(rows);positive(wheelbase,'Entre-eixos');rows.forEach(r=>nonnegative(r.speed_kmh,'Velocidade'));
 const has=k=>rows.every(r=>Number.isFinite(r[k]));
 for(const key of ['throttle_pct','brake_pct'])if(has(key)&&rows.some(r=>r[key]<0||r[key]>100))throw Error(key+' deve estar entre 0 e 100.');
 const duration=rows.at(-1).time_s-rows[0].time_s;
 const fraction=test=>100*rows.slice(0,-1).reduce((sum,r,i)=>sum+(test(r)?rows[i+1].time_s-r.time_s:0),0)/duration;
 const balance=has('steering_roadwheel_deg')&&has('curvature_1pm')?rows.filter(r=>Math.abs(r.curvature_1pm)>.001&&r.speed_kmh>20).map(r=>({ay_g:r.ay_ms2/G,residual_deg:Math.sign(r.curvature_1pm)*(r.steering_roadwheel_deg-Math.atan(wheelbase*r.curvature_1pm)*180/Math.PI)})):[];
 return {peak_speed_kmh:Math.max(...rows.map(r=>r.speed_kmh)),peak_observed_lateral_g:Math.max(...rows.map(r=>Math.abs(r.ay_ms2/G))),peak_braking_g:Math.max(0,...rows.map(r=>-r.ax_ms2/G)),braking_time_pct:has('brake_pct')?fraction(r=>r.brake_pct>5):null,full_throttle_time_pct:has('throttle_pct')?fraction(r=>r.throttle_pct>=95):null,coasting_time_pct:has('brake_pct')&&has('throttle_pct')?fraction(r=>r.throttle_pct<=5&&r.brake_pct<=5):null,mean_steering_residual_deg:balance.length?mean(balance.map(r=>r.residual_deg)):null,balance};
}
export function tireAnalysis(rows,linearAngle){
 positive(linearAngle,'Faixa linear');
 rows.forEach(r=>positive(r.fz_n,'Carga vertical'));
 const linear=rows.filter(r=>Math.abs(r.slip_angle_deg)<=linearAngle);
 const stiffness=regression(linear.map(r=>r.slip_angle_deg*Math.PI/180),linear.map(r=>r.fy_n));
 const normalized=rows.map(r=>({load_n:r.fz_n,mu_observed:Math.abs(r.fy_n)/r.fz_n,slip_angle_deg:r.slip_angle_deg}));
 return {cornering_stiffness_n_per_rad:stiffness.slope,linear_fit:stiffness,normalized,peak_observed_mu:Math.max(...normalized.map(r=>r.mu_observed)),load_association:new Set(rows.map(r=>r.fz_n)).size>1?regression(normalized.map(r=>r.load_n),normalized.map(r=>r.mu_observed)):null};
}
export function slipRatio(rows,radius){
 positive(radius,'Raio efetivo');
 return rows.map(r=>{nonnegative(r.speed_ms,'Velocidade');return {...r,slip_ratio:r.speed_ms>=1?(r.wheel_omega_rad_s*radius-r.speed_ms)/r.speed_ms:null};});
}
export function tireMeasurements(rows,ambientKpa,targetHotKpa=null){
 if(targetHotKpa!==null)nonnegative(targetHotKpa,'Pressão-alvo a quente');
 positive(ambientKpa,'Pressão atmosférica');
 return rows.map(r=>{
  ['cold_pressure_kpa','hot_pressure_kpa'].forEach(k=>nonnegative(r[k],k));
  if(r.cold_air_c<=-273.15||r.hot_air_c<=-273.15)throw Error('Temperatura absoluta inválida.');
  positive(r.distance_km,'Distância rodada');
  for(const k of ['wear_before_mm','wear_inner_mm','wear_middle_mm','wear_outer_mm'])nonnegative(r[k],k);
  const predicted=(r.cold_pressure_kpa+ambientKpa)*(r.hot_air_c+273.15)/(r.cold_air_c+273.15)-ambientKpa;
  return {...r,target_cold_gauge_kpa:targetHotKpa===null?null:(targetHotKpa+ambientKpa)*(r.cold_air_c+273.15)/(r.hot_air_c+273.15)-ambientKpa,measured_minus_ideal_hot_kpa:r.hot_pressure_kpa-predicted,ideal_hot_gauge_kpa:(r.cold_pressure_kpa+ambientKpa)*(r.hot_air_c+273.15)/(r.cold_air_c+273.15)-ambientKpa,inner_outer_delta_c:r.temp_inner_c-r.temp_outer_c,crown_delta_c:r.temp_middle_c-(r.temp_inner_c+r.temp_outer_c)/2,wear_inner_mm_per_100km:100*(r.wear_before_mm-r.wear_inner_mm)/r.distance_km,wear_middle_mm_per_100km:100*(r.wear_before_mm-r.wear_middle_mm)/r.distance_km,wear_outer_mm_per_100km:100*(r.wear_before_mm-r.wear_outer_mm)/r.distance_km};
 });
}
export function thermalROI(rows,x0,x1,y0,y1){
 if(x1<x0||y1<y0)throw Error('Limites da região invertidos.');
 const seen=new Set();rows.forEach(r=>{if(!Number.isInteger(r.x)||!Number.isInteger(r.y)||r.x<0||r.y<0)throw Error('Coordenadas de pixel devem ser inteiras e não negativas.');const k=r.x+','+r.y;if(seen.has(k))throw Error('Pixel duplicado.');seen.add(k);});
 const selected=rows.filter(r=>r.x>=x0&&r.x<=x1&&r.y>=y0&&r.y<=y1);
 if(!selected.length)throw Error('Nenhum pixel na região selecionada.');
 const temps=selected.map(r=>r.temp_c);
 return {pixels:selected.length,min_c:Math.min(...temps),mean_c:mean(temps),max_c:Math.max(...temps),range_c:Math.max(...temps)-Math.min(...temps),selected};
}
export function strategy(p){
 ['laps','max_tire_laps'].forEach(k=>{if(!Number.isInteger(p[k])||p[k]<1||p[k]>500)throw Error(k+' deve ser inteiro entre 1 e 500.');});
 ['base_lap_s','fuel_per_lap_l','tank_l'].forEach(k=>positive(p[k],k));
 ['degradation_s_per_lap','pit_loss_s','refuel_l_per_s'].forEach(k=>nonnegative(p[k],k));
 const capacity=Math.floor(p.tank_l/p.fuel_per_lap_l);
 if(capacity<1)throw Error('Combustível insuficiente para uma volta.');
 if(p.refuel_l_per_s===0&&p.laps>capacity)throw Error('Sem reabastecimento, o tanque não comporta a corrida.');
 const maxStint=Math.min(p.max_tire_laps,p.refuel_l_per_s>0?capacity:p.laps),best=Array(p.laps+1).fill(Infinity),plans=Array(p.laps+1);best[0]=0;plans[0]=[];
 for(let lap=1;lap<=p.laps;lap++)for(let length=1;length<=Math.min(lap,maxStint);length++){
  const prior=lap-length,stop=prior>0?p.pit_loss_s:0;
  const fuel=prior>0&&p.refuel_l_per_s>0?length*p.fuel_per_lap_l/p.refuel_l_per_s:0;
  const cost=best[prior]+length*p.base_lap_s+p.degradation_s_per_lap*length*(length-1)/2+stop+fuel;
  if(cost<best[lap]){best[lap]=cost;plans[lap]=[...plans[prior],length];}
 }
 let completed=0;const stints=plans[p.laps].map(length=>{const stint={start_lap:completed+1,end_lap:completed+length,laps:length,fuel_l:length*p.fuel_per_lap_l};completed+=length;return stint;});
 return {predicted_race_s:best[p.laps],stops:stints.length-1,total_fuel_l:p.laps*p.fuel_per_lap_l,stints,assumptions:'Constant base pace, linear age penalty reset at every stop, additive pit and refuel time, no traffic or safety car. Initial fuel is assumed available; when refuelling is enabled, subsequent stint fuel is charged at the entered flow. With no refuelling the total race fuel must fit in the tank.'};
}
export function wetCrossover(dryLap,wetLap,pitLoss,remaining){
 [dryLap,wetLap].forEach(v=>positive(v,'Tempo de volta'));nonnegative(pitLoss,'Perda de parada');positive(remaining,'Voltas restantes');
 const saving=dryLap-wetLap;return {saving_per_lap_s:saving,break_even_laps:saving>0?pitLoss/saving:null,net_saving_s:remaining*saving-pitLoss};
}
export function timingAnalysis(rows){
 rows.forEach(r=>{positive(r.lap_time_s,'Tempo de volta');if(!Number.isInteger(r.lap)||r.lap<1||![0,1].includes(r.pit_lap))throw Error('Volta inválida ou pit_lap fora de 0/1.');});
 const cars=[...new Set(rows.map(r=>r.car_id))];
 return cars.map(id=>{const laps=rows.filter(r=>r.car_id===id).sort((a,b)=>a.lap-b.lap);if(new Set(laps.map(r=>r.lap)).size!==laps.length)throw Error('Volta duplicada por carro.');const clean=laps.filter(r=>r.pit_lap===0).map(r=>r.lap_time_s);return {car_id:id,laps:laps.length,observed_sum_s:laps.reduce((s,r)=>s+r.lap_time_s,0),best_clean_s:clean.length?Math.min(...clean):null,median_clean_s:clean.length?percentile(clean,.5):null,pit_laps:laps.filter(r=>r.pit_lap).map(r=>r.lap)};});
}
export function lapSimulation(track,p){
 for(const k of ['mass_kg','wheel_power_kw','mu','brake_g','max_speed_kmh'])positive(p[k],k);
 nonnegative(p.drag_area_m2,'Área de arrasto');positive(p.air_density,'Densidade do ar');
 track.forEach(r=>{positive(r.length_m,'Comprimento do segmento');if(!Number.isFinite(r.curvature_1pm))throw Error('Curvatura inválida.');});
 const caps=track.map(r=>Math.min(p.max_speed_kmh/3.6,Math.abs(r.curvature_1pm)>1e-9?Math.sqrt(p.mu*G/Math.abs(r.curvature_1pm)):p.max_speed_kmh/3.6));
 const v=[...caps];let converged=false;
 for(let iteration=0;iteration<100;iteration++){
  const before=[...v];
  for(let i=0;i<v.length;i++){const j=(i+1)%v.length,drag=.5*p.air_density*p.drag_area_m2*v[i]**2,force=Math.min(p.mu*p.mass_kg*G,p.wheel_power_kw*1000/Math.max(v[i],1));const accel=(force-drag)/p.mass_kg;v[j]=Math.min(v[j],Math.sqrt(Math.max(.01,v[i]**2+2*accel*track[i].length_m)));}
  for(let i=v.length-1;i>=0;i--){const j=(i+1)%v.length;v[i]=Math.min(v[i],Math.sqrt(v[j]**2+2*Math.min(p.brake_g,p.mu)*G*track[i].length_m));}
  if(v.every((value,i)=>Math.abs(value-before[i])<1e-5)){converged=true;break;}
 }
 if(!converged)throw Error('O solver não convergiu. Revise discretização e parâmetros.');
 let distance=0,time=0;const profile=track.map((r,i)=>{const dt=2*r.length_m/(v[i]+v[(i+1)%v.length]);distance+=r.length_m;time+=dt;return {distance_m:distance,time_s:time,speed_kmh:v[(i+1)%v.length]*3.6};});
 return {laptime_s:time,distance_m:distance,profile,assumptions:'Periodic point-mass model, constant grip, wheel power, quadratic drag, independent lateral and longitudinal limits. No suspension, aero downforce, tire transients or ChassisSim equivalence.'};
}
export function setupComparison(rows){
 const a=rows.filter(r=>r.setup_id===0),b=rows.filter(r=>r.setup_id===1);
 if(a.length<2||b.length<2)throw Error('Use pelo menos duas voltas para cada setup 0 e 1.');
 rows.forEach(r=>{positive(r.lap_time_s,'Tempo de volta');if(![0,1].includes(r.setup_id))throw Error('setup_id deve ser 0 ou 1.');});
 const summary=items=>{const times=items.map(r=>r.lap_time_s),avg=mean(times);return {n:times.length,mean_s:avg,median_s:percentile(times,.5),best_s:Math.min(...times),sample_sd_s:Math.sqrt(times.reduce((s,v)=>s+(v-avg)**2,0)/(times.length-1))};};
 const sa=summary(a),sb=summary(b);return {a:sa,b:sb,mean_b_minus_a_s:sb.mean_s-sa.mean_s,standard_error_difference_s:Math.sqrt(sa.sample_sd_s**2/sa.n+sb.sample_sd_s**2/sb.n)};
}
