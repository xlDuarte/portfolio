import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const observed=JSON.parse(await fs.readFile(new URL('../site/motorsport/data/bahrain-2024-race.json',import.meta.url),'utf8'));
globalThis.fetch=async()=>({ok:true,json:async()=>observed});
const {sample,series,snapshot,trail,clampTime,DURATION,DRIVERS}=await import('../site/motorsport/replay/session.mjs');
assert.equal(DURATION,240);assert.deepEqual(DRIVERS.map(d=>d.id),['VER','PER','SAI']);
for(const t of [1,30,90,200,239]){const cars=sample(t);assert.equal(cars.length,3);assert.deepEqual(cars,sample(t,.1));for(const c of cars){assert(Number.isFinite(c.x));const d=DRIVERS.find(d=>d.id===c.driver),raw=observed.telemetry[d.number].find(p=>p.date===c.sample_date);assert.equal(raw.speed,c.speed);assert.equal(raw.n_gear,c.gear);assert(Number.isFinite(c.position))}assert.equal(snapshot(t,1,'VER').origin,'observed');assert(trail(t,1,'VER').length>0)}
for(const d of series()){assert(d.values.length>500);assert(d.values.every(row=>row.every(Number.isFinite)))}
assert.equal(clampTime(-1),0);assert.equal(clampTime(900),240);console.log('PASS real replay: source parity, timestamps, no grip modification, finite coordinates');
