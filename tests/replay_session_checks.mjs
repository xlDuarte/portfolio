import assert from 'node:assert/strict';
import {sample,series,snapshot,trail,clampTime,DURATION} from '../site/motorsport/replay/session.mjs';
import {replay} from '../site/motorsport/lab/engine.mjs';
for(const grip of [.85,1,1.15])for(const t of [0,90,450,900]){
 assert.deepEqual(sample(t,grip),replay(t,grip));
 const out=snapshot(t,grip,'DRV-B');
 assert.equal(out.selected.driver,'DRV-B');
 assert(Number.isFinite(out.selected.acceleration));
 assert.equal(trail(t,grip,'DRV-B').length,41);
 const end=trail(t,grip,'DRV-B').at(-1);assert.equal(end[0],out.selected.x);assert.equal(end[1],out.selected.y);
}
const rows=series(1);assert.equal(rows.length,3);
for(const d of rows){assert.equal(d.values.length,1801);assert.equal(d.values[0][0],0);assert.equal(d.values.at(-1)[0],900);assert(d.values.every(v=>v.every(Number.isFinite)));assert.equal(d.values[180][1],sample(90).find(c=>c.driver===d.id).speed)}
assert.equal(clampTime(-10),0);assert.equal(clampTime(1000),DURATION);console.log('Replay: engine parity, synchronized series, trails, exports and bounds passed');
