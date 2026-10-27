import assert from 'node:assert/strict';
import {strategy,ekf,flow,vibration,experiment,replay,monteCarlo} from '../site/motorsport/lab/engine.mjs';
assert(strategy(58,45)[0].stops.length<=strategy(58,5)[0].stops.length);
assert(ekf(0).rmse<ekf(3).rmse);
for(const [x,y] of [[6,-3],[-10,10],[0,0]]){const r=flow(x,y);assert.equal(r.dx,x);assert.equal(r.dy,y);assert.equal(r.error,0)}
assert(vibration(1.35,1).fp>vibration(1.35,2.8).fp);
const r=experiment(100,0);assert(r.losses.at(-1)<r.losses[0]);assert(experiment(100,2).psi>r.psi);
assert(replay(0).every(c=>c.dist===0));assert(replay(100)[0].dist>replay(90)[0].dist);
let mc=monteCarlo([{driver_code:'A',ranking_score:1},{driver_code:'B',ranking_score:5}],1,3000);assert.equal(mc.reduce((s,c)=>s+c.win,0),1);assert(mc[0].win>mc[1].win);
console.log('Seven computational engines passed');
