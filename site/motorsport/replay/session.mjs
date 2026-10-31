import {loadRace,fail,seconds,nearestBefore} from '../data/load.mjs';
export const race=await loadRace().catch(e=>{fail(e);throw e});
const start=seconds(race.replay_window.start);
export const DURATION=seconds(race.replay_window.end)-start;
export const DRIVERS=race.replay_window.drivers.map(n=>{const d=race.drivers.find(d=>d.driver_number===n),color='#'+d.team_colour;return {id:d.name_acronym,number:n,color,rgb:[1,3,5].map(i=>parseInt(color.slice(i,i+2),16)),label:d.full_name+' / '+d.team_name}});
const positions=Object.values(race.location).flat(),xs=positions.map(p=>p.x),ys=positions.map(p=>p.y),cx=(Math.min(...xs)+Math.max(...xs))/2,cy=(Math.min(...ys)+Math.max(...ys))/2,scale=Math.min(1050/(Math.max(...xs)-Math.min(...xs)),700/(Math.max(...ys)-Math.min(...ys)));
const xy=p=>[(p.x-cx)*scale,(p.y-cy)*scale,0];
export const clampTime=t=>Math.min(DURATION,Math.max(0,Number(t)||0));
export function sample(t){const utc=start+clampTime(t);return DRIVERS.map(d=>{const raw=nearestBefore(race.telemetry[d.number],utc),pos=nearestBefore(race.location[d.number],utc),[x,y]=xy(pos),laps=race.laps.filter(l=>l.driver_number===d.number&&l.date_start&&seconds(l.date_start)<=utc),lap=laps.at(-1),rank=nearestBefore(race.position.filter(p=>p.driver_number===d.number),utc);return {driver:d.id,x,y,speed:raw.speed,gear:raw.n_gear,lap:lap?.lap_number||null,u:lap?.lap_duration?Math.min(1,(utc-seconds(lap.date_start))/lap.lap_duration):0,position:rank?.position,utc:new Date(utc*1000).toISOString(),sample_date:raw.date,stale:utc-seconds(raw.date)>2}}).sort((a,b)=>a.position-b.position)}
export function acceleration(t,grip,id){const d=DRIVERS.find(d=>d.id===id),rows=race.telemetry[d.number],p=nearestBefore(rows,start+clampTime(t)),i=rows.indexOf(p);if(!i)return 0;const prev=rows[i-1],dt=seconds(p.date)-seconds(prev.date);return dt>0?(p.speed-prev.speed)/3.6/dt:0}
export function series(){return DRIVERS.map(d=>({id:d.id,values:race.telemetry[d.number].map(p=>{const t=seconds(p.date)-start;return [t,p.speed,acceleration(t,1,d.id)]})}))}
export function trail(t,grip,id){const d=DRIVERS.find(d=>d.id===id);return race.location[d.number].filter(p=>{const s=seconds(p.date)-start;return s>=t-4&&s<=t}).map(xy)}
// Actual recorded trajectory; no harmonic circuit generation.
export const track=race.location[DRIVERS[0].number].map(xy);
export function snapshot(t,grip,driver){return {project:'109',origin:'observed',provider:race.provider,session:race.session,time:clampTime(t),selected_driver:driver,cars:sample(t),sources:race.sources,limitations:race.limitations,derived_channel:'acceleration = finite difference of observed speed; not an accelerometer measurement'}}
