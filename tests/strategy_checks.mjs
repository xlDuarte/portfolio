import assert from 'node:assert/strict';
import {calculate,detail} from '../site/motorsport/strategy/model.mjs';
for(const laps of [20,58,78])for(const loss of [10,22.4,40]){const r=calculate(laps,loss);assert(r.one&&r.two);for(const row of r.rows){const d=detail(row,laps,loss);assert(Math.abs(d.total-row.time)<1e-8);assert.equal(d.points.length,laps);assert.equal(d.stints.reduce((n,s)=>n+s.end-s.start+1,0),laps);assert.equal(d.points.filter(p=>p.pit>0).length,row.stops.length);assert(d.points.every(p=>Number.isFinite(p.pace)));}assert.equal(r.best.time,Math.min(...r.rows.map(x=>x.time)))}
assert.throws(()=>calculate(0,22));console.log('PASS: all candidate totals, stints, pit losses and optimum across bounds');
