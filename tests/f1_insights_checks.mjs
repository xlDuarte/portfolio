import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {corner,validateLap,observedLap,standingsScenario,trackCSV,optimizeTrack,latest} from '../site/motorsport/insights/core.mjs';
const root=new URL('../site/motorsport/insights/',import.meta.url),json=async path=>JSON.parse(await readFile(new URL(path,root),'utf8'));
const a=[0,1,2,3].map(i=>({time_s:i,distance_m:i*10,speed_kmh:36})),b=a.map(r=>({...r,time_s:r.time_s*2,speed_kmh:18}));
assert.equal(corner(a,b,5,25).delta_s,2);assert.equal(corner(a,b,5,25).min_b,18);assert.throws(()=>corner(a,b,-1,25));assert.throws(()=>validateLap([...a,a.at(-1)]));
const standings=[{Driver:{driverId:'a',givenName:'A',familyName:'A'},points:'100'},{Driver:{driverId:'b',givenName:'B',familyName:'B'},points:'90'}],results=[{Driver:{driverId:'a'},points:'25'},{Driver:{driverId:'b'},points:'18'}];
assert.equal(standingsScenario(standings,results,{} )[0].points,100);assert.equal(standingsScenario(standings,results,{a:15})[1].rank,1);assert.equal(standingsScenario(standings,results,{a:0})[0].driver,'b');assert.throws(()=>standingsScenario(standings,results,{a:NaN}));
const track=trackCSV(await readFile(new URL('data/silverstone.csv',root),'utf8'));const opt=optimizeTrack(track,1.2,30);assert(opt.objective<=opt.baseline);assert(opt.objective>0);opt.path.forEach((p,i)=>assert(p.offset_m>=-track[i].right+1.2-1e-9&&p.offset_m<=track[i].left-1.2+1e-9));assert.throws(()=>optimizeTrack(track,100));
const race=await json('../data/bahrain-2024-race.json');for(const driver of ['1','11']){const lap=observedLap(race,driver);assert(lap.rows.length>200);assert(lap.rows.at(-1).distance_m>4000);}
const official=await json('data/2024-standings.json'),round=await json('data/2024-round1.json');const s=official.MRData.StandingsTable.StandingsLists[0].DriverStandings;const restored=standingsScenario(s,round.MRData.RaceTable.Races[0].Results,{});for(const r of restored)assert.equal(r.points,Number(s.find(d=>d.Driver.driverId===r.driver).points));
assert.equal(latest([{driver_number:1,date:'2024-01-02',position:2},{driver_number:1,date:'2024-01-01',position:1}])[0].position,2);
console.log(`Passed: corner interpolation, domain validation, real laps, championship invariance/ties, latest timestamps, ${track.length} TUM track constraints; curvature improvement ${(100*(1-opt.objective/opt.baseline)).toFixed(2)}%.`);
