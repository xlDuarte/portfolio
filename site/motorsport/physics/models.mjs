// SI units. Independent engineering scenarios, never measured proprietary F1 outputs.
export const G=9.80665;
function finite(x,n){if(!Number.isFinite(x))throw Error(n+' deve ser finito.');}
function positive(x,n){finite(x,n);if(x<=0)throw Error(n+' deve ser positivo.');}
function nonnegative(x,n){finite(x,n);if(x<0)throw Error(n+' não pode ser negativo.');}
export function telemetry(rows){
 if(rows.length<2||rows.length>50000)throw Error('Use 2 a 50.000 amostras.');
 rows.forEach((r,i)=>{finite(r.time_s,'Tempo');nonnegative(r.speed_kmh,'Velocidade');if(![0,1].includes(r.brake))throw Error('brake deve ser 0 ou 1.');if(i&&r.time_s<=rows[i-1].time_s)throw Error('Tempo deve crescer estritamente.');});
 return rows;
}
export function aero(rows,p,configs){
 telemetry(rows);positive(p.rho,'Densidade');positive(p.area,'Área');
 if(!configs.length)throw Error('Importe configurações aerodinâmicas.');
 configs.forEach(c=>{['front_deg','rear_deg'].forEach(k=>finite(c[k],k));['cd','cl_down'].forEach(k=>nonnegative(c[k],k));});
 return configs.map(c=>{
  let work=0,down=0,duration=0;
  const profile=rows.map((r,i)=>{const v=r.speed_kmh/3.6,q=.5*p.rho*v*v,drag=q*p.area*c.cd,force=q*p.area*c.cl_down;
   const out={time_s:r.time_s,drag_n:drag,downforce_n:force,drag_power_kw:drag*v/1000};
   if(i){const dt=r.time_s-rows[i-1].time_s,old=rows[i-1].speed_kmh/3.6;work+=.25*p.rho*p.area*c.cd*(v**3+old**3)*dt;down+=.25*p.rho*p.area*c.cl_down*(v*v+old*old)*dt;duration+=dt;}
   return out;
  });
  return {...c,drag_energy_mj:work/1e6,mean_downforce_n:down/duration,efficiency:c.cd?c.cl_down/c.cd:null,profile};
 });
}
export function ers(rows,p){
 telemetry(rows);['mass','capacity','regen_kw','deploy_kw','rho'].forEach(k=>positive(p[k],k));nonnegative(p.drag_area,'Área de arrasto');
 for(const k of ['eta_charge','eta_discharge']){positive(p[k],k);if(p[k]>1)throw Error('Eficiências devem estar em (0,1].');}
 if(!Number.isFinite(p.initial_soc)||p.initial_soc<0||p.initial_soc>100)throw Error('SoC entre 0 e 100.');
 let energy=p.capacity*p.initial_soc/100,recovered=0,deployed=0,available=0,friction=0,loss=0;
 const initial=energy,profile=[{time_s:rows[0].time_s,soc_pct:p.initial_soc,recovered_mj:0,deployed_mj:0,friction_mj:0}];
 for(let i=1;i<rows.length;i++){
  const a=rows[i-1],b=rows[i],dt=b.time_s-a.time_s,v=a.speed_kmh/3.6,w=b.speed_kmh/3.6;
  // Piecewise constant brake status from the interval's left sample.
  const kineticLoss=Math.max(0,.5*p.mass*(v*v-w*w))/1e6;
  const dragWork=.25*p.rho*p.drag_area*(v**3+w**3)*dt/1e6;
  const brakeWork=a.brake?Math.max(0,kineticLoss-dragWork):0;
  const mechanical=Math.min(brakeWork,p.regen_kw*dt/1000,(p.capacity-energy)/p.eta_charge);
  const charged=mechanical*p.eta_charge;
  energy+=charged;available+=brakeWork;recovered+=charged;friction+=brakeWork-mechanical;loss+=mechanical-charged;
  // Deploy only to positive kinetic-energy increments; no powertrain or demand measurement is implied.
  const demand=!a.brake?Math.max(0,.5*p.mass*(w*w-v*v))/1e6:0;
  const wheel=Math.min(demand,p.deploy_kw*dt/1000,energy*p.eta_discharge),draw=wheel/p.eta_discharge;
  energy-=draw;deployed+=wheel;loss+=draw-wheel;
  profile.push({time_s:b.time_s,soc_pct:100*energy/p.capacity,recovered_mj:recovered,deployed_mj:deployed,friction_mj:friction});
 }
 return {initial_energy_mj:initial,final_energy_mj:energy,recovered_mj:recovered,deployed_wheel_mj:deployed,available_brake_mj:available,friction_mj:friction,conversion_loss_mj:loss,balance_error_mj:initial+available-friction-deployed-loss-energy,profile};
}
export function lap(track,p){
 if(track.length<3||track.length>10000)throw Error('Use 3 a 10.000 segmentos.');
 ['mass','power_kw','mu','brake_g','max_kmh','rho'].forEach(k=>positive(p[k],k));
 ['cd_area','cl_area'].forEach(k=>nonnegative(p[k],k));
 track.forEach(r=>{positive(r.length_m,'Comprimento');finite(r.curvature_1pm,'Curvatura');if(r.length_m>50)throw Error('Discretize a pista em segmentos de até 50 m.');});
 const max=p.max_kmh/3.6,n=track.length;
 const caps=track.map(r=>{const denominator=p.mass*Math.abs(r.curvature_1pm)-.5*p.mu*p.rho*p.cl_area;return denominator>0?Math.min(max,Math.sqrt(p.mu*p.mass*G/denominator)):max;});
 const v=[...caps];
 const grip=(i,speed)=>{const total=p.mu*(p.mass*G+.5*p.rho*p.cl_area*speed**2),lat=p.mass*speed**2*Math.abs(track[i].curvature_1pm);return Math.sqrt(Math.max(0,total**2-lat**2));};
 let converged=false;
 for(let k=0;k<500;k++){
  const old=[...v];
  for(let i=0;i<n;i++){const j=(i+1)%n,force=Math.min(grip(i,v[i]),p.power_kw*1000/Math.max(v[i],.1)),drag=.5*p.rho*p.cd_area*v[i]**2;
   v[j]=Math.min(v[j],Math.sqrt(Math.max(.0001,v[i]**2+2*(force-drag)/p.mass*track[i].length_m)));}
  for(let i=n-1;i>=0;i--){const j=(i+1)%n;const decel=Math.min(p.brake_g*G,grip(j,v[j])/p.mass);v[i]=Math.min(v[i],Math.sqrt(v[j]**2+2*decel*track[i].length_m));}
  if(v.every((x,i)=>Math.abs(x-old[i])<1e-6)){converged=true;break;}
 }
 if(!converged)throw Error('Sem convergência. Revise discretização, potência e arrasto.');
 let distance=0,time=0;const profile=[{distance_m:0,time_s:0,speed_kmh:v[0]*3.6}];
 track.forEach((r,i)=>{distance+=r.length_m;time+=2*r.length_m/(v[i]+v[(i+1)%n]);profile.push({distance_m:distance,time_s:time,speed_kmh:v[(i+1)%n]*3.6});});
 return {laptime_s:time,distance_m:distance,profile};
}
export function sensitivity(track,p){const baseline=lap(track,p).laptime_s;return ['mass','power_kw','mu','cd_area','cl_area','brake_g'].flatMap(parameter=>[-.1,.1].map(change=>({parameter,change_pct:100*change,laptime_s:lap(track,{...p,[parameter]:p[parameter]*(1+change)}).laptime_s}))).map(r=>({...r,delta_s:r.laptime_s-baseline}));}
export function wingCAD(p){
 ['span','chord'].forEach(k=>positive(p[k],k));['front_deg','rear_deg'].forEach(k=>finite(p[k],k));
 return '// Concept geometry, metres. NACA 0012 symmetric wing pair. Not a homologated F1 car or CFD result.\n'+
 'span='+p.span+'; chord='+p.chord+';\n'+
 'function yt(x)=5*0.12*(0.2969*sqrt(x)-0.1260*x-0.3516*x*x+0.2843*x*x*x-0.1036*x*x*x*x);\n'+
 'points=concat([for(i=[0:80]) let(x=(1-cos(i*180/80))/2) [chord*x,chord*yt(x)]],[for(i=[79:-1:1]) let(x=(1-cos(i*180/80))/2) [chord*x,-chord*yt(x)]]);\n'+
 'module wing(angle){rotate([angle,0,0]) rotate([90,0,90]) linear_extrude(height=span,center=true) polygon(points);}\n'+
 'wing('+p.front_deg+'); translate([0,3,0.5]) wing('+p.rear_deg+');\n';
}

