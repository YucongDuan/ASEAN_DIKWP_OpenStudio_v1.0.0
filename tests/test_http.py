"""Actual loopback HTTP checks, independent of the browser's in-memory harness."""
import http.cookiejar,json,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from wsgiref.simple_server import make_server,WSGIRequestHandler
from app.server import Application
class QuietHandler(WSGIRequestHandler):
    def log_message(self,*args):pass
class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.app=Application(Path(cls.tmp.name)/'http.sqlite3')
        cls.httpd=make_server('127.0.0.1',0,cls.app,handler_class=QuietHandler);cls.origin='http://127.0.0.1:'+str(cls.httpd.server_port);cls.app.public_origin=cls.origin;cls.app.host='127.0.0.1:'+str(cls.httpd.server_port)
        cls.thread=threading.Thread(target=cls.httpd.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.httpd.shutdown();cls.thread.join();cls.httpd.server_close();cls.tmp.cleanup()
    def test_health_over_http(self):
        with urllib.request.urlopen(self.origin+'/api/health') as r:self.assertTrue(json.load(r)['ok'])
    def test_javascript_served_over_http(self):
        with urllib.request.urlopen(self.origin+'/core.js') as r:self.assertIn(b'rankRepositories',r.read())
    def test_denies_private_http(self):
        with self.assertRaises(urllib.error.HTTPError) as ex:urllib.request.urlopen(self.origin+'/api/projects')
        self.assertEqual(ex.exception.code,401)
    def test_login_save_read_over_http(self):
        self.app.store.create_user('httpstudent','Http_test_password')
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        def call(path,payload=None,method='GET',csrf=''):
            req=urllib.request.Request(self.origin+path,data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':self.origin,'X-CSRF-Token':csrf},method=method)
            with opener.open(req) as r:return json.load(r)
        login=call('/api/login',{'username':'httpstudent','password':'Http_test_password'},'POST')
        p={'schema':'openstudio.project/1','id':'project_http','title':'HTTP project','repositories':[],'runs':[],'version':0}
        self.assertEqual(call('/api/projects/project_http',p,'PUT',login['csrf'])['project']['version'],1)
        self.assertEqual(call('/api/projects')['projects'][0]['title'],'HTTP project')
    def test_html_csp_over_http(self):
        with urllib.request.urlopen(self.origin+'/') as r:self.assertIn("script-src 'self'",r.headers['Content-Security-Policy']);self.assertIn(b'OpenStudio',r.read())
if __name__=='__main__':unittest.main()
