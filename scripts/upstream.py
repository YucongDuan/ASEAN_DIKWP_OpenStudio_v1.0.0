#!/usr/bin/env python3
"""Pin, fetch and inspect public YucongDuan repositories. Never runs downloaded code.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import argparse,base64,hashlib,io,json,os,re,shutil,stat,tempfile,time,urllib.error,urllib.parse,urllib.request,zipfile
from pathlib import Path,PurePosixPath
MAX_ARCHIVE=64*1024*1024;MAX_EXPANDED=256*1024*1024;MAX_FILES=10000
ALLOWED_HOSTS={'api.github.com','codeload.github.com','github.com','raw.githubusercontent.com'}

def valid_repo(name):
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,160}',name) or name in ('.','..'):raise ValueError('Invalid repository name')
    return name

def valid_sha(sha):
    if not isinstance(sha,str) or not re.fullmatch(r'[0-9a-f]{40}',sha):raise ValueError('A full 40-character commit SHA is required')
    return sha

def check_url(url):
    u=urllib.parse.urlsplit(url)
    if u.scheme!='https' or u.hostname not in ALLOWED_HOSTS or u.username or u.password or u.port not in (None,443):raise ValueError('Only approved public GitHub HTTPS endpoints are supported')
    return u

class RestrictedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        check_url(newurl)
        result=super().redirect_request(req,fp,code,msg,headers,newurl)
        if result is not None and urllib.parse.urlsplit(req.full_url).hostname!=urllib.parse.urlsplit(newurl).hostname:
            result.remove_header('Authorization')
        return result

def request_bytes(url,limit=MAX_ARCHIVE):
    u=check_url(url);headers={'User-Agent':'DIKWP-OpenStudio/1.0','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
    if u.hostname=='api.github.com' and os.environ.get('GITHUB_TOKEN'):headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
    req=urllib.request.Request(url,headers=headers)
    try:
        with urllib.request.build_opener(RestrictedRedirect()).open(req,timeout=30) as response:
            raw=response.read(limit+1)
            if len(raw)>limit:raise ValueError('Download exceeds size limit')
            return raw
    except urllib.error.HTTPError as ex:
        if ex.code in (403,429):raise RuntimeError('GitHub rate or access limit. Retry later or configure a read-only token.') from ex
        raise RuntimeError('GitHub request failed with HTTP '+str(ex.code)) from ex

def request_json(url):return json.loads(request_bytes(url,4*1024*1024))

def load_manifest(path):
    d=json.loads(Path(path).read_text(encoding='utf-8'))
    if d.get('schema')!='openstudio.upstream-lock/1' or not isinstance(d.get('repositories'),list) or len(d['repositories'])>6:raise ValueError('Invalid upstream manifest')
    for r in d['repositories']:
        valid_repo(r['name'])
        if r.get('owner','YucongDuan')!='YucongDuan' or r.get('url')!='https://github.com/YucongDuan/'+r['name']:raise ValueError('Manifest owner/source mismatch')
    return d

def pin_manifest(d,fetch_json=request_json):
    d=json.loads(json.dumps(d));receipts=[]
    for r in d['repositories']:
        name=valid_repo(r['name']);base='https://api.github.com/repos/YucongDuan/'+name
        meta=fetch_json(base)
        if meta.get('full_name','').lower()!=('YucongDuan/'+name).lower():raise ValueError('GitHub repository identity mismatch')
        branch=meta['default_branch'];commit=fetch_json(base+'/commits/'+urllib.parse.quote(branch,safe=''))
        r.update({'owner':'YucongDuan','commit':valid_sha(commit['sha']),'default_branch':branch,'license':(meta.get('license') or {}).get('spdx_id'),'pinned_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'commit-pinned'})
        receipts.append({'name':name,'commit':r['commit'],'source':base,'license_metadata':r['license']})
    d['pin_receipt']=receipts;return d

def safe_extract(raw: bytes,dest: Path):
    """Reject traversal, links, duplicate paths, special files and unreasonable expansion."""
    if len(raw)>MAX_ARCHIVE:raise ValueError('Archive too large')
    dest=Path(dest)
    if dest.exists() or dest.is_symlink():raise ValueError('Destination must not exist')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        info=archive.infolist()
        if not info or len(info)>MAX_FILES:raise ValueError('Invalid archive file count')
        total=sum(i.file_size for i in info)
        if total>MAX_EXPANDED:raise ValueError('Expanded archive too large')
        seen=set();checked=[]
        for i in info:
            name=i.filename
            if '\\' in name or '\x00' in name or ':' in name:raise ValueError('Unsafe archive path')
            p=PurePosixPath(name)
            if p.is_absolute() or any(v in ('..','') for v in p.parts) or not p.parts:raise ValueError('Unsafe archive path')
            canonical=str(p).rstrip('/')
            if canonical in seen:raise ValueError('Duplicate archive path')
            seen.add(canonical)
            mode=(i.external_attr>>16)&0xffff
            if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0,stat.S_IFREG,stat.S_IFDIR)):raise ValueError('Archive links and special files are not supported')
            if i.flag_bits&1:raise ValueError('Encrypted archives are not supported')
            if i.compress_size and i.file_size/i.compress_size>300:raise ValueError('Unreasonable compression ratio')
            checked.append((i,p))
        roots={p.parts[0] for _,p in checked};strip_root=len(roots)==1 and all(len(p.parts)>1 or i.is_dir() for i,p in checked)
        dest.parent.mkdir(parents=True,exist_ok=True)
        temp=Path(tempfile.mkdtemp(prefix='.upstream-',dir=dest.parent))
        files=[]
        try:
            for i,p in checked:
                parts=p.parts[1:] if strip_root else p.parts
                if not parts:continue
                target=temp.joinpath(*parts)
                if not target.resolve().is_relative_to(temp.resolve()):raise ValueError('Archive escaped destination')
                if i.is_dir():target.mkdir(parents=True,exist_ok=True);continue
                target.parent.mkdir(parents=True,exist_ok=True)
                blob=archive.read(i)
                if len(blob)!=i.file_size:raise ValueError('Archive size mismatch')
                target.write_bytes(blob);os.chmod(target,0o644)
                files.append({'path':str(Path(*parts)).replace(os.sep,'/'),'size':len(blob),'sha256':hashlib.sha256(blob).hexdigest()})
            temp.rename(dest)
        except Exception:
            shutil.rmtree(temp,ignore_errors=True);raise
    return files

def fetch_repository(record,destination,fetch_bytes=request_bytes):
    name=valid_repo(record['name']);sha=valid_sha(record.get('commit'))
    if record.get('owner','YucongDuan')!='YucongDuan':raise ValueError('Unsupported owner')
    url=f'https://api.github.com/repos/YucongDuan/{name}/zipball/{sha}'
    raw=fetch_bytes(url);dest=Path(destination)/name;files=safe_extract(raw,dest)
    licenses=[f for f in files if Path(f['path']).name.upper().startswith(('LICENSE','COPYING','NOTICE'))]
    receipt={'schema':'openstudio.upstream-receipt/1','name':name,'url':record['url'],'commit':sha,'download_url':url,'archive_sha256':hashlib.sha256(raw).hexdigest(),'files':files,'license_files':licenses,'executed':False,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    (Path(destination)/(name+'.receipt.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    return receipt

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('pin');p.add_argument('--manifest',required=True)
    p=sub.add_parser('fetch');p.add_argument('--manifest',required=True);p.add_argument('--dest',default='vendor')
    p=sub.add_parser('inspect-local');p.add_argument('--archive',required=True);p.add_argument('--dest',required=True)
    args=parser.parse_args()
    try:
        if args.cmd=='inspect-local':
            path=Path(args.archive)
            if path.stat().st_size>MAX_ARCHIVE:raise ValueError('Archive too large')
            files=safe_extract(path.read_bytes(),Path(args.dest));print(json.dumps({'files':len(files),'executed':False}));return
        d=load_manifest(args.manifest)
        if args.cmd=='pin':
            result=pin_manifest(d);path=Path(args.manifest);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(path);print('Pinned',len(result['repositories']),'repositories. No source code executed.')
        else:
            for r in d['repositories']:
                receipt=fetch_repository(r,args.dest);print(r['name'],receipt['commit'],len(receipt['files']),'files; not executed')
    except (ValueError,RuntimeError,OSError,KeyError,zipfile.BadZipFile) as ex:parser.exit(1,str(ex)+'\n')
if __name__=='__main__':main()
