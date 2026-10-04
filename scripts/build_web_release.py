#!/usr/bin/env python3
"""Build the public GHPR release only from a completely validated engine generation."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,subprocess,os
from datetime import datetime,timezone
from pathlib import Path

FILES=['data/processed/ghpr_master_weekly.csv','data/processed/mm_lifecycle_dataset.csv','data/processed/mm_structure_lifecycle_dataset.csv','data/processed/mm_weekly_change_dataset.csv','outputs/reports/historical_similarity_report.csv','outputs/reports/historical_similarity_stats.csv','outputs/reports/single_factor_decile_analysis.csv','outputs/reports/ghpr_summary_for_hub.json','outputs/reports/data_freshness_diagnostics.json','outputs/reports/ghpr_factor_report.md','outputs/reports/update_log.md','outputs/reports/mm_velocity_reading_layer.md']
def encode(value): return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
def sha(data): return hashlib.sha256(data).hexdigest()
def build(root,outcomes_path,output,status_path=None):
    now=datetime.now(timezone.utc).isoformat()
    raw={p:(root/p).read_text(encoding='utf-8-sig') for p in FILES}
    raw['outputs/reports/update_log.md']=raw['outputs/reports/update_log.md'].replace(str(root),'PROJECT_ROOT')
    rows=list(csv.DictReader(io.StringIO(raw[FILES[0]])))
    summary=json.loads(raw[FILES[7]]); diagnostics=json.loads(raw[FILES[8]])
    if not rows or summary['date']!=rows[-1]['date'] or diagnostics['expected_latest_date']!=rows[-1]['date']: raise ValueError('MIXED_GENERATION')
    for path in FILES[1:4]:
        other=list(csv.DictReader(io.StringIO(raw[path])))
        if [r['date'] for r in other]!=[r['date'] for r in rows]: raise ValueError('MISALIGNED_WEEKLY_FILES')
    outcomes=json.loads(outcomes_path.read_text(encoding='utf-8'))
    if outcomes.get('price_feed') not in ('Yahoo Finance GC=F','GC=F'): raise ValueError('WRONG_PRICE_FEED')
    cot_dates={r['date'] for r in rows}
    if any(r['cot_date'] not in cot_dates for r in outcomes['rows']): raise ValueError('OUTCOME_COT_NOT_IN_MASTER')
    if outcomes.get('scope',{}).get('coverage_scope')=='ALL_MASTER' and [r['cot_date'] for r in outcomes['rows']] != [r['date'] for r in rows]: raise ValueError('ALL_HISTORY_OUTCOME_COVERAGE_MISMATCH')
    source_status={}
    for candidate in [root/'outputs/reports/source_status.json',root/'data/raw/source_status.json',root/'data/source_status.json']:
        if candidate.exists(): source_status=json.loads(candidate.read_text(encoding='utf-8'));break
    status=json.loads(status_path.read_text(encoding='utf-8')) if status_path and status_path.exists() else {'schema':'ghpr.update-status.v1','status':'DATA_PREPARED','last_data_success_at':summary['last_update_time'],'last_error':None,'schedule':'Every Sunday 08:00 Asia/Taipei (00:00 UTC)','host_dependency':'Windows host powered on, Administrator signed in, network and existing GitHub credential available'}
    code_sha=os.environ.get('GHPR_SOURCE_COMMIT') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    bundle={'schema_version':1,'source':{'repository':'square1005/ghpr-online-dashboard','commit':code_sha,'code_commit':code_sha,'mode':'published','data_date':rows[-1]['date'],'generated_at':now,'sha256':{p:sha(v.encode()) for p,v in raw.items()},'price_source':'Yahoo Finance GC=F','source_status':source_status},'rawFiles':raw}
    # Generation key describes data, not wall-clock metadata or publication status.
    stable_keys=('cot_date','week_start','week_end','open','high','low','close','change','change_pct','range','range_pct','high_date','low_date','high_weekday','low_weekday','high_time_utc','low_time_utc','high_time_range_taipei','low_time_range_taipei','high_time_precision','low_time_precision','high_time_reason','low_time_reason','hourly_unavailable_reason','missing_session_dates','unexpected_session_dates','revision_publication_dates','revision_release_at_utc','release_mapping_inferred','release_evidence_note','observed_hourly_bars','expected_hourly_bars','research_window_mode','research_availability_status','not_ex_ante_available','no_lookahead_eligible','original_scheduled_release_date','revised_publication_date','scheduled_release_date','planned_release_window_start','planned_release_window_end','actual_publication_date','scheduled_release_relation','release_evidence_kind','release_evidence_sources','publication_delayed','actual_cot_release_at_utc','actual_cot_release_source_url','revision_risk','point_in_time_vintage_unverified','revision_note','coverage_status','observed_sessions','expected_sessions','hourly_coverage_status','extreme_order','high_tie_count','low_tie_count','bars')
    stable_outcomes={'price_feed':outcomes['price_feed'],'coverage_scope':outcomes.get('scope',{}).get('coverage_scope'),'rows':[{key:row.get(key) for key in stable_keys} for row in outcomes['rows']]}
    generation=sha(encode({'master':raw[FILES[0]],'outcomes':stable_outcomes}))[:24]
    bundle['source']['generation_id']=generation
    outcomes['generation_id']=generation
    assets={'bundle.json':encode(bundle),'next-week-outcomes.json':encode(outcomes),'update-status.json':encode(status)}
    manifest={'schema':'ghpr.release.v1','generation_id':generation,'generated_at':now,'as_of':rows[-1]['date'],'price_feed':'Yahoo Finance GC=F','source_status':source_status,'files':{key:{'path':path,'sha256':sha(assets[path])} for key,path in [('bundle','bundle.json'),('outcomes','next-week-outcomes.json'),('status','update-status.json')]},'release_time_note':'CFTC actual publication timestamps remain null unless directly evidenced; observation date is separate from this GHPR build time.'}
    output.mkdir(parents=True,exist_ok=True)
    for name,data in assets.items():
        temp=output/(name+'.tmp');temp.write_bytes(data);temp.replace(output/name)
    temp=output/'manifest.json.tmp';temp.write_bytes(encode(manifest));temp.replace(output/'manifest.json')
    return {'status':'PASS','generation_id':generation,'cot_as_of':rows[-1]['date'],'master_rows':len(rows),'outcome_rows':len(outcomes['rows']),'output':str(output)}
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--outcomes',type=Path);p.add_argument('--output',type=Path);p.add_argument('--status',type=Path);a=p.parse_args()
    print(json.dumps(build(a.root,a.outcomes or a.root/'data/processed/ghpr_next_week_outcomes.json',a.output or a.root/'web-data',a.status or a.root/'outputs/reports/auto_update_status.json'),ensure_ascii=False))
if __name__=='__main__':main()
