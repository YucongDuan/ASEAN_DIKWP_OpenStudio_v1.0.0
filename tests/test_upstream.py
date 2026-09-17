import io,json,stat,tempfile,unittest,zipfile,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from upstream import valid_repo,valid_sha,check_url,safe_extract,pin_manifest,fetch_repository,load_manifest
from sync_catalog import fetch_all,merge_catalog

def archive(entries):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        for name,content in entries:z.writestr(name,content)
    return b.getvalue()
class ArchiveTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_extract_strips_wrapper(self):
        fs=safe_extract(archive([('repo/README.md','learn'),('repo/LICENSE','license')]),self.root/'v');self.assertEqual((self.root/'v/README.md').read_text(),'learn');self.assertEqual(fs[0]['sha256'],hashlib.sha256(b'learn').hexdigest())
    def test_does_not_strip_single_file(self):safe_extract(archive([('README.md','learn')]),self.root/'v');self.assertTrue((self.root/'v/README.md').exists())
    def test_path_traversal(self):self.assertRaises(ValueError,safe_extract,archive([('../oops','x')]),self.root/'v')
    def test_absolute_path(self):self.assertRaises(ValueError,safe_extract,archive([('/tmp/oops','x')]),self.root/'v')
    def test_backslash(self):self.assertRaises(ValueError,safe_extract,archive([('a\\b','x')]),self.root/'v')
    def test_drive_path(self):self.assertRaises(ValueError,safe_extract,archive([('C:/oops','x')]),self.root/'v')
    def test_symlink(self):
        i=zipfile.ZipInfo('repo/link');i.create_system=3;i.external_attr=(stat.S_IFLNK|0o777)<<16
        self.assertRaises(ValueError,safe_extract,archive([(i,'../../oops')]),self.root/'v')
    def test_special_file(self):
        i=zipfile.ZipInfo('repo/fifo');i.create_system=3;i.external_attr=(stat.S_IFIFO|0o600)<<16
        self.assertRaises(ValueError,safe_extract,archive([(i,'')]),self.root/'v')
    def test_duplicate(self):
        import warnings
        with warnings.catch_warnings():warnings.simplefilter('ignore');raw=archive([('a','1'),('a','2')])
        self.assertRaises(ValueError,safe_extract,raw,self.root/'v')
    def test_existing_not_overwritten(self):
        d=self.root/'v';d.mkdir();(d/'safe').write_text('keep');self.assertRaises(ValueError,safe_extract,archive([('a','x')]),d);self.assertEqual((d/'safe').read_text(),'keep')
    def test_empty_archive(self):self.assertRaises(ValueError,safe_extract,archive([]),self.root/'v')
    def test_file_directory_collision_rolls_back(self):
        self.assertRaises(OSError,safe_extract,archive([('root/a','x'),('root/a/b','y')]),self.root/'v');self.assertFalse((self.root/'v').exists())
    def test_fetch_receipt_mock_transport(self):
        record={'name':'Example','owner':'YucongDuan','url':'https://github.com/YucongDuan/Example','commit':'a'*40};raw=archive([('root/LICENSE','Apache-2.0'),('root/code.py','print(123)')]);seen=[]
        def transport(url):seen.append(url);return raw
        r=fetch_repository(record,self.root/'vendor',transport);self.assertFalse(r['executed']);self.assertEqual(len(r['license_files']),1);self.assertIn('a'*40,seen[0]);self.assertTrue((self.root/'vendor/Example.receipt.json').exists())
    def test_pin_mock_transport(self):
        d={'schema':'openstudio.upstream-lock/1','repositories':[{'name':'Example','url':'https://github.com/YucongDuan/Example'}]}
        def f(url):return {'sha':'f'*40} if '/commits/' in url else {'full_name':'YucongDuan/Example','default_branch':'main','license':{'spdx_id':'Apache-2.0'}}
        r=pin_manifest(d,f);self.assertEqual(r['repositories'][0]['commit'],'f'*40);self.assertNotIn('commit',d['repositories'][0])
    def test_wrong_pin_identity(self):self.assertRaises(ValueError,pin_manifest,{'repositories':[{'name':'Example'}]},lambda _: {'full_name':'evil/Example'})
    def test_manifest_owner_rejected(self):
        p=self.root/'m.json';p.write_text(json.dumps({'schema':'openstudio.upstream-lock/1','repositories':[{'name':'a','owner':'evil','url':'https://github.com/evil/a'}]}));self.assertRaises(ValueError,load_manifest,p)

class InputTests(unittest.TestCase):
    def test_bad_repository_names(self):
        for name in ['../x','a/b','..','','https://x','a;rm']:
            with self.subTest(name=name):self.assertRaises(ValueError,valid_repo,name)
    def test_bad_shas(self):
        for sha in ['main','1234','z'*40,None]:
            with self.subTest(sha=sha):self.assertRaises(ValueError,valid_sha,sha)
    def test_allowed_url(self):self.assertEqual(check_url('https://api.github.com/repos/YucongDuan/test').hostname,'api.github.com')
    def test_url_restrictions(self):
        for u in ['http://api.github.com/x','https://evil.invalid/x','https://user:pw@api.github.com/x','https://api.github.com:444/x','file:///tmp/x']:
            with self.subTest(u=u):self.assertRaises(ValueError,check_url,u)
    def test_pagination(self):
        pages=[]
        def f(u):pages.append(u);return [{}]*100 if len(pages)==1 else [{}]*2
        self.assertEqual(len(fetch_all(f)),102);self.assertEqual(len(pages),2)
    def test_pagination_failure_no_partial(self):
        def f(u):
            if u.endswith('&page=1'):return [{}]*100
            raise RuntimeError('network failure')
        self.assertRaises(RuntimeError,fetch_all,f)
    def test_pagination_limit_no_partial(self):self.assertRaises(ValueError,fetch_all,lambda u:[{}]*100)
    def test_nonlist_response(self):self.assertRaises(ValueError,fetch_all,lambda u:{'message':'error'})
    def test_merge_preserves_annotations(self):
        old={'repositories':[{'name':'Example','tags':['education'],'featured':True,'role':'Learning','description':'old'}]};rows=[{'name':'Example','id':3,'html_url':'https://github.com/YucongDuan/Example','owner':{'login':'YucongDuan'},'description':'new','license':{'spdx_id':'Apache-2.0'}}];r=merge_catalog(old,rows);self.assertEqual(r['repositories'][0]['tags'],['education']);self.assertEqual(r['repositories'][0]['description'],'new');self.assertEqual(old['repositories'][0]['description'],'old')
    def test_merge_new_metadata_not_verified(self):
        r=merge_catalog({'repositories':[]},[{'name':'New','id':4,'html_url':'https://github.com/YucongDuan/New','owner':{'login':'YucongDuan'}}]);self.assertEqual(r['repositories'][0]['verification'],'metadata-only');self.assertFalse(r['repositories'][0]['featured'])
    def test_missing_remains_historical(self):r=merge_catalog({'repositories':[{'name':'old'}]},[]);self.assertFalse(r['repositories'][0]['present_in_latest_sync'])
    def test_foreign_source_not_imported(self):r=merge_catalog({'repositories':[]},[{'name':'a','owner':{'login':'someone'}}]);self.assertEqual(r['repositories'],[])
if __name__=='__main__':unittest.main()
