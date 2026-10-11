import assert from 'node:assert/strict';
import {FEATURES,similarCases,similarityRankKey} from './web-validation/core.mjs';
// Actual equal-distance states from the 2026-10-06 cutoff; no provider/network needed.
const current=[.3269230769230769,.9166666666666666,.1282051282051282];
const ties=[['2014-02-11',.21794871794871795,.9166666666666666,.038461538461538464],['2014-04-15',.358974358974359,.8525641025641025,.02564102564102564],['2014-04-29',.391025641025641,.8269230769230769,.08333333333333333],['2021-10-12',.28205128205128205,.9423076923076923,.2564102564102564]];
const row=(date,values)=>({date,gold_close:1500,...Object.fromEntries(FEATURES.map((k,i)=>[k,values[i]]))});
const controls=Array.from({length:19},(_,i)=>row(new Date(Date.UTC(2010,0,5+i*7)).toISOString().slice(0,10),[current[0]+(i+1)*.0001,...current.slice(1)]));
const recent=Array.from({length:52},(_,i)=>row(new Date(Date.UTC(2026,9,6)-(51-i)*7*86400000).toISOString().slice(0,10),current));
const rows=[...controls,...ties.map(([date,...values])=>row(date,values)),...recent];
const all=similarCases(rows,23),top=similarCases(rows,20);
assert.deepEqual(all.slice(19).map(r=>r.historical_date),ties.map(r=>r[0]));
assert.equal(top.at(-1).historical_date,'2014-02-11');
assert.equal(new Set(all.slice(19).map(r=>similarityRankKey(r.similarity_score))).size,1);
assert.equal(similarityRankKey(2.5/1e10),3);
assert.notEqual(similarityRankKey(93.376068),similarityRankKey(93.376069));
for(const c of all){const raw=rows.find(r=>r.date===c.historical_date);assert.equal(c.similarity_score,100-FEATURES.reduce((sum,k)=>sum+Math.abs(raw[k]-recent.at(-1)[k])*100,0)/3);}
console.log('PASS: stable actual ties, Top20 cutoff, recent exclusion, half-up key, distinct scores and raw score preservation');