"""A standard-library WSGI application with private projects and opt-in class sharing.
Use a production WSGI host behind HTTPS for campus deployment; the bundled runner is local.
"""
from __future__ import annotations
import base64, hashlib, hmac, json, mimetypes, os, re, secrets, sqlite3, time
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlsplit, unquote
from typing import Any
ROOT = Path(__file__).resolve().parents[1]
MAX_BODY = 700_000
class APIError(Exception):
    def __init__(self, status: int, message: str): self.status, self.message = status, message

def now() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
def password_hash(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1).hex()
    return salt + ':' + digest

def verify_password(password: str, stored: str) -> bool:
    try: return hmac.compare_digest(password_hash(password, stored.split(':')[0]), stored)
    except (ValueError, TypeError): return False

def clean_text(d: dict, name: str, maximum: int = 20000, required: bool = False) -> str:
    v = d.get(name, '')
    if not isinstance(v, str) or len(v) > maximum or (required and not v.strip()):
        raise APIError(400, f'Invalid {name}')
    return v

def validate_project(d: Any) -> dict:
    if not isinstance(d, dict) or d.get('schema') != 'openstudio.project/1': raise APIError(400, 'Unsupported project schema')
    pid = d.get('id', '')
    if not isinstance(pid,str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,80}', pid): raise APIError(400, 'Invalid project id')
    out = {'id':pid, 'schema':d['schema']}
    for k in ['title','problem','beneficiary','purpose','data','information','knowledge','wisdom','constraints','inherited','changed','hypothesis','evidence','reflection','locale']:
        out[k] = clean_text(d,k,200 if k=='title' else 20000,k=='title')
    repos = d.get('repositories', [])
    if not isinstance(repos,list) or len(repos)>6: raise APIError(400, 'Select at most six repositories')
    out['repositories'] = []
    for r in repos:
        if not isinstance(r,dict) or not isinstance(r.get('name'),str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,160}',r['name']) or r['name'] in ('.','..'): raise APIError(400, 'Invalid repository')
        if r.get('url')!='https://github.com/YucongDuan/'+r['name']: raise APIError(400, 'Repository source mismatch')
        out['repositories'].append({'name':r['name'],'url':r['url'],'license':clean_text(r,'license',100) if r.get('license') is not None else None,'role':clean_text(r,'role',1000),'commit':r.get('commit') if isinstance(r.get('commit'),str) and re.fullmatch('[0-9a-f]{40}',r['commit']) else None})
    runs=d.get('runs',[])
    if not isinstance(runs,list) or len(runs)>100:raise APIError(400,'Too many runs')
    for run in runs:
        if not isinstance(run,dict) or run.get('lab') not in ('alignment','three-no','action','purpose') or not isinstance(run.get('input'),dict) or not isinstance(run.get('output'),dict):raise APIError(400,'Invalid experiment record')
        clean_text(run,'at',80,True);clean_text(run,'engine',40,True)
    if len(json.dumps(runs,allow_nan=False))>300000:raise APIError(400,'Experiment history too large')
    out['runs']=runs;out['updated_at']=now();return out

class ClosingConnection(sqlite3.Connection):
    def __exit__(self,*args):
        try:return super().__exit__(*args)
        finally:self.close()

class Store:
    def __init__(self,path: str | Path):
        self.path = str(path);Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('student','teacher')), created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id), csrf TEXT NOT NULL, expires REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id), version INTEGER NOT NULL, data TEXT NOT NULL, updated TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS revisions(project_id TEXT NOT NULL, version INTEGER NOT NULL, data TEXT NOT NULL, created TEXT NOT NULL, PRIMARY KEY(project_id,version));
            CREATE TABLE IF NOT EXISTS courses(id TEXT PRIMARY KEY,teacher_id INTEGER NOT NULL REFERENCES users(id),name TEXT NOT NULL,brief TEXT NOT NULL,code TEXT UNIQUE NOT NULL,created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS members(course_id TEXT NOT NULL REFERENCES courses(id),user_id INTEGER NOT NULL REFERENCES users(id),PRIMARY KEY(course_id,user_id));
            CREATE TABLE IF NOT EXISTS submissions(id TEXT PRIMARY KEY,course_id TEXT NOT NULL REFERENCES courses(id),user_id INTEGER NOT NULL REFERENCES users(id),project_id TEXT NOT NULL,version INTEGER NOT NULL,snapshot TEXT NOT NULL,feedback TEXT,created TEXT NOT NULL);
            ''')
    def connect(self):
        db=sqlite3.connect(self.path,timeout=15,factory=ClosingConnection);db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON');db.execute('PRAGMA journal_mode=WAL');return db
    def create_user(self,username,password,role='student'):
        if not isinstance(username,str) or not re.fullmatch('[a-zA-Z0-9_-]{3,40}',username): raise APIError(400,'Username: 3–40 letters, numbers, underscores or hyphens')
        if not isinstance(password,str) or not 10<=len(password)<=200:raise APIError(400,'Password: 10–200 characters')
        if role not in ('student','teacher'):raise APIError(400,'Invalid role')
        try:
            with self.connect() as db:
                uid=db.execute('INSERT INTO users(username,password,role,created) VALUES(?,?,?,?)',(username.lower(),password_hash(password),role,now())).lastrowid
            return {'id':uid,'username':username.lower(),'role':role}
        except sqlite3.IntegrityError: raise APIError(409,'Username is unavailable')

class Application:
    def __init__(self, db_path=None, public_origin=None):
        self.store=Store(db_path or os.environ.get('OPENSTUDIO_DB',str(ROOT/'instance/studio.sqlite3')))
        self.public_origin=(public_origin or os.environ.get('OPENSTUDIO_ORIGIN','http://127.0.0.1:8765')).rstrip('/')
        parsed=urlsplit(self.public_origin)
        if parsed.scheme not in ('http','https') or not parsed.netloc or parsed.path:raise ValueError('OPENSTUDIO_ORIGIN must be a URL origin')
        self.host=parsed.netloc;self.secure=parsed.scheme=='https';self.failures={}
        self.registration=os.environ.get('OPENSTUDIO_REGISTRATION','1')=='1'
    def __call__(self,environ,start_response):
        headers=[]
        try:
            if environ.get('HTTP_HOST','')!=self.host:raise APIError(403,'Host not allowed')
            method=environ.get('REQUEST_METHOD','GET');path=environ.get('PATH_INFO','/')
            if method not in ('GET','POST','PUT','DELETE'):raise APIError(405,'Method not allowed')
            if method!='GET':
                origin=environ.get('HTTP_ORIGIN')
                if origin and origin!=self.public_origin:raise APIError(403,'Origin not allowed')
                if environ.get('CONTENT_TYPE','').split(';')[0]!='application/json':raise APIError(415,'Use application/json')
                try:length=int(environ.get('CONTENT_LENGTH') or 0)
                except ValueError:raise APIError(400,'Invalid content length')
                if not 0<=length<=MAX_BODY:raise APIError(413,'Request too large')
                raw=environ['wsgi.input'].read(length)
                try:data=json.loads(raw or b'{}',parse_constant=lambda _:(_ for _ in ()).throw(ValueError()))
                except (ValueError,UnicodeError):raise APIError(400,'Invalid JSON')
                if not isinstance(data,dict):raise APIError(400,'JSON object required')
            else:data={}
            if not path.startswith('/api/'):
                if method!='GET':raise APIError(405,'Method not allowed')
                rel='index.html' if path=='/' else unquote(path).lstrip('/')
                target=(ROOT/'web'/rel).resolve();web=(ROOT/'web').resolve()
                if not target.is_relative_to(web) or not target.is_file() or target.suffix not in ('.html','.js','.css','.svg','.json','.ico'):raise APIError(404,'Not found')
                body=target.read_bytes();ctype=mimetypes.guess_type(str(target))[0] or 'application/octet-stream';status=200
            else:
                session=self.session(environ)
                if method!='GET' and path not in ('/api/login','/api/register'):
                    if not session:raise APIError(401,'Sign in first')
                    if not hmac.compare_digest(environ.get('HTTP_X_CSRF_TOKEN',''),session['csrf']):raise APIError(403,'CSRF token missing or invalid')
                result,status,headers=self.route(method,path,data,session,environ)
                body=json.dumps(result,ensure_ascii=False,allow_nan=False).encode();ctype='application/json'
        except APIError as ex:status=ex.status;body=json.dumps({'error':ex.message},ensure_ascii=False).encode();ctype='application/json'
        except (ValueError,TypeError,KeyError):status=400;body=b'{"error":"Invalid request"}';ctype='application/json'
        except Exception as ex:
            import traceback;traceback.print_exc();status=500;body=b'{"error":"Internal server error"}';ctype='application/json'
        status_names={200:'OK',201:'Created',400:'Bad Request',401:'Unauthorized',403:'Forbidden',404:'Not Found',405:'Method Not Allowed',409:'Conflict',413:'Payload Too Large',415:'Unsupported Media Type',429:'Too Many Requests',500:'Internal Server Error'}
        security=[('Content-Type',ctype+'; charset=utf-8'),('Content-Length',str(len(body))),('X-Content-Type-Options','nosniff'),('X-Frame-Options','DENY'),('Referrer-Policy','no-referrer'),('Cache-Control','no-store'),('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")]
        start_response(f'{status} {status_names[status]}',headers+security);return [body]
    def session(self,env):
        try:
            cookies=SimpleCookie();cookies.load(env.get('HTTP_COOKIE',''));token=cookies['studio_session'].value
        except (KeyError,ValueError):return None
        with self.store.connect() as db:
            row=db.execute('SELECT s.*,u.username,u.role FROM sessions s JOIN users u ON u.id=s.user_id WHERE token_hash=? AND expires>?',(hashlib.sha256(token.encode()).hexdigest(),time.time())).fetchone()
            return dict(row) if row else None
    def cookie(self,token,expire=False):
        return ('Set-Cookie',f'studio_session={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={0 if expire else 43200}'+('; Secure' if self.secure else ''))
    def route(self,m,p,d,s,env):
        if p=='/api/health' and m=='GET':return {'ok':True,'version':'1.0.0','mode':'campus-local'},200,[]
        if p=='/api/session' and m=='GET':return {'user':{'id':s['user_id'],'username':s['username'],'role':s['role']} if s else None,'csrf':s['csrf'] if s else None,'registration':self.registration},200,[]
        if p=='/api/register' and m=='POST':
            if not self.registration:raise APIError(403,'Registration is disabled')
            # Public registration always creates students; client-provided roles are ignored.
            user=self.store.create_user(d.get('username'),d.get('password'),'student');return {'user':user},201,[]
        if p=='/api/login' and m=='POST':
            username=clean_text(d,'username',40,True).lower();password=clean_text(d,'password',200,True)
            key=(env.get('REMOTE_ADDR','local'),username);fails=[t for t in self.failures.get(key,[]) if time.time()-t<120]
            if len(fails)>=8:raise APIError(429,'Too many attempts. Try again later.')
            with self.store.connect() as db:
                row=db.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
                if not row or not verify_password(password,row['password']):
                    self.failures[key]=fails+[time.time()];raise APIError(401,'Invalid credentials')
                self.failures.pop(key,None);token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32)
                db.execute('DELETE FROM sessions WHERE expires<?',(time.time(),))
                db.execute('INSERT INTO sessions VALUES(?,?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),row['id'],csrf,time.time()+43200))
                return {'user':{'id':row['id'],'username':row['username'],'role':row['role']},'csrf':csrf},200,[self.cookie(token)]
        if not s:raise APIError(401,'Sign in first')
        uid=s['user_id']
        with self.store.connect() as db:
            if p=='/api/logout' and m=='POST':
                db.execute('DELETE FROM sessions WHERE token_hash=?',(s['token_hash'],));return {'ok':True},200,[self.cookie('',True)]
            if p=='/api/projects' and m=='GET':
                rows=db.execute('SELECT data,version FROM projects WHERE user_id=? ORDER BY updated DESC',(uid,)).fetchall()
                return {'projects':[{**json.loads(r['data']),'version':r['version']} for r in rows]},200,[]
            match=re.fullmatch(r'/api/projects/([A-Za-z0-9_-]{8,80})(/history)?',p)
            if match:
                pid=match[1];existing=db.execute('SELECT * FROM projects WHERE id=?',(pid,)).fetchone()
                if existing and existing['user_id']!=uid:raise APIError(404,'Project not found')
                if match[2] and m=='GET':
                    if not existing:raise APIError(404,'Project not found')
                    return {'revisions':[{'version':r['version'],'created':r['created'],'project':json.loads(r['data'])} for r in db.execute('SELECT * FROM revisions WHERE project_id=? ORDER BY version DESC',(pid,))]},200,[]
                if m=='PUT' and not match[2]:
                    project=validate_project(d)
                    if project['id']!=pid:raise APIError(400,'Project id mismatch')
                    expected=d.get('version',0)
                    if not isinstance(expected,int) or isinstance(expected,bool) or expected<0:raise APIError(400,'Invalid version')
                    db.execute('BEGIN IMMEDIATE')
                    existing=db.execute('SELECT * FROM projects WHERE id=?',(pid,)).fetchone()
                    if existing and existing['user_id']!=uid:raise APIError(404,'Project not found')
                    current=existing['version'] if existing else 0
                    if expected!=current:raise APIError(409,'Project changed on server. Reload before saving; your local work is retained.')
                    project['version']=current+1;blob=json.dumps(project,ensure_ascii=False,allow_nan=False)
                    db.execute('INSERT INTO projects VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET version=excluded.version,data=excluded.data,updated=excluded.updated',(pid,uid,current+1,blob,now()))
                    db.execute('INSERT INTO revisions VALUES(?,?,?,?)',(pid,current+1,blob,now()))
                    return {'project':project},200,[]
                if m=='DELETE' and not match[2]:
                    if not existing:raise APIError(404,'Project not found')
                    db.execute('DELETE FROM revisions WHERE project_id=?',(pid,));db.execute('DELETE FROM projects WHERE id=?',(pid,));return {'ok':True},200,[]
            if p=='/api/courses' and m=='GET':
                rows=db.execute('SELECT DISTINCT c.* FROM courses c LEFT JOIN members mb ON c.id=mb.course_id WHERE c.teacher_id=? OR mb.user_id=?',(uid,uid)).fetchall()
                return {'courses':[dict(r) for r in rows]},200,[]
            if p=='/api/courses' and m=='POST':
                if s['role']!='teacher':raise APIError(403,'Teacher role required')
                cid='c_'+secrets.token_hex(10);name=clean_text(d,'name',160,True);brief=clean_text(d,'brief',10000)
                code=secrets.token_hex(5).upper();db.execute('INSERT INTO courses VALUES(?,?,?,?,?,?)',(cid,uid,name,brief,code,now()));db.execute('INSERT INTO members VALUES(?,?)',(cid,uid))
                return {'id':cid,'name':name,'code':code,'brief':brief},201,[]
            if p=='/api/courses/join' and m=='POST':
                code=clean_text(d,'code',20,True).upper();course=db.execute('SELECT * FROM courses WHERE code=?',(code,)).fetchone()
                if not course:raise APIError(404,'Join code not found')
                db.execute('INSERT OR IGNORE INTO members VALUES(?,?)',(course['id'],uid));return {'course':dict(course)},200,[]
            match=re.fullmatch(r'/api/courses/(c_[0-9a-f]{20})/(submit|submissions)',p)
            if match:
                cid,action=match.groups();course=db.execute('SELECT * FROM courses WHERE id=?',(cid,)).fetchone()
                member=db.execute('SELECT 1 FROM members WHERE course_id=? AND user_id=?',(cid,uid)).fetchone()
                if not course or not member:raise APIError(404,'Course not found')
                if action=='submit' and m=='POST':
                    project=db.execute('SELECT * FROM projects WHERE id=? AND user_id=?',(d.get('project_id',''),uid)).fetchone()
                    if not project:raise APIError(404,'Save your project before submitting')
                    sid='s_'+secrets.token_hex(12);db.execute('INSERT INTO submissions VALUES(?,?,?,?,?,?,?,?)',(sid,cid,uid,project['id'],project['version'],project['data'],None,now()))
                    return {'id':sid},201,[]
                if action=='submissions' and m=='GET':
                    query='SELECT sub.*,u.username FROM submissions sub JOIN users u ON u.id=sub.user_id WHERE course_id=?';args=[cid]
                    if course['teacher_id']!=uid:query+=' AND user_id=?';args.append(uid)
                    rows=db.execute(query+' ORDER BY created DESC',args).fetchall()
                    return {'submissions':[{**dict(r),'snapshot':json.loads(r['snapshot']),'feedback':json.loads(r['feedback']) if r['feedback'] else None} for r in rows]},200,[]
            match=re.fullmatch(r'/api/submissions/(s_[0-9a-f]{24})/review',p)
            if match and m=='POST':
                row=db.execute('SELECT s.id,c.teacher_id FROM submissions s JOIN courses c ON s.course_id=c.id WHERE s.id=?',(match[1],)).fetchone()
                if not row or row['teacher_id']!=uid:raise APIError(404,'Submission not found')
                comment=clean_text(d,'comment',15000,True);rubric=d.get('rubric',{})
                if not isinstance(rubric,dict) or any(k not in ('understanding','choice','inheritance','validation','innovation') or not isinstance(v,int) or isinstance(v,bool) or not 0<=v<=4 for k,v in rubric.items()):raise APIError(400,'Invalid review rubric')
                fb={'comment':comment,'rubric':rubric,'reviewer':s['username'],'created':now()};db.execute('UPDATE submissions SET feedback=? WHERE id=?',(json.dumps(fb,ensure_ascii=False),match[1]));return {'feedback':fb},200,[]
        raise APIError(404,'Endpoint not found')