export function activeAero(rows,p,configs){
 positive(p.switch_kmh,'Velocidade de ativação');nonnegative(p.hysteresis_kmh,'Histerese');
 if(p.hysteresis_kmh>=p.switch_kmh)throw Error('Histerese deve ser menor que a velocidade de ativação.');
 const cases=aero(rows,p,configs),low=cases.reduce((a,b)=>b.cd<a.cd?b:a),high=cases.reduce((a,b)=>b.cl_down>a.cl_down?b:a);
 let open=false,switches=0,energy=0;
 const profile=rows.map((r,i)=>{
  const prior=open;
  if(r.brake||r.speed_kmh<p.switch_kmh-p.hysteresis_kmh)open=false;
  else if(r.speed_kmh>=p.switch_kmh)open=true;
  if(i&&prior!==open)switches++;
  const c=open?low:high,x=c.profile[i],v={...x,low_drag:open?1:0,front_deg:c.front_deg,rear_deg:c.rear_deg};
  return v;
 });
 for(let i=1;i<profile.length;i++)energy+=(profile[i].drag_power_kw+profile[i-1].drag_power_kw)/2*(rows[i].time_s-rows[i-1].time_s)/1000;
 return {drag_energy_mj:energy,switches,profile,policy:'min Cd above threshold, max Cl_down with brake or below threshold minus hysteresis; instantaneous commanded states, not FIA logic'};
}
