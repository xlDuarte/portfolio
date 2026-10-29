import {strategy} from '../lab/engine.mjs';
export {strategy};
export const compounds=[{code:'S',name:'Macio',color:'#d94650',p:[-.65,.085,.0028]},{code:'M',name:'Médio',color:'#bc8900',p:[0,.048,.0014]},{code:'H',name:'Duro',color:'#72828d',p:[.45,.026,.0007]}];
export function detail(row,laps,loss){
 const codes=row.stops.length===1?[0,2]:[0,1,0],ends=[...row.stops,laps];let start=1,total=0;const points=[],stints=[];
 ends.forEach((end,i)=>{const c=compounds[codes[i]];stints.push({start,end,...c});for(let lap=start;lap<=end;lap++){const age=lap-start,pace=81.2+c.p[0]+(58-lap)*.035+c.p[1]*age+c.p[2]*age*age,pit=row.stops.includes(lap)?loss:0;total+=pace+pit;points.push({lap,pace,pit,total,compound:c.code})}start=end+1});return {row,stints,points,total};
}
export function calculate(laps,loss){if(!Number.isInteger(laps)||laps<20||laps>78||!Number.isFinite(loss)||loss<10||loss>40)throw Error('Parâmetros fora dos limites');const rows=strategy(laps,loss);return {rows,best:rows[0],one:rows.find(r=>r.stops.length===1),two:rows.find(r=>r.stops.length===2)}}
