import {replay,point} from '../lab/engine.mjs';
export const DURATION=900;
export const DRIVERS=[{id:'DRV-A',color:'#007f8b',rgb:[0,127,139],label:'Configuração A'},{id:'DRV-B',color:'#b36b18',rgb:[179,107,24],label:'Configuração B'},{id:'DRV-C',color:'#7555af',rgb:[117,85,175],label:'Configuração C'}];
export const clampTime=t=>Math.min(DURATION,Math.max(0,Number(t)||0));
export function sample(t,grip=1){return replay(clampTime(t),grip)}
export function acceleration(t,grip,id){const lo=Math.max(0,t-.25),hi=Math.min(DURATION,t+.25);return (sample(hi,grip).find(c=>c.driver===id).speed-sample(lo,grip).find(c=>c.driver===id).speed)/3.6/(hi-lo||1)}
export function series(grip=1){return DRIVERS.map(d=>({id:d.id,values:Array.from({length:1801},(_,i)=>{const t=i*.5,c=sample(t,grip).find(c=>c.driver===d.id);return [t,c.speed,acceleration(t,grip,d.id)]})}))}
export function trail(t,grip,id){return Array.from({length:41},(_,i)=>{const c=sample(Math.max(0,t-4+i*.1),grip).find(c=>c.driver===id);return [c.x,c.y,2]})}
export const track=Array.from({length:801},(_,i)=>{const p=point(i/800);return [p.x,p.y,0]});
export function snapshot(t,grip,driver){const cars=sample(t,grip),selected=cars.find(c=>c.driver===driver);return {project:'109',data_origin:'synthetic',time:clampTime(t),grip,selected_driver:driver,cars,selected:{...selected,acceleration:acceleration(t,grip,driver)},limitations:'Synthetic harmonic geometry. Position advance and displayed speed are independent simplified models. Gap approximates distance difference / 60.5 m/s; acceleration is the derivative of the synthetic speed signal.'}}
