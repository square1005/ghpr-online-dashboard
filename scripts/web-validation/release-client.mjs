
import {parseBundle,REPO} from './core.mjs';
export const digest=async text=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))].map(v=>v.toString(16).padStart(2,'0')).join('');
export function validateOutcomes(value,master){
 if(value.schema_version!==1||!['GC=F','Yahoo Finance GC=F'].includes(value.price_feed)||!Array.isArray(value.rows))throw Error('次週行情來源或格式不符');
 const dates=new Set(master.map(r=>r.date));let prior='';
 if(value.scope?.coverage_scope==='ALL_MASTER'&&(value.rows.length!==master.length||value.rows.some((r,i)=>r.cot_date!==master[i].date)))throw Error('全歷史行情未完整對齊母表');
 for(const row of value.rows){
  if(!dates.has(row.cot_date)||row.cot_date<=prior)throw Error('次週行情與持倉日期不一致');prior=row.cot_date;
  const d=new Date(row.cot_date+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+((8-d.getUTCDay())%7||7));
  if(row.week_start!==d.toISOString().slice(0,10))throw Error('次週對應日期錯誤');
  if(row.coverage_status==='PENDING'){
   if(['open','high','low','close'].some(k=>row[k]!=null))throw Error('未來週不能含已完成行情');
  }else if(row.coverage_status==='COMPLETE_DAILY'){
   if(!['open','high','low','close'].every(k=>Number.isFinite(row[k])&&row[k]>0)||row.high<Math.max(row.open,row.close,row.low)||row.low>Math.min(row.open,row.close))throw Error('週行情值不符');
   if(Math.abs(row.change_pct-(row.close/row.open-1))>1e-8||Math.abs(row.range_pct-(row.high-row.low)/row.open)>1e-8)throw Error('週行情比率不符');
  }
  if(row.no_lookahead_eligible===true&&!((row.actual_cot_release_source_url&&Number.isFinite(Date.parse(row.actual_cot_release_at_utc))&&Date.parse(row.actual_cot_release_at_utc)<=Date.parse(row.window_start_utc))||(row.research_availability_status==='ACTUAL_PUBLICATION_DATE_BEFORE_WEEK_START'&&row.actual_publication_date&&row.release_evidence_sources?.length)))throw Error('研究資格缺少實際發布證據');
  if(row.not_ex_ante_available===true&&row.no_lookahead_eligible!==false)throw Error('延遲发布研究資格不一致');
  if(row.revision_risk===true&&row.no_lookahead_eligible===true)throw Error('歷史修訂版本尚未核實');
  if(row.coverage_status==='PENDING'&&['change','change_pct','range','range_pct','high_date','low_date','high_time_utc','low_time_utc'].some(k=>row[k]!=null))throw Error('未來週不得含結果');
  for(const side of ['high','low'])if(row[side+'_time_range_taipei']&&row[side+'_time_precision']==='day')throw Error('日K不能宣稱小時精度');
 }
 return value;
}
export async function verifyRelease(manifest,texts){
 if(manifest.schema!=='ghpr.release.v1'||manifest.price_feed!=='Yahoo Finance GC=F')throw Error('發布資料格式不符');
 for(const key of ['bundle','outcomes','status']){
  if(!manifest.files?.[key]||!/^[a-f0-9]{64}$/.test(manifest.files[key].sha256)||await digest(texts[key])!==manifest.files[key].sha256)throw Error('發布檔案校驗失敗：'+key);
 }
 const bundle=JSON.parse(texts.bundle),D=parseBundle(bundle),outcomes=validateOutcomes(JSON.parse(texts.outcomes),D.master),status=JSON.parse(texts.status);
 if(manifest.as_of!==D.summary.date||manifest.generation_id!==bundle.source.generation_id||manifest.generation_id!==outcomes.generation_id)throw Error('發布資料不屬於同一批');
 return {manifest,bundle,D,outcomes,status};
}
async function fetchText(url,fetcher){
 const r=await fetcher(url,{cache:'no-store',signal:AbortSignal.timeout(25000)});
 if(!r.ok)throw Error('GHPR 發布來源無法讀取（'+r.status+'）');return r.text();
}
export async function fetchPublishedRelease(fetcher=fetch){
 const info=JSON.parse(await fetchText('https://api.github.com/repos/'+REPO+'/commits/main',fetcher));
 if(!/^[a-f0-9]{40}$/.test(info.sha))throw Error('GitHub 版本無法辨識');
 const base='https://raw.githubusercontent.com/'+REPO+'/'+info.sha+'/web-data/';
 const manifest=JSON.parse(await fetchText(base+'manifest.json',fetcher)),texts={};
 await Promise.all(['bundle','outcomes','status'].map(async key=>{
  const path=manifest.files?.[key]?.path;
  if(!path||!['bundle.json','next-week-outcomes.json','update-status.json'].includes(path))throw Error('發布檔案路徑不符');
  texts[key]=await fetchText(base+path,fetcher);
 }));
 const next=await verifyRelease(manifest,texts);
 next.published_commit=info.sha;next.published_commit_at=info.commit?.committer?.date??null;
 next.D.source.commit=info.sha;next.D.source.mode='synced';
 return next;
}
export async function loadBundledRelease(fetcher=fetch){
 const manifest=JSON.parse(await fetchText('update-manifest.json',fetcher));
 const paths={bundle:'data.json',outcomes:'next-week-outcomes.json',status:'update-status.json'},texts={};
 await Promise.all(Object.entries(paths).map(async([k,p])=>texts[k]=await fetchText(p,fetcher)));
 return verifyRelease(manifest,texts);
}
