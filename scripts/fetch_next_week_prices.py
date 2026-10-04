"""Capture and normalize public Yahoo GC=F daily/hourly prices. No COT outcomes or publishing.

python -B fetch_prices.py --start 2026-07-01 --end-exclusive 2026-10-04 --output-dir D:/.../prices
python -B fetch_prices.py --from-capture --output-dir D:/.../prices
Use a new output directory per automated run to retain response history.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
SYMBOL = 'GC=F'
TZ_NAME = 'America/New_York'
CME_SPEC = 'https://www.cmegroup.com/market-regulation/files/gold-futures-and-options-fact-card.pdf'
CME_HOURS = 'https://www.cmegroup.com/trading-hours.html'
CME_LABOR = 'https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/labor-day-holiday-settlement-times-2026.pdf'
DEFAULT_CALENDAR_PATH = Path(__file__).resolve().parents[1] / 'config' / 'gc_price_calendar.json'
def load_source_calendar(path:Path|None=None):
 calendar_path=path or DEFAULT_CALENDAR_PATH
 calendar=json.loads(calendar_path.read_text(encoding='utf-8-sig'))
 if calendar.get('symbol')!=SYMBOL or calendar.get('exchange_timezone')!=TZ_NAME:raise ValueError('Calendar source identity mismatch')
 return calendar


def write_json(path:Path,value):
 path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8'))

def set_process_temp(output_dir:Path):
 output_dir.mkdir(parents=True,exist_ok=True)
 tmp=output_dir/'tmp';tmp.mkdir(exist_ok=True)
 os.environ['TMP']=str(tmp);os.environ['TEMP']=str(tmp);os.environ['PYTHONDONTWRITEBYTECODE']='1'

def fetch_chart(start:dt.date,end_exclusive:dt.date,interval:str,output_dir:Path,timeout:int=60):
 if interval not in ('1d','1h'):raise ValueError('Only GC=F daily and one-hour capture is supported')
 if end_exclusive<=start:raise ValueError('end-exclusive must follow start')
 start_utc=dt.datetime.combine(start,dt.time(),UTC);end_utc=dt.datetime.combine(end_exclusive,dt.time(),UTC)
 url=f'https://query1.finance.yahoo.com/v8/finance/chart/GC%3DF?period1={int(start_utc.timestamp())}&period2={int(end_utc.timestamp())}&interval={interval}&events=history'
 record={'source':'Yahoo Finance chart','symbol':SYMBOL,'interval':interval,'url':url,'requested_start_utc':start_utc.isoformat(),'requested_end_exclusive_utc':end_utc.isoformat(),'fetched_at_utc':dt.datetime.now(UTC).isoformat()}
 request=Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
 try:
  with urlopen(request,timeout=timeout) as response:
   raw=response.read();status=response.status
   headers={k:v for k,v in response.headers.items() if k.lower() in ('date','content-type','cache-control','age','last-modified')}
 except HTTPError as error:
  status=error.code;raw=error.read();headers={}
 except Exception as error:
  record['network_error']=f'{type(error).__name__}: {error}'
  write_json(output_dir/f'yahoo_gc_f_{interval}_fetch.json',record);raise
 path=output_dir/f'yahoo_gc_f_{interval}_raw.json';path.write_bytes(raw)
 record.update({'http_status':status,'response_headers':headers,'raw_file':path.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 try:
  payload=json.loads(raw);record['chart_error']=payload.get('chart',{}).get('error')
 except Exception as error:
  record['parse_error']=f'{type(error).__name__}: {error}'
 write_json(output_dir/f'yahoo_gc_f_{interval}_fetch.json',record)
 if status!=200 or record.get('chart_error') or record.get('parse_error'):raise RuntimeError(f'Yahoo {interval} capture failed; see saved fetch metadata')
 return record

def is_regular_hour(local:dt.datetime)->bool:
 wd=local.weekday();h=local.hour
 return (wd==6 and h>=18) or (wd in (0,1,2,3) and h!=17) or (wd==4 and h<17)

def normalize_interval(output_dir:Path,interval:str,calendar:dict|None=None):
 calendar=calendar if calendar is not None else load_source_calendar()
 raw_path=output_dir/f'yahoo_gc_f_{interval}_raw.json';raw=raw_path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
 fetch=json.loads((output_dir/f'yahoo_gc_f_{interval}_fetch.json').read_text(encoding='utf-8'))
 payload=json.loads(raw)
 if fetch.get('http_status')!=200 or payload.get('chart',{}).get('error') is not None:raise ValueError('Unsuccessful source response')
 if sha!=fetch['sha256']:raise ValueError('Raw response hash does not match fetch metadata')
 result=payload['chart']['result'][0];meta=result['meta'];q=result['indicators']['quote'][0];stamps=result.get('timestamp') or []
 if meta.get('symbol')!=SYMBOL or meta.get('instrumentType')!='FUTURE' or meta.get('dataGranularity')!=interval:raise ValueError('Unexpected feed identity or interval')
 if meta.get('exchangeTimezoneName')!=TZ_NAME:raise ValueError('Unexpected exchange timezone; calendar mapping must be reviewed')
 if len(stamps)!=len(set(stamps)) or stamps!=sorted(stamps):raise ValueError('Duplicate or unordered source timestamps')
 tz=ZoneInfo(TZ_NAME);rows=[];rejected=[]
 requested_start=dt.datetime.fromisoformat(fetch['requested_start_utc']).timestamp();requested_end=dt.datetime.fromisoformat(fetch['requested_end_exclusive_utc']).timestamp()
 next_minute={};next_stamp=None
 for candidate_stamp in reversed(stamps):
  next_minute[candidate_stamp]=next_stamp
  if candidate_stamp%60==0 and requested_start<=candidate_stamp<requested_end:next_stamp=candidate_stamp
 for i,stamp in enumerate(stamps):
  utc=dt.datetime.fromtimestamp(stamp,UTC);local=utc.astimezone(tz)
  values={k:q[k][i] for k in ('open','high','low','close','volume')}
  raw_row={'raw_index':i,'source_timestamp_utc':utc.isoformat(),'source_timestamp_exchange':local.isoformat(),**values}
  reason=None
  if not requested_start<=stamp<requested_end:reason='outside_requested_capture_window'
  elif any(values[k] is None or not math.isfinite(values[k]) or values[k]<=0 for k in ('open','high','low','close')):reason='missing_ohlc_chart_slot'
  elif interval=='1h' and stamp%60:reason='non_minute_quote_snapshot'
  elif interval=='1h' and not is_regular_hour(local):reason='outside_cme_regular_session'
  elif values['high']<max(values['open'],values['close'],values['low']) or values['low']>min(values['open'],values['close'],values['high']):reason='ohlc_bounds_inconsistent'
  if reason:rejected.append({**raw_row,'reason':reason});continue
  shared={**values,'symbol':SYMBOL,'source':'Yahoo Finance chart','source_interval':interval,'exchange_timezone':TZ_NAME,'fetched_at_utc':fetch['fetched_at_utc'],'raw_sha256':sha,'raw_index':i}
  if interval=='1d':
   row={'date':local.date().isoformat(),'source_timestamp_utc':utc.isoformat(),'source_timestamp_exchange':local.isoformat(),**shared}
  else:
   end_stamp=min(stamp+3600,requested_end,next_minute[stamp] if next_minute[stamp] is not None else requested_end);end=dt.datetime.fromtimestamp(end_stamp,UTC);candidate=(local.date()+(dt.timedelta(days=1) if local.hour>=18 else dt.timedelta())).isoformat()
   session_date=calendar.get('trade_date_overrides', {}).get(candidate,candidate)
   row={'bar_start_utc':utc.isoformat(),'bar_end_utc_nominal':end.isoformat(),'bar_start_exchange':local.isoformat(),'bar_end_exchange_nominal':end.astimezone(tz).isoformat(),'calendar_date_exchange':local.date().isoformat(),'session_date_candidate':candidate,'session_date':session_date,'session_date_rule':'NY_1800_rollover_plus_verified_calendar_overrides','bar_duration_seconds_nominal':end_stamp-stamp,'bar_start_minute':local.minute,'bar_end_basis':'min_one_hour_and_next_minute_aligned_source_timestamp','extremum_time_precision':'one_hour_or_shorter_vendor_bucket',**shared}
  rows.append(row)
 if not rows:raise ValueError(f'No usable {interval} rows')
 out=output_dir/f'gc_f_{interval}_normalized.csv'
 with out.open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 write_json(output_dir/f'gc_f_{interval}_normalized.json',rows)
 write_json(output_dir/f'gc_f_{interval}_excluded_rows.json',rejected)
 key='date' if interval=='1d' else 'bar_start_utc'
 summary={'raw_rows':len(stamps),'normalized_rows':len(rows),'excluded_rows':len(rejected),'exclusion_counts':dict(Counter(r['reason'] for r in rejected)),'first':rows[0][key],'last':rows[-1][key],'normalized_file':out.name,'normalized_json_file':f'gc_f_{interval}_normalized.json','normalized_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'raw_sha256':sha,'source_url':fetch['url'],'fetched_at_utc':fetch['fetched_at_utc'],'requested_start_utc':fetch['requested_start_utc'],'requested_end_exclusive_utc':fetch['requested_end_exclusive_utc'],'exchange':meta.get('fullExchangeName'),'exchange_timezone':TZ_NAME,'currency':meta.get('currency'),'instrument_type':meta.get('instrumentType'),'ohlc_bounds_issues':sum(r['reason']=='ohlc_bounds_inconsistent' for r in rejected)}
 if interval=='1h':summary['per_provisional_session_counts']=dict(sorted(Counter(r['session_date_candidate'] for r in rows).items()))
 return summary

def normalize_directory(output_dir:Path,calendar_path:Path|None=None):
 set_process_temp(output_dir)
 calendar=load_source_calendar(calendar_path)
 report={'schema_version':2,'normalization_version':'ghpr-prices-v2','normalized_at_utc':dt.datetime.now(UTC).isoformat(),'symbol':SYMBOL,'source':'Yahoo Finance chart','notes':['No COT outcome table is produced by this script.','Daily OHLC dates are labels, not intraday extreme timestamps.','Hourly timestamps denote one-hour buckets, not exact extreme times.','Hourly regular-session filtering does not establish holiday-specific coverage completeness.','No interpolation or fill or other instruments are used.']}
 for interval in ('1d','1h'):report[interval]=normalize_interval(output_dir,interval,calendar)
 write_json(output_dir/'source_calendar.json',calendar)
 write_json(output_dir/'price_coverage.json',report)
 return report

def fetch_prices(start:dt.date,end_exclusive:dt.date,output_dir:Path,calendar_path:Path|None=None):
 set_process_temp(output_dir)
 for interval in ('1d','1h'):fetch_chart(start,end_exclusive,interval,output_dir)
 return normalize_directory(output_dir,calendar_path)

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--start',type=dt.date.fromisoformat)
 p.add_argument('--end-exclusive',type=dt.date.fromisoformat)
 p.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent)
 p.add_argument('--calendar',type=Path)
 p.add_argument('--from-capture',action='store_true',help='Normalize saved raw JSON with no network requests')
 args=p.parse_args(argv)
 if args.from_capture:result=normalize_directory(args.output_dir.resolve(),args.calendar)
 else:
  if not args.start or not args.end_exclusive:p.error('--start and --end-exclusive are required unless --from-capture')
  result=fetch_prices(args.start,args.end_exclusive,args.output_dir.resolve(),args.calendar)
 print(json.dumps({k:v for k,v in result.items() if k in ('1d','1h')},ensure_ascii=False))
 return 0
if __name__=='__main__':raise SystemExit(main())

