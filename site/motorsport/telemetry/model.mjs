import {ekf} from '../lab/engine.mjs';
export const DT=.02,COUNT=200;
const rms=a=>Math.sqrt(a.reduce((s,v)=>s+v*v,0)/a.length);
export function session(noise=.25,q=.0001){
 if(!Number.isFinite(noise)||noise<0||noise>3||!Number.isFinite(q)||q<.000001-1e-15||q>.001+1e-15)throw new RangeError('Parâmetros fora dos limites');
 const raw=ekf(noise,q),points=raw.truth.map((truth,i)=>({index:i,time:i*DT,truth,measured:raw.measured[i],estimated:raw.estimated[i],sensorError:raw.measured[i]-truth,error:raw.estimated[i]-truth}));
 const sensorRmse=rms(points.map(p=>p.sensorError));return {noise,q,dt:DT,count:COUNT,seed:102,points,metrics:{rmse:raw.rmse,sensorRmse,mae:points.reduce((s,p)=>s+Math.abs(p.error),0)/COUNT,maxError:Math.max(...points.map(p=>Math.abs(p.error))),reduction:sensorRmse>1e-12?(1-raw.rmse/sensorRmse)*100:null}};
}
export function histogram(points,bins=16){const all=points.flatMap(p=>[p.error,p.sensorError]),limit=Math.max(.001,...all.map(Math.abs))*1.001,width=2*limit/bins,counts=[Array(bins).fill(0),Array(bins).fill(0)];points.forEach(p=>[p.sensorError,p.error].forEach((v,i)=>counts[i][Math.min(bins-1,Math.max(0,Math.floor((v+limit)/width)))]++));return {centers:Array.from({length:bins},(_,i)=>-limit+(i+.5)*width),width,sensor:counts[0],filter:counts[1]};}
