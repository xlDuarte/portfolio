import assert from 'node:assert/strict';
import * as E from '../site/motorsport/porsche/engineering.mjs';
const near=(a,b,t=1e-7)=>assert(Math.abs(a-b)<t,`${a} != ${b}`);
// Controlled fixtures test algorithms only. No fixture is shipped as measured session data.
const parsed=E.numericCSV('time_s;speed_kmh\n0;10,5\n1;20,5',['time_s','speed_kmh']);near(parsed[0].speed_kmh,10.5);
assert.throws(()=>E.numericCSV('time_s,speed_kmh\n0,\n1,2',['time_s']));
assert.throws(()=>E.numericCSV('time_s,time_s\n0,0\n1,1',['time_s']));
assert.throws(()=>E.numericCSV('time_s\n0\nInfinity',['time_s']));
const a=[0,1,2,3].map(i=>({time_s:i*10,distance_m:i*100,speed_kmh:36,ax_ms2:-E.G,ay_ms2:E.G,throttle_pct:i<2?0:100,brake_pct:i<2?50:0,steering_roadwheel_deg:5,curvature_1pm:.01}));
const b=a.map(r=>({...r,time_s:r.time_s*1.1,speed_kmh:r.speed_kmh/1.1}));
near(E.acquisitionQuality(a).median_hz,.1);
assert.throws(()=>E.acquisitionQuality([{time_s:0},{time_s:0}]));
const comparison=E.lapComparison(a,b,3);near(comparison.delta_b_minus_a_s,3);near(comparison.sectors.reduce((s,r)=>s+r.loss_b_s,0),3);assert.equal(comparison.priorities_b.length,3);
assert.throws(()=>E.lapComparison(a,b,0));
assert.throws(()=>E.lapComparison(a,b.map(r=>({...r,distance_m:r.distance_m+1000})),3));
const partial=E.lapComparison(a,b.slice(1),2);near(partial.common_start_m,100);near(partial.delta_b_minus_a_s,2);
const driver=E.driverMetrics(a,2.5);near(driver.peak_observed_lateral_g,1);near(driver.peak_braking_g,1);near(driver.braking_time_pct,200/3);near(driver.full_throttle_time_pct,100/3);assert(driver.mean_steering_residual_deg!==null);
assert.equal(E.driverMetrics(a.map(({throttle_pct,brake_pct,steering_roadwheel_deg,curvature_1pm,...r})=>r),2.5).coasting_time_pct,null);
const tire=[-2,-1,0,1,2].map(angle=>({fz_n:3000,fy_n:80000*angle*Math.PI/180,slip_angle_deg:angle}));near(E.tireAnalysis(tire,2).cornering_stiffness_n_per_rad,80000);assert.equal(E.tireAnalysis(tire,2).load_association,null);assert.throws(()=>E.tireAnalysis(tire,.1));
near(E.slipRatio([{speed_ms:20,wheel_omega_rad_s:70}],.3)[0].slip_ratio,.05);assert.equal(E.slipRatio([{speed_ms:.5,wheel_omega_rad_s:2}],.3)[0].slip_ratio,null);
const measurement={cold_pressure_kpa:200,hot_pressure_kpa:230,cold_air_c:20,hot_air_c:50,temp_inner_c:90,temp_middle_c:85,temp_outer_c:80,wear_before_mm:5,wear_inner_mm:4,wear_middle_mm:4.5,wear_outer_mm:4.2,distance_km:100};
const tm=E.tireMeasurements([measurement],100)[0];near(tm.inner_outer_delta_c,10);near(tm.crown_delta_c,0);near(tm.wear_inner_mm_per_100km,1);near(tm.ideal_hot_gauge_kpa,300*323.15/293.15-100);
assert.throws(()=>E.tireMeasurements([{...measurement,cold_air_c:-274}],100));
const pixels=[{x:0,y:0,temp_c:20},{x:1,y:0,temp_c:40},{x:0,y:1,temp_c:60}];near(E.thermalROI(pixels,0,1,0,0).mean_c,30);assert.throws(()=>E.thermalROI(pixels,2,3,2,3));assert.throws(()=>E.thermalROI([...pixels,pixels[0]],0,1,0,1));
const params={laps:10,max_tire_laps:10,base_lap_s:60,fuel_per_lap_l:1,tank_l:10,degradation_s_per_lap:0,pit_loss_s:20,refuel_l_per_s:0};near(E.strategy(params).predicted_race_s,600);assert.equal(E.strategy(params).stops,0);
assert.equal(E.strategy({...params,max_tire_laps:5}).stops,1);near(E.strategy({...params,max_tire_laps:5}).predicted_race_s,620);assert.throws(()=>E.strategy({...params,tank_l:5}));near(E.strategy({...params,tank_l:5,refuel_l_per_s:1}).predicted_race_s,625);assert.throws(()=>E.strategy({...params,laps:1.5}));
// Exhaustive partitions verify the optimizer for a small case with degradation and refuelling.
const small={...params,laps:6,max_tire_laps:3,tank_l:3,degradation_s_per_lap:2,pit_loss_s:3,refuel_l_per_s:1};
function enumerate(remaining,parts=[]){if(!remaining){let cost=0;parts.forEach((n,i)=>cost+=60*n+n*(n-1)+ (i?3+n:0));return cost;}return Math.min(...Array.from({length:Math.min(3,remaining)},(_,i)=>enumerate(remaining-i-1,[...parts,i+1])));}
near(E.strategy(small).predicted_race_s,enumerate(6));near(E.wetCrossover(100,95,20,10).net_saving_s,30);assert.equal(E.wetCrossover(95,100,20,10).break_even_laps,null);
const timing=[{car_id:1,lap:1,lap_time_s:90,pit_lap:0},{car_id:1,lap:2,lap_time_s:120,pit_lap:1},{car_id:2,lap:1,lap_time_s:95,pit_lap:0}];assert.equal(E.timingAnalysis(timing)[0].best_clean_s,90);assert.throws(()=>E.timingAnalysis([...timing,timing[0]]));
const circle=Array.from({length:20},()=>({length_m:20,curvature_1pm:.01}));const car={mass_kg:1200,wheel_power_kw:300,mu:1,brake_g:1,max_speed_kmh:300,drag_area_m2:.6,air_density:1.2};
const sim=E.lapSimulation(circle,car);near(sim.laptime_s,400/Math.sqrt(E.G/.01),.001);assert(E.lapSimulation(circle,{...car,mu:.8}).laptime_s>sim.laptime_s);assert(E.lapSimulation(circle,{...car,wheel_power_kw:5}).laptime_s>sim.laptime_s);assert.throws(()=>E.lapSimulation(circle,{...car,mass_kg:0}));
const setups=[{setup_id:0,lap_time_s:90},{setup_id:0,lap_time_s:92},{setup_id:1,lap_time_s:89},{setup_id:1,lap_time_s:91}];near(E.setupComparison(setups).mean_b_minus_a_s,-1);assert.throws(()=>E.setupComparison([...setups,{setup_id:2,lap_time_s:88}]));
console.log('PASS all 13 engineering modules: validation, measured metrics, regressions, optimizer and solver invariants');
