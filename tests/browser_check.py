"""UI integration checks with browser set_content and an explicit in-memory storage double.
The managed environment blocks URL navigation. This harness does not alter policy:
rendering is in-memory, and an exposed test transport calls the real WSGI application.
Actual HTTP routes are checked separately in test_http.py.
"""
import json,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from playwright.sync_api import sync_playwright
from app.server import Application
from test_api import Client
checks=[];errors=[]
def check(name,cond):
    assert cond,name
    checks.append(name);print('PASS',name,flush=True)
html=(ROOT/'OpenStudio_Offline.html').read_text()
# Deliberately visible test double for about:blank, not a claim about real disk persistence.
inject="""<script>const __testStorage={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>__testStorage[k]??null,setItem:(k,v)=>{__testStorage[k]=String(v)},removeItem:k=>{delete __testStorage[k]}}});</script>"""
html=html.replace('<script>const STUDIO_DATA',inject+'<script>const STUDIO_DATA')
with tempfile.TemporaryDirectory() as td,sync_playwright() as pw:
    app=Application(Path(td)/'test.sqlite3');app.store.create_user('teacher','testPassword_123','teacher');app.store.create_user('student','testPassword_123')
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':960},accept_downloads=True)
    def newpage():
        p=context.new_page();p.set_default_timeout(5000);p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html,wait_until='load');p.wait_for_selector('.hero');return p
    p=newpage()
    check('home metrics 483', '483' in p.locator('.stat').first.inner_text());check('home six problem starters',p.locator('.scenario').count()==6)
    p.evaluate('document.activeElement?.blur();window.scrollTo(0,0)');p.wait_for_timeout(80);p.screenshot(path=str(ROOT/'qa/home.png'),full_page=True)
    for lang in ['zh','en','vi','id','ms','pt','fil','th','km','lo','my','ta','tet']:
        p.locator('#locale').select_option(lang);check('locale '+lang,p.evaluate('locale')==lang and p.locator('h1').inner_text().strip()!='')
    p.locator('#locale').select_option('vi');p.locator('.nav [data-to="learn"]').click();p.wait_for_selector('#reading')
    check('Vietnamese lesson automatically selected',p.locator('#reading').input_value()=='vi');check('Vietnamese full body', 'tài nguyên' in p.locator('.lesson-body').inner_text())
    p.evaluate('document.activeElement?.blur();window.scrollTo(0,0)');p.wait_for_timeout(80);p.screenshot(path=str(ROOT/'qa/vietnamese_learning.png'),full_page=True)
    p.locator('#locale').select_option('zh')
    for l in json.loads((ROOT/'data/lessons.json').read_text()):
        p.locator(f'.lesson-menu [data-id="{l["id"]}"]').click();p.locator(f'input[name="answer"][value="{l["quiz"]["answer"]}"]').check();p.locator('#quiz-form button[type="submit"]').click();check('quiz interaction '+l['id'],'本次自测正确' in p.locator('#quiz-result').inner_text())
    check('quiz progress 12 persisted in test storage',p.evaluate('Object.values(progress.quizzes).filter(x=>x.correct).length')==12)
    p.locator('.nav [data-to="compass"]').click();p.locator('#problem-query').fill('giáo dục ngôn ngữ');p.locator('[data-action="recommend"]').click()
    check('Vietnamese query identifies concepts', 'language' in p.evaluate('C.findConcepts(repoQuery,D.concepts)'))
    p.locator('#featured').check();check('curated filter',p.locator('.repository').count()==24)
    p.locator('.repository [data-action="select"]').nth(0).click();p.locator('.repository [data-action="select"]').nth(1).click();check('selection basket',p.evaluate('selected.length')==2)
    p.locator('[data-action="compare"]').click();check('comparison modal opens',p.locator('#modal').inner_text().strip()!='');p.keyboard.press('Escape')
    p.locator('[data-action="route"]').click();check('learning route contains modules',p.locator('#modal [data-action="lesson"]').count()>1);p.keyboard.press('Escape')
    p.evaluate('document.activeElement?.blur();window.scrollTo(0,0)');p.wait_for_timeout(80);p.screenshot(path=str(ROOT/'qa/repository_compass.png'),full_page=True)
    p.locator('.nav [data-to="home"]').click();p.locator('.scenario [data-action="scenario"]').first.click();check('starter generates project',len(p.locator('[data-projectfield="title"]').input_value())>0)
    for lab in ['alignment','three-no','action','purpose']:
        p.evaluate('(v)=>go("labs/"+v)',lab);p.locator('[data-action="run-lab"]').click();check('lab runs '+lab,p.locator('#lab-results .result-banner').count()==2);p.locator('[data-action="attach-run"]').click()
    check('four results attached',p.evaluate('project.runs.length')==4)
    p.evaluate('go("labs/alignment")');p.locator('[data-labfield="right.purpose"]').fill('send-offer');p.locator('[data-action="run-lab"]').click();check('changed purpose produces mismatch',p.evaluate('lastRun.output.revision.status')=='mismatch');p.locator('[data-action="ablation"]').click();check('ablation comparison visible','equivalent' in p.locator('#modal').inner_text());p.keyboard.press('Escape')
    p.evaluate('document.activeElement?.blur();window.scrollTo(0,0)');p.wait_for_timeout(80);p.screenshot(path=str(ROOT/'qa/semantic_lab.png'),full_page=True)
    p.locator('.nav [data-to="studio"]').click();p.locator('[data-projectfield="changed"]').fill('添加单位对齐与币种检查');p.locator('[data-action="save-project"]').click();check('project saved to test storage',p.evaluate('projects.length')==1)
    p.locator('[data-action="replay"]').first.click();check('experiment replay consistent','回放与保存结果一致' in p.locator('#modal').inner_text());p.keyboard.press('Escape')
    with p.expect_download() as ev:p.locator('[data-action="export-zip"]').click()
    dl=ev.value;dl.save_as(str(ROOT/'qa/browser_export.zip'));check('browser creates ZIP download',(ROOT/'qa/browser_export.zip').stat().st_size>1000)
    p.locator('.nav [data-to="library"]').click();check('107 source cards',p.locator('.source-list > article').count()==107)
    p.locator('[data-action="library-tab"][data-id="books"]').click();check('ten formal books',p.locator('.book').count()==10);check('Henan book included','河南科学技术出版社' in p.locator('#main').inner_text())
    p.locator('[data-action="report"]').click();p.locator('#slide-picker').select_option('128');check('lecture page 128',p.locator('#slide-picker').input_value()=='128')
    p.set_viewport_size({'width':390,'height':844});p.evaluate('go("home")');check('mobile home no horizontal overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'));p.evaluate('document.activeElement?.blur();window.scrollTo(0,0)');p.wait_for_timeout(80);p.screenshot(path=str(ROOT/'qa/mobile_home.png'),full_page=True)
    p.evaluate('go("learn")');check('mobile lesson no overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
    p.set_viewport_size({'width':1440,'height':960})
    # Real backend, explicit test transport. No network/browser restrictions altered.
    def attach_backend(page):
        client=Client(app)
        def bridge(req):
            r=client.call(req['method'],req['url'],json.loads(req.get('body') or '{}'),HTTP_X_CSRF_TOKEN=req.get('headers',{}).get('X-CSRF-Token',''))
            return {'status':r['status'],'body':r['data']}
        page.expose_function('testBackend',bridge)
        page.evaluate("window.fetch=async (url,options={})=>{const r=await window.testBackend({url,method:options.method||'GET',body:options.body,headers:options.headers||{}});return {ok:r.status>=200&&r.status<300,status:r.status,json:async()=>r.body};};hasServer=true;go('classroom');")
        return client
    teacher=newpage();attach_backend(teacher);teacher.locator('#username').fill('teacher');teacher.locator('#password').fill('testPassword_123');teacher.locator('#auth-form button[type="submit"]').click();teacher.wait_for_selector('#course-form')
    teacher.locator('#course-name').fill('中越语义共创课堂');teacher.locator('#course-brief').fill('选择自己的跨语言问题，保留继承与创新的记录。');teacher.locator('#course-form button[type="submit"]').click();teacher.wait_for_selector('.course');code=teacher.evaluate('classCourses[0].code');cid=teacher.evaluate('classCourses[0].id');check('teacher creates class',bool(code))
    student=newpage();attach_backend(student);student.locator('#username').fill('student');student.locator('#password').fill('testPassword_123');student.locator('#auth-form button[type="submit"]').click();student.wait_for_selector('#join-form');student.locator('#join-code').fill(code);student.locator('#join-form button[type="submit"]').click();student.wait_for_selector('.course');check('student joins class',student.locator('.course').count()==1)
    student.evaluate('go("home")');student.locator('.scenario [data-action="scenario"]').first.click();student.locator('[data-action="save-project"]').click();student.wait_for_function('project.version===1');check('server version save',student.evaluate('project.version')==1)
    student.evaluate('go("classroom")');student.locator('[data-action="submit-project"]').click();student.wait_for_selector('[data-action="view-submission"]');check('student submits snapshot',student.locator('[data-action="view-submission"]').count()==1)
    teacher.locator('[data-action="load-submissions"]').click();teacher.wait_for_selector('.review-form');teacher.locator('.review-form textarea').fill('单位标准化解释清楚；请补充币种不一致的反例。');teacher.locator('.review-form button').click();teacher.wait_for_function("Object.values(submissions).flat().some(s=>s.feedback?.comment.includes('币种'))");check('teacher saves feedback',True)
    student.locator('[data-action="load-submissions"]').click();student.wait_for_function("Object.values(submissions).flat().some(s=>s.feedback)");check('student receives feedback','补充币种' in student.locator('#course-list').inner_text());teacher.evaluate('document.activeElement?.blur();window.scrollTo(0,0)');teacher.wait_for_timeout(80);teacher.screenshot(path=str(ROOT/'qa/teacher_feedback.png'),full_page=True)
    check('no uncaught JS errors',len(errors)==0)
    browser.close()
result={'suite':'browser-ui','passed':len(checks),'failed':0,'checks':checks,'uncaught_errors':errors,'scope':'Chromium set_content; explicit in-memory localStorage double; real WSGI API through test transport. URL navigation is restricted by host policy; no end-to-end network-browser or real browser disk-persistence claim.'}
(ROOT/'qa/browser-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('TOTAL',len(checks),'passed')
