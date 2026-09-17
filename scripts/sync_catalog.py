#!/usr/bin/env python3
"""Refresh public metadata without executing source code or replacing learning annotations."""
from pathlib import Path
import argparse,json,datetime,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from upstream import request_json
ROOT=Path(__file__).resolve().parents[1]
def fetch_all(fetch=request_json):
    rows=[]
    for page in range(1,101):
        result=fetch(f'https://api.github.com/users/YucongDuan/repos?type=owner&per_page=100&page={page}')
        if not isinstance(result,list):raise ValueError('Unexpected GitHub response; catalogue not changed')
        rows.extend(result)
        if len(result)<100:return rows
    raise ValueError('Pagination limit reached; refusing a partial update')

def merge_catalog(catalog,rows):
    known={r['name']:dict(r) for r in catalog['repositories']};present=set()
    for meta in rows:
        if meta.get('private') or (meta.get('owner') or {}).get('login','').lower()!='yucongduan':continue
        name=meta.get('name','')
        if not name or meta.get('html_url')!='https://github.com/YucongDuan/'+name:raise ValueError('Repository identity mismatch')
        present.add(name)
        if name not in known:
            known[name]={'id':'GH'+str(meta['id']),'name':name,'area':'foundations','tags':[],'featured':False,'difficulty':3,'role':'','explore':'','work':'','verification':'metadata-only','source':meta['html_url'],'readme_check':None}
        known[name].update({'url':meta['html_url'],'description':meta.get('description') or known[name].get('description',''),'license':(meta.get('license') or {}).get('spdx_id'),'archived':bool(meta.get('archived')),'default_branch':meta.get('default_branch'),'present_in_latest_sync':True,'latest_pushed_at':meta.get('pushed_at')})
    for name,r in known.items():
        if name not in present:r['present_in_latest_sync']=False
    return {**catalog,'last_sync':datetime.datetime.now(datetime.timezone.utc).isoformat(),'live_public_count':len(present),'repositories':list(known.values())}

def main():
    p=argparse.ArgumentParser();p.add_argument('--from-json',help='Offline API metadata array');a=p.parse_args()
    rows=json.loads(Path(a.from_json).read_text(encoding='utf-8')) if a.from_json else fetch_all()
    path=ROOT/'data/catalog.json';old=json.loads(path.read_text(encoding='utf-8'));new=merge_catalog(old,rows)
    path.with_suffix('.previous.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(path)
    from build_web import build
    build();print('Metadata updated:',new['live_public_count'],'public repositories; new entries await pedagogical tagging.')
if __name__=='__main__':main()
