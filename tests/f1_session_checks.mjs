import assert from 'node:assert/strict';
import {createLoadGate,parseSession} from '../site/motorsport/physics/session.mjs';
const gate=createLoadGate(),t1=gate.begin('telemetry'),d1=gate.begin('dataset');
assert(t1());assert(d1());const t2=gate.begin('telemetry');
assert(!t1());assert(t2());assert(d1());gate.invalidate('dataset');assert(!d1());assert(t2());
// Fixtures validate the import contract only. They are not shipped as race data.
const session={schema:'f1-physics-session/v1',provenance:{source:'FastF1',year:2024,event:'Test fixture',driver:'TST',observed_laptime_s:90},telemetry:[{time_s:0,speed_kmh:100,brake:0},{time_s:1,speed_kmh:90,brake:1}],track:Array.from({length:3},()=>({length_m:10,curvature_1pm:.01}))};
assert.deepEqual(parseSession(JSON.stringify(session)),session);
for(const bad of [
 {...session,schema:'other'}, {...session,provenance:{}},
 {...session,telemetry:[session.telemetry[0],session.telemetry[0]]},
 {...session,track:[{length_m:51,curvature_1pm:0},...session.track]},
 {...session,track:[]},
 {...session,telemetry:session.telemetry.map(r=>({...r,brake:100}))}
])assert.throws(()=>parseSession(JSON.stringify(bad)));
console.log('PASS independent import channels, stale-request rejection and complete FastF1 session validation');
