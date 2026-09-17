#!/usr/bin/env python3
"""Run non-browser release checks and preserve subprocess logs. Runtime needs no Node."""
import argparse,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--browser',action='store_true');args=p.parse_args();qa=ROOT/'qa';qa.mkdir(exist_ok=True)
    jobs=[('python-tests',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'],ROOT),('core-tests',['node','tests/test_core.js'],ROOT),('student-scaffold-tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'],ROOT/'examples/cross_language_trade')]
    if args.browser:jobs.append(('browser-tests',[sys.executable,'tests/browser_check.py'],ROOT))
    result=[]
    for name,cmd,cwd in jobs:
        r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);log=r.stdout+'\n'+r.stderr;(qa/(name+'.log')).write_text(log,encoding='utf-8')
        m=re.search(r'(?:Ran|TOTAL)\s+(\d+)',log);result.append({'suite':name,'passed':r.returncode==0,'cases':int(m[1]) if m else None});print(name,'PASS' if not r.returncode else 'FAIL')
        if r.returncode:sys.exit(r.returncode)
    (qa/'latest-check.json').write_text(json.dumps(result,indent=2));print('All requested suites passed.')
if __name__=='__main__':main()
