export const REPO='square1005/ghpr-online-dashboard';
export const FILES={master:'data/processed/ghpr_master_weekly.csv',lifecycle:'data/processed/mm_lifecycle_dataset.csv',structure:'data/processed/mm_structure_lifecycle_dataset.csv',weekly:'data/processed/mm_weekly_change_dataset.csv',cases:'outputs/reports/historical_similarity_report.csv',stats:'outputs/reports/historical_similarity_stats.csv',factors:'outputs/reports/single_factor_decile_analysis.csv',summary:'outputs/reports/ghpr_summary_for_hub.json',diagnostics:'outputs/reports/data_freshness_diagnostics.json',report:'outputs/reports/ghpr_factor_report.md',log:'outputs/reports/update_log.md',velocity:'outputs/reports/mm_velocity_reading_layer.md'};
export const FEATURES=['mm_net_percentile_156w','producer_net_percentile_156w','oi_percentile_156w'];
export const finite=v=>typeof v==='number'&&Number.isFinite(v);
export function csvParse(text){
 const rows=[];let row=[],field='',quoted=false;
 text=text.replace(/^\uFEFF/,'');
 for(let i=0;i<text.length;i++){const c=text[i];if(quoted){if(c==='"'&&text[i+1]==='"'){field+='"';i++;}else if(c==='"')quoted=false;else field+=c;}else if(c==='"'){quoted=true;}else if(c===','){row.push(field);field='';}else if(c==='\n'){row.push(field.replace(/\r$/,''));if(row.some(x=>x!==''))rows.push(row);row=[];field='';}else field+=c;}
 if(quoted)throw new Error('CSV 引號未閉合');if(field||row.length){row.push(field.replace(/\r$/,''));if(row.some(x=>x!==''))rows.push(row);}
 const header=rows.shift();if(!header||new Set(header).size!==header.length)throw new Error('CSV 欄位不完整');
 return rows.map(row=>{if(row.length!==header.length)throw new Error('CSV 欄位數不一致');return Object.fromEntries(header.map((k,i)=>[k,row[i]===''?null:/^-?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$/i.test(row[i])?Number(row[i]):row[i]]));});
}
export function parseBundle(bundle){
 if(bundle.schema_version!==1||!bundle.rawFiles)throw new Error('不支援的資料格式');
 const d={source:bundle.source,raw:bundle.rawFiles};
 for(const [key,path] of Object.entries(FILES)){const raw=bundle.rawFiles[path];if(typeof raw!=='string')throw new Error('缺少研究檔案：'+key);d[key]=path.endsWith('.csv')?csvParse(raw):path.endsWith('.json')?JSON.parse(raw):raw;}
 validateData(d);return d;
}
export function validateData(d){
 if(!d.master.length)throw new Error('主資料集為空');const dates=new Set();let prev='';
 for(const r of d.master){if(typeof r.date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(r.date)||!Number.isFinite(Date.parse(r.date))||dates.has(r.date)||r.date<=prev)throw new Error('主資料日期重複或未排序');dates.add(r.date);prev=r.date;if(!finite(r.gold_close)||r.gold_close<=0)throw new Error('黃金價格缺值或格式不符');if(![r.mm_long,r.mm_short,r.mm_net].every(finite)||Math.abs(r.mm_long-r.mm_short-r.mm_net)>0.001)throw new Error('MM 淨部位不一致');for(const k of [...FEATURES,'swap_net_percentile_156w'])if(r[k]!==null&&(!finite(r[k])||r[k]<0||r[k]>1))throw new Error('分位必須介於 0 與 1');}
 const last=d.master.at(-1);if(d.summary.date!==last.date)throw new Error('摘要與主資料日期不同');
 if(typeof d.summary.last_update_time!=='string'||!Number.isFinite(Date.parse(d.summary.last_update_time))||!Array.isArray(d.diagnostics.components))throw new Error('摘要或診斷格式不完整');
 if(!finite(d.summary.gold_close)||Math.abs(d.summary.gold_close-last.gold_close)>.01)throw new Error('摘要價格不一致');
 for(const [s,k] of [['mm_percentile',FEATURES[0]],['producer_percentile',FEATURES[1]],['oi_percentile',FEATURES[2]]])if(!finite(d.summary[s])||Math.abs(d.summary[s]-last[k]*100)>.001)throw new Error('摘要分位不一致');
 for(const k of ['lifecycle','structure','weekly']){if(d[k].length!==d.master.length||d[k].some((r,i)=>r.date!==d.master[i].date))throw new Error(k+' 與主資料日期不一致');}
 if(!d.cases.length||d.cases.some(r=>r.current_date!==last.date||!dates.has(r.historical_date)))throw new Error('相似案例日期不同');
 if(d.diagnostics.expected_latest_date!==last.date)throw new Error('診斷檔日期不一致');
 for(const r of d.cases){const idx=d.master.findIndex(x=>x.date===r.historical_date);for(const w of [1,2,4,8]){const actual=forward(d.master,idx,w);if(!finite(actual)||!finite(r['future_return_'+w+'w'])||Math.abs(actual-r['future_return_'+w+'w'])>1e-8)throw new Error('相似案例後續報酬不一致');}}
 const expected=similarCases(d.master,20);if(expected.length!==d.cases.length||expected.some(r=>!d.cases.some(c=>r.historical_date===c.historical_date&&Math.abs(r.similarity_score-c.similarity_score)<1e-7)))throw new Error('相似案例與既有三因子定義不同');
 if(d.source?.data_date&&d.source.data_date!==last.date)throw new Error('來源日期不一致');return true;
}
export function forward(rows,i,w){return rows[i+w]&&finite(rows[i+w].gold_close)&&rows[i].gold_close>0?rows[i+w].gold_close/rows[i].gold_close-1:null;}
export function similarCases(rows,n=20){const current=rows.at(-1);return rows.slice(0,Math.max(rows.length-52,0)).map((r,i)=>({r,i})).filter(({r})=>FEATURES.every(k=>finite(r[k])&&finite(current[k]))).map(({r,i})=>({historical_date:r.date,similarity_score:100-FEATURES.reduce((a,k)=>a+Math.abs(r[k]-current[k])*100,0)/3,historical_gold_close:r.gold_close,historical_mm_percentile:r[FEATURES[0]]*100,historical_producer_percentile:r[FEATURES[1]]*100,historical_oi_percentile:r[FEATURES[2]]*100,...Object.fromEntries([1,2,4,8].map(w=>['future_return_'+w+'w',forward(rows,i,w)]))})).sort((a,b)=>b.similarity_score-a.similarity_score||a.historical_date.localeCompare(b.historical_date)).slice(0,n);}
export function quantile(values,q){const a=values.filter(finite).sort((a,b)=>a-b);if(!a.length)return null;const i=(a.length-1)*q,l=Math.floor(i);return a[l]+(a[Math.ceil(i)]-a[l])*(i-l);}
export function stats(cases,w){const a=cases.map(r=>r['future_return_'+w+'w']).filter(finite);return {n:a.length,median:quantile(a,.5),q1:quantile(a,.25),q3:quantile(a,.75),mean:a.length?a.reduce((s,v)=>s+v,0)/a.length:null,win:a.length?a.filter(v=>v>0).length/a.length:null,best:a.length?Math.max(...a):null,worst:a.length?Math.min(...a):null};}
export function ageDays(date,now=new Date()){return Math.floor((Date.UTC(now.getUTCFullYear(),now.getUTCMonth(),now.getUTCDate())-Date.parse(date+'T00:00:00Z'))/86400000);}
export function freshness(date,now=new Date()){const days=ageDays(date,now);return {days,stale:days>10,label:days<0?'日期待核對':days>10?'資料待更新':'官方最新期未核對'};}
export function clusters(cases,w=8){const a=cases.map(r=>r.historical_date).sort();let n=0,end=-Infinity;for(const date of a){const t=Date.parse(date);if(t>end)n++;end=Math.max(end,t+w*7*86400000);}return n;}
export function filterHistory(rows,start,end,search=''){return rows.filter(r=>(!start||r.date>=start)&&(!end||r.date<=end)&&(!search||r.date.includes(search)));}
export function safeCSV(rows,columns){const q=v=>'"'+String(v??'').replaceAll('"','""')+'"';return '\uFEFF'+[columns.map(q).join(','),...rows.map(r=>columns.map(k=>q(typeof r[k]==='string'&&/^[=+@]/.test(r[k])?"'"+r[k]:r[k])).join(','))].join('\r\n');}
