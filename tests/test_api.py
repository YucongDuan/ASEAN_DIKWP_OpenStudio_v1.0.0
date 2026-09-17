"""WSGI and persistence regression tests. Uses isolated temporary databases."""
from __future__ import annotations
import io,json,tempfile,unittest
from pathlib import Path
from app.server import Application,APIError,password_hash,verify_password,validate_project

class Client:
    def __init__(self,app):self.app=app;self.cookie='';self.csrf=''
    def call(self,method,path,data=None,**extra):
        raw=json.dumps(data or {},ensure_ascii=False).encode();raw=extra.pop('raw',raw)
        env={'REQUEST_METHOD':method,'PATH_INFO':path,'HTTP_HOST':'127.0.0.1:8765','CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)),'wsgi.input':io.BytesIO(raw),'HTTP_ORIGIN':'http://127.0.0.1:8765','HTTP_COOKIE':self.cookie,'HTTP_X_CSRF_TOKEN':self.csrf,'REMOTE_ADDR':'127.0.0.1'};env.update(extra)
        response={}
        def start(status,headers):response.update(status=int(status.split()[0]),headers=dict(headers))
        body=b''.join(self.app(env,start));response['raw']=body
        response['data']=json.loads(body) if response['headers']['Content-Type'].startswith('application/json') else body.decode()
        if 'Set-Cookie' in response['headers']:self.cookie=response['headers']['Set-Cookie'].split(';')[0]
        if isinstance(response['data'],dict) and response['data'].get('csrf'):self.csrf=response['data']['csrf']
        return response
    def login(self,name):return self.call('POST','/api/login',{'username':name,'password':'testPassword_123'})

def project(pid='project_alpha'):
    return {'schema':'openstudio.project/1','id':pid,'title':'中越课程作品','purpose':'learn','repositories':[],'runs':[],'version':0}

class APITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.app=Application(Path(self.tmp.name)/'db.sqlite3')
        for name,role in [('alice','student'),('bob','student'),('teacher','teacher'),('otherteacher','teacher')]:self.app.store.create_user(name,'testPassword_123',role)
        self.a=Client(self.app);self.b=Client(self.app);self.t=Client(self.app);self.o=Client(self.app)
        self.a.login('alice');self.b.login('bob');self.t.login('teacher');self.o.login('otherteacher')
    def tearDown(self):self.tmp.cleanup()
    def status(self,r,n):self.assertEqual(r['status'],n,r['data']);return r['data']
    def save(self,c=None,p=None):return self.status((c or self.a).call('PUT','/api/projects/'+(p or project())['id'],p or project()),200)['project']
    def course(self):return self.status(self.t.call('POST','/api/courses',{'name':'多语种共创','brief':'Explore a problem, no imposed deadline'}),201)
    def test_health(self):self.assertTrue(self.status(Client(self.app).call('GET','/api/health'),200)['ok'])
    def test_static_home(self):self.assertIn('DIKWP OpenStudio',self.status(self.a.call('GET','/'),200))
    def test_static_traversal(self):self.status(self.a.call('GET','/../app/server.py'),404)
    def test_encoded_traversal(self):self.status(self.a.call('GET','/%2e%2e/LICENSE'),404)
    def test_private_database_not_served(self):self.status(self.a.call('GET','/../instance/studio.sqlite3'),404)
    def test_host_restriction(self):self.status(self.a.call('GET','/api/health',HTTP_HOST='evil.invalid'),403)
    def test_origin_restriction(self):self.status(self.a.call('PUT','/api/projects/project_alpha',project(),HTTP_ORIGIN='https://evil.invalid'),403)
    def test_csrf_restriction(self):self.status(self.a.call('PUT','/api/projects/project_alpha',project(),HTTP_X_CSRF_TOKEN=''),403)
    def test_unauthenticated_project(self):self.status(Client(self.app).call('GET','/api/projects'),401)
    def test_nonjson_rejected(self):self.status(self.a.call('POST','/api/courses',{},CONTENT_TYPE='text/plain'),415)
    def test_malformed_json_rejected(self):self.status(self.a.call('POST','/api/courses',raw=b'{bad'),400)
    def test_nan_json_rejected(self):self.status(self.a.call('POST','/api/courses',raw=b'{"x":NaN}'),400)
    def test_array_json_rejected(self):self.status(self.a.call('POST','/api/courses',raw=b'[]'),400)
    def test_oversized_rejected_before_read(self):self.status(self.a.call('POST','/api/courses',CONTENT_LENGTH='700001'),413)
    def test_negative_length_rejected(self):self.status(self.a.call('POST','/api/courses',CONTENT_LENGTH='-1'),413)
    def test_bad_length_rejected(self):self.status(self.a.call('POST','/api/courses',CONTENT_LENGTH='abc'),400)
    def test_security_headers(self):
        h=self.a.call('GET','/')['headers'];self.assertEqual(h['X-Frame-Options'],'DENY');self.assertIn("script-src 'self'",h['Content-Security-Policy'])
    def test_cookie_flags(self):
        h=self.a.login('alice')['headers']['Set-Cookie'];self.assertIn('HttpOnly',h);self.assertIn('SameSite=Strict',h)
    def test_student_registration_role_injection(self):
        r=self.status(Client(self.app).call('POST','/api/register',{'username':'eve','password':'testPassword_123','role':'teacher'}),201);self.assertEqual(r['user']['role'],'student')
    def test_duplicate_user(self):self.status(Client(self.app).call('POST','/api/register',{'username':'ALICE','password':'testPassword_123'}),409)
    def test_short_password(self):self.status(Client(self.app).call('POST','/api/register',{'username':'new','password':'short'}),400)
    def test_wrong_password(self):self.status(self.a.call('POST','/api/login',{'username':'alice','password':'incorrect_pass'}),401)
    def test_rate_limit(self):
        c=Client(self.app)
        for _ in range(8):self.status(c.call('POST','/api/login',{'username':'ghost','password':'incorrect_pass'}),401)
        self.status(c.call('POST','/api/login',{'username':'ghost','password':'incorrect_pass'}),429)
    def test_session_role(self):self.assertEqual(self.status(self.t.call('GET','/api/session'),200)['user']['role'],'teacher')
    def test_logout_invalidates(self):self.status(self.a.call('POST','/api/logout'),200);self.status(self.a.call('GET','/api/projects'),401)
    def test_save_increment_version(self):
        p=self.save();self.assertEqual(p['version'],1);p['changed']='New normalization';p=self.save(p=p);self.assertEqual(p['version'],2)
    def test_stale_save_conflict(self):self.save();self.status(self.a.call('PUT','/api/projects/project_alpha',project()),409)
    def test_history(self):
        p=self.save();p['title']='修订版';self.save(p=p);r=self.status(self.a.call('GET','/api/projects/project_alpha/history'),200);self.assertEqual([x['version'] for x in r['revisions']],[2,1]);self.assertEqual(r['revisions'][1]['project']['title'],'中越课程作品')
    def test_private_list(self):self.save();self.assertEqual(self.status(self.b.call('GET','/api/projects'),200)['projects'],[])
    def test_cannot_overwrite_other_user(self):self.save();self.status(self.b.call('PUT','/api/projects/project_alpha',project()),404)
    def test_cannot_read_other_history(self):self.save();self.status(self.b.call('GET','/api/projects/project_alpha/history'),404)
    def test_cannot_delete_other(self):self.save();self.status(self.b.call('DELETE','/api/projects/project_alpha'),404)
    def test_delete_own(self):self.save();self.status(self.a.call('DELETE','/api/projects/project_alpha'),200);self.assertEqual(self.status(self.a.call('GET','/api/projects'),200)['projects'],[])
    def test_id_mismatch(self):self.status(self.a.call('PUT','/api/projects/project_alpha',project('project_other')),400)
    def test_project_bool_version_rejected(self):p=project();p['version']=True;self.status(self.a.call('PUT','/api/projects/project_alpha',p),400)
    def test_invalid_source(self):p=project();p['repositories']=[{'name':'abc','url':'https://evil.invalid'}];self.status(self.a.call('PUT','/api/projects/project_alpha',p),400)
    def test_malformed_run(self):p=project();p['runs']=[{}];self.status(self.a.call('PUT','/api/projects/project_alpha',p),400)
    def test_student_cannot_create_class(self):self.status(self.a.call('POST','/api/courses',{'name':'unauthorized'}),403)
    def test_join_class(self):
        c=self.course();self.status(self.a.call('POST','/api/courses/join',{'code':c['code']}),200);self.assertEqual(len(self.status(self.a.call('GET','/api/courses'),200)['courses']),1)
    def test_bad_join_code(self):self.status(self.a.call('POST','/api/courses/join',{'code':'NONEXISTENT'}),404)
    def test_membership_required_for_submission(self):
        c=self.course();self.save();self.status(self.a.call('POST',f"/api/courses/{c['id']}/submit",{'project_id':'project_alpha'}),404)
    def test_teacher_feedback_and_peer_privacy(self):
        c=self.course();cid=c['id']
        for client,pid in [(self.a,'project_alpha'),(self.b,'project_beta')]:
            self.status(client.call('POST','/api/courses/join',{'code':c['code']}),200);self.save(client,project(pid));self.status(client.call('POST',f'/api/courses/{cid}/submit',{'project_id':pid}),201)
        all_=self.status(self.t.call('GET',f'/api/courses/{cid}/submissions'),200)['submissions'];self.assertEqual(len(all_),2)
        own=self.status(self.a.call('GET',f'/api/courses/{cid}/submissions'),200)['submissions'];self.assertEqual(len(own),1);sid=own[0]['id']
        self.status(self.o.call('POST',f'/api/submissions/{sid}/review',{'comment':'not your teacher'}),404)
        self.status(self.a.call('POST',f'/api/submissions/{sid}/review',{'comment':'self escalation'}),404)
        self.status(self.t.call('POST',f'/api/submissions/{sid}/review',{'comment':'请解释单位标准化与币种检查的不同作用。','rubric':{'understanding':3}}),200)
        latest=self.status(self.a.call('GET',f'/api/courses/{cid}/submissions'),200)['submissions'];self.assertEqual(latest[0]['feedback']['rubric']['understanding'],3)
    def test_submission_snapshot_not_changed_by_edit(self):
        c=self.course();self.a.call('POST','/api/courses/join',{'code':c['code']});p=self.save();self.status(self.a.call('POST',f"/api/courses/{c['id']}/submit",{'project_id':p['id']}),201);p['title']='New title';self.save(p=p)
        s=self.status(self.t.call('GET',f"/api/courses/{c['id']}/submissions"),200)['submissions'][0];self.assertEqual(s['snapshot']['title'],'中越课程作品');self.assertEqual(s['version'],1)
    def test_foreign_project_submission_blocked(self):
        c=self.course();self.b.call('POST','/api/courses/join',{'code':c['code']});self.save();self.status(self.b.call('POST',f"/api/courses/{c['id']}/submit",{'project_id':'project_alpha'}),404)

class PasswordTests(unittest.TestCase):
    def test_hashes_salted(self):self.assertNotEqual(password_hash('somePassword123'),password_hash('somePassword123'))
    def test_verify(self):h=password_hash('somePassword123');self.assertTrue(verify_password('somePassword123',h));self.assertFalse(verify_password('anotherPassword',h))
    def test_corrupt_hash(self):self.assertFalse(verify_password('p','nothex'))
if __name__=='__main__':unittest.main()
