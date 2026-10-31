export async function loadRace(){
 const url=new URL('./bahrain-2024-race.json',import.meta.url);
 const response=await fetch(url);if(!response.ok)throw Error('Dados reais indisponíveis. Nenhum dado sintético será gerado.');
 const d=await response.json();if(d.origin!=='observed'||d.session?.session_key!==9472||!d.laps?.length)throw Error('Fonte de dados inválida');return d;
}
export function fail(error){const root=document.querySelector('#demo,#replay');if(root){root.dataset.error='true';root.innerHTML='<p role="alert">Não foi possível carregar a sessão real. Recarregue a página. Nenhum dado sintético foi utilizado.</p>'}console.error(error)}
export const seconds=date=>Date.parse(date)/1000;
export function nearestBefore(rows,t,key='date'){let lo=0,hi=rows.length-1;while(lo<hi){const mid=Math.ceil((lo+hi)/2);if(seconds(rows[mid][key])<=t)lo=mid;else hi=mid-1}return rows[lo]}
