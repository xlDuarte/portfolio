import assert from 'node:assert/strict';
import {parseAcquisition,wheelBalance,indexAt,statistics,sampleForPlot} from '../site/motorsport/porsche/observed.mjs';

// Small deterministic fixtures exercise the parser; they are never shipped as session data.
const data=parseAcquisition('\uFEFFtime_s;load_FL_N;load_FR_N;load_RL_N;load_RR_N;temp_FL_C\n0;1000;2000;3000;4000;70,5\n0,2;2000;3000;4000;5000;71,5');
assert.equal(data.rows[0].temp_FL_C,70.5);
assert.equal(wheelBalance(data.rows[0]).total,10000);
assert.equal(wheelBalance(data.rows[0]).front,30);
assert.equal(wheelBalance(data.rows[0]).cross,50);
assert.equal(wheelBalance({load_FL_N:1}),null);
assert.equal(wheelBalance({load_FL_N:0,load_FR_N:0,load_RL_N:0,load_RR_N:0}).front,null);
assert.equal(indexAt(data.rows,.1),0);assert.equal(indexAt(data.rows,.2),1);
assert.equal(statistics(data.rows,data.names).temp_FL_C.mean,71);
for(const csv of ['time_s,temp_FL_C\n0,NaN\n1,70','time_s,temp_FL_C\n0,70\n0,71','time_s,temp_FL_C\n0,\n1,71','time_s,temp_FL_C,temp_FL_C\n0,1,1\n1,2,2','time_s,unknown\n0,1\n1,2','time_s,load_FL_N\n0,-1\n1,2','time_s,temp_FL_C\n0,1,2\n1,2,3'])assert.throws(()=>parseAcquisition(csv));
assert.deepEqual(parseAcquisition('time_s,ax_ms2\n0,-9.81\n1,2').names,['ax_ms2']);
const many=Array.from({length:50000},(_,time_s)=>({time_s})),points=sampleForPlot(many);
assert.equal(points[0],many[0]);assert.equal(points.at(-1),many.at(-1));assert(points.length<=900);
console.log('PASS parser, missing channels, zero load, chronology, statistics, and plot bounds');
