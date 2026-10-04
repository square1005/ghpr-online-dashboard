import fs from 'node:fs';import {verifyRelease} from './web-validation/release-client.mjs';
const manifest=JSON.parse(fs.readFileSync('web-data/manifest.json','utf8'));
const texts=Object.fromEntries(Object.entries(manifest.files).map(([k,v])=>[k,fs.readFileSync('web-data/'+v.path,'utf8')]));
const result=await verifyRelease(manifest,texts);
console.log(JSON.stringify({status:'PASS',master_rows:result.D.master.length,as_of:result.D.summary.date,outcome_rows:result.outcomes.rows.length,generation_id:manifest.generation_id}));
