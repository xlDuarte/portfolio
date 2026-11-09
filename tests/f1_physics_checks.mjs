import assert from 'node:assert/strict';
import {aero,ers,lap,sensitivity,wingCAD,telemetry} from '../site/motorsport/physics/models.mjs';
const near=(a,b,t=1e-8)=>assert.ok(Math.abs(a-b)<t, a+' != '+b);
// Controlled analytic fixtures are tests only, never shipped as session data.
const rows=[{time_s:0,speed_kmh:72,brake:1},{time_s:1,speed_kmh:36,brake:0},{time_s:2,speed_kmh:72,brake:0}];
const p={mass:1000,capacity:4,initial_soc:50,regen_kw:350,deploy_kw:350,rho:1.2,drag_area:0,eta_charge:.8,eta_discharge:.9};
const r=ers(rows,p);near(r.available_brake_mj,.15);near(r.recovered_mj,.12);near(r.deployed_wheel_mj,.15);near(r.final_energy_mj,2+.12-.15/.9);near(r.balance_error_mj,0);
for(const initial_soc of [0,1,50,99,100])for(const capacity of [.001,.01,4])for(const regen_kw of [1,350]){
 const x=ers(rows,{...p,initial_soc,capacity,regen_kw});near(x.balance_error_mj,0);assert.ok(x.profile.every(r=>r.soc_pct>=-1e-9&&r.soc_pct<=100+1e-9));assert.ok(x.recovered_mj<=x.available_brake_mj+1e-9);
}
near(ers(rows,{...p,regen_kw:10}).recovered_mj,.008);
near(ers(rows,{...p,initial_soc:100}).recovered_mj,0);
near(ers(rows,{...p,drag_area:1000}).available_brake_mj,0);
near(ers(rows.map(r=>({...r,brake:0})),p).recovered_mj,0);
for(const changes of [{mass:0},{eta_charge:1.1},{capacity:-1},{initial_soc:101},{initial_soc:NaN}])assert.throws(()=>ers(rows,{...p,...changes}));
assert.throws(()=>telemetry([{time_s:0,speed_kmh:1,brake:0},{time_s:0,speed_kmh:2,brake:0}]));
assert.throws(()=>telemetry(rows.map(r=>({...r,brake:2}))));
const configs=[{front_deg:10,rear_deg:15,cd:1,cl_down:2},{front_deg:0,rear_deg:0,cd:.5,cl_down:1}];
const a=aero(rows,{rho:1.2,area:1},configs);near(a[0].profile[0].drag_n,240);near(a[0].profile[0].downforce_n,480);near(a[0].drag_energy_mj,.0054);near(a[0].drag_energy_mj,2*a[1].drag_energy_mj);
assert.throws(()=>aero(rows,{rho:0,area:1},configs));
const circle=Array.from({length:100},()=>({length_m:10,curvature_1pm:.01})),car={mass:1000,power_kw:500,mu:1,brake_g:1,max_kmh:300,rho:1.2,cd_area:0,cl_area:0};
const l=lap(circle,car);near(l.laptime_s,1000/Math.sqrt(9.80665/.01),1e-6);near(l.profile[0].speed_kmh,l.profile.at(-1).speed_kmh);
assert.ok(lap(circle,{...car,mu:.8}).laptime_s>l.laptime_s);
assert.ok(lap(circle,{...car,cl_area:2}).laptime_s<l.laptime_s);
near(lap(circle.flatMap(r=>[{...r,length_m:5},{...r,length_m:5}]),car).laptime_s,l.laptime_s);
assert.throws(()=>lap(circle,{...car,mass:0}));assert.throws(()=>lap([{length_m:100,curvature_1pm:0},...circle],car));
assert.equal(sensitivity(circle,car).length,12);
assert.ok(wingCAD({span:1.5,chord:.3,front_deg:10,rear_deg:15}).includes('polygon(points)'));
assert.throws(()=>wingCAD({span:-1,chord:1,front_deg:0,rear_deg:0}));
console.log('PASS F1 physics: energy conservation, battery limits, aero equations, periodic lap solver, sensitivity, CAD validation.');
