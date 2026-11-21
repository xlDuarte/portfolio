import {telemetry} from './models.mjs';
// Independent imports must not cancel each other. A newer request invalidates only its channel.
export function createLoadGate(){
 const versions=new Map();
 return {begin(channel){const v=(versions.get(channel)||0)+1;versions.set(channel,v);return ()=>versions.get(channel)===v;},invalidate(channel){versions.set(channel,(versions.get(channel)||0)+1);}};
}
export function parseSession(text){
 const session=JSON.parse(text);
 if(session.schema!=='f1-physics-session/v1')throw Error('Formato de sessão incompatível.');
 const meta=session.provenance;
 if(!meta||meta.source!=='FastF1'||!Number.isInteger(meta.year)||typeof meta.event!=='string'||typeof meta.driver!=='string'||!Number.isFinite(meta.observed_laptime_s)||meta.observed_laptime_s<=0)throw Error('Metadados FastF1 incompletos.');
 if(!Array.isArray(session.telemetry)||!Array.isArray(session.track))throw Error('Sessão sem telemetria ou pista.');
 telemetry(session.telemetry);
 if(session.track.length<3||session.track.length>10000||session.track.some(r=>!Number.isFinite(r.length_m)||r.length_m<=0||r.length_m>50||!Number.isFinite(r.curvature_1pm)))throw Error('Geometria inválida: use 3–10.000 segmentos de até 50 m.');
 return session;
}
