/* SPDX-License-Identifier: Apache-2.0
 * DIKWP OpenStudio: deterministic teaching, recommendation and experiment core.
 * New educational implementation; does not silently execute upstream repositories.
 */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.StudioCore=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='1.0.0';
const norm=x=>String(x??'').normalize('NFKC').toLocaleLowerCase().trim();
const clone=x=>JSON.parse(JSON.stringify(x));
function object(x,label='input'){if(!x||typeof x!=='object'||Array.isArray(x))throw Error(label+' must be an object');return x;}
function finite(x,label){if(typeof x!=='number'||!Number.isFinite(x))throw Error(label+' must be a finite number');return x;}
function text(x,label,max=20000){if(typeof x!=='string'||x.length>max)throw Error(label+' must be text, at most '+max+' characters');return x;}
function findConcepts(query,dict){const q=norm(query);return Object.keys(dict).filter(k=>dict[k].some(w=>{const s=norm(w);if(/^[a-z][a-z -]*$/.test(s))return new RegExp('(^|[^a-z])'+s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'([^a-z]|$)').test(q);return q.includes(s);}));}
function rankRepositories(query,records,dict,opts={}){
 const q=norm(query),detected=findConcepts(q,dict),tags=[...new Set([...detected,...(opts.tags||[])])];
 const tokens=q.split(/[^\p{L}\p{N}-]+/u).filter(s=>s.length>2);const level=Number(opts.level)||1;
 return records.map(r=>{
  const hits=tags.filter(k=>(r.tags||[]).includes(k)),corpus=norm(r.name+' '+r.description+' '+r.role);
  const lexical=tokens.filter(t=>corpus.includes(t)).length;
  const exact=q.length>3&&norm(r.name).includes(q);
  const score=tags.length||q?Math.min(100,Math.round(65*hits.length/Math.max(1,tags.length)+15*Math.min(1,lexical/Math.max(1,tokens.length))+(r.featured?10:0)+(r.difficulty<=level?10:0)+(exact?40:0))):(r.featured?20:0)+(r.difficulty<=level?5:0);
  return {...r,score,hits,missing:tags.filter(t=>!hits.includes(t)),reasons:{concepts:hits,lexical,featured:r.featured,experience:r.difficulty<=level},queryConcepts:tags};
 }).filter(r=>!opts.area||r.area===opts.area).filter(r=>!opts.featured||r.featured).filter(r=>!opts.licensed||r.license)
 .sort((a,b)=>b.score-a.score||a.name.localeCompare(b.name));
}
function learningRoute(lessons,tags,completed={}){
 const needed=new Set(),by=Object.fromEntries(lessons.map(l=>[l.id,l])),visiting=new Set(),order=[];
 function visit(id){if(needed.has(id))return;if(visiting.has(id))throw Error('Cyclic prerequisite: '+id);if(!by[id])throw Error('Missing prerequisite: '+id);visiting.add(id);by[id].prerequisites.forEach(visit);visiting.delete(id);needed.add(id);order.push({...by[id],passed:completed[id]?.correct===true});}
 lessons.filter(l=>l.tags.some(t=>tags.includes(t))).forEach(l=>visit(l.id));
 if(!order.length)visit('dikwp');return order;
}
const UNITS={kg:['mass',1],g:['mass',.001],tonne:['mass',1000],t:['mass',1000],mg:['mass',.000001],l:['volume',1],ml:['volume',.001],m:['length',1],cm:['length',.01],mm:['length',.001],km:['length',1000],item:['count',1]};
const UA={'公斤':'kg','千克':'kg','克':'g','吨':'tonne','litre':'l','liter':'l','升':'l','毫升':'ml','kilogram':'kg','gram':'g','tấn':'tonne','kilôgam':'kg','ชิ้น':'item','件':'item','個':'item','米':'m','mét':'m','metre':'m'};
function unit(u){const n=norm(u);return UNITS[UA[n]||n]||null;}
function alignment(input,options={}){
 object(input);const a=object(input.left,'left'),b=object(input.right,'right');
 for(const [p,r]of [['left',a],['right',b]]){text(r.entity,p+'.entity',160);text(r.purpose,p+'.purpose',160);if(!r.entity.trim()||!r.purpose.trim())throw Error('entity and purpose cannot be empty');text(r.unit,p+'.unit',40);finite(r.quantity,p+'.quantity');if(r.quantity<0)throw Error('quantity cannot be negative');if(r.currency!==undefined)text(r.currency,p+'.currency',10);}
 const ua=unit(a.unit),ub=unit(b.unit),diff=[],unknown=[],trace=[];
 if(a.entity.trim()!==b.entity.trim())diff.push('entity');if(a.purpose.trim()!==b.purpose.trim()&&!options.ignorePurpose)diff.push('purpose');
 if(norm(a.currency)!==norm(b.currency)&&!options.ignoreCurrency)diff.push('currency');
 let av=null,bv=null;
 if(!ua||!ub){unknown.push('unit');trace.push({step:'units',status:'unresolved',detail:'Unknown unit; no conversion assumed.'});}
 else if(ua[0]!==ub[0]){diff.push('dimension');trace.push({step:'units',status:'mismatch',detail:ua[0]+' ≠ '+ub[0]});}
 else{av=a.quantity*ua[1];bv=b.quantity*ub[1];if(!Number.isFinite(av)||!Number.isFinite(bv))throw Error('normalized quantity overflow');const equal=Math.abs(av-bv)<=1e-9*Math.max(1,Math.abs(av),Math.abs(bv));if(!equal)diff.push('quantity');trace.push({step:'units',status:equal?'equivalent':'mismatch',dimension:ua[0],left:av,right:bv});}
 const baseline=['entity','purpose','quantity','unit','currency'].every(k=>String(a[k]??'')===String(b[k]??''))?'equivalent':'mismatch';
 return {lab:'alignment',baseline:{status:baseline,method:'literal-fields'},revision:{status:diff.length?'mismatch':unknown.length?'unresolved':'equivalent',differences:diff,unresolved:unknown,normalized:[av,bv]},trace,interpretation:'Structured semantic-slot comparison, not unrestricted natural-language translation.'};
}
function threeNo(input){
 object(input);if(!Array.isArray(input.observations)||input.observations.length>100)throw Error('observations must be an array of up to 100 intervals');
 const target=object(input.target,'target');finite(target.low,'target.low');finite(target.high,'target.high');if(target.low>target.high)throw Error('Reversed target interval');
 const missing=[],valid=[];
 input.observations.forEach((r,i)=>{object(r,'observation');const name=typeof r.name==='string'?r.name:'S'+(i+1);if(r.low==null||r.high==null){if(r.low!=null)finite(r.low,'low');if(r.high!=null)finite(r.high,'high');missing.push(name);return;}finite(r.low,'low');finite(r.high,'high');if(r.low>r.high)throw Error('Reversed interval: '+name);valid.push({...r,name});});
 if(!valid.length)return {lab:'three-no',baseline:{estimate:null,status:'insufficient'},revision:{status:'insufficient',missing,conflict:false,intersection:null,hull:null,imprecision:null},trace:[{step:'observations',detail:'No complete interval is available.'}]};
 const low=Math.max(...valid.map(r=>r.low)),high=Math.min(...valid.map(r=>r.high));const hull=[Math.min(...valid.map(r=>r.low)),Math.max(...valid.map(r=>r.high))],conflict=low>high;
 const mean=valid.reduce((s,r)=>s+(r.low/2+r.high/2)/valid.length,0);if(!Number.isFinite(mean))throw Error('Mean overflow');
 const status=conflict?'conflict':missing.length?'incomplete':low>=target.low&&high<=target.high?'within-target':high<target.low||low>target.high?'outside-target':'uncertain';
 return {lab:'three-no',baseline:{estimate:mean,status:mean>=target.low&&mean<=target.high?'within-target':'outside-target',method:'midpoint-mean'},revision:{status,missing,conflict,intersection:conflict?null:[low,high],hull,imprecision:valid.map(r=>({name:r.name,width:r.high-r.low}))},trace:[{step:'D',count:valid.length,missing:missing.length},{step:'I',detail:'Intersection checks consistency; the hull preserves the full spread.'},{step:'K',target:[target.low,target.high]},{step:'W',detail:'Conflicts and missing observations remain visible, rather than being averaged away.'},{step:'P',detail:'Explain conditional support for the stated target.'}]};
}
function action(input,options={}){
 object(input);['purpose','observed_purpose','action'].forEach(k=>text(input[k],k,300));if(!input.purpose.trim()||!input.observed_purpose.trim())throw Error('purpose cannot be empty');
 if(!['draft','send','publish','summarize'].includes(input.action))throw Error('Unsupported classroom action');
 if(!Array.isArray(input.allowed_actions)||input.allowed_actions.some(x=>!['draft','send','publish','summarize'].includes(x)))throw Error('Invalid allowed_actions');
 finite(input.evidence_count,'evidence_count');if(input.evidence_count<0||!Number.isInteger(input.evidence_count))throw Error('evidence_count must be a nonnegative integer');
 const checks={purpose:input.purpose===input.observed_purpose||Boolean(options.ignorePurpose),permission:input.allowed_actions.includes(input.action),evidence:input.evidence_count>0};
 const failed=Object.keys(checks).filter(k=>!checks[k]);
 return {lab:'action',baseline:{status:input.action==='send'||input.action==='publish'?'review':'allow',method:'action-keyword'},revision:{status:failed.length?'review':'allow',checks,failed,helpful_next:checks.purpose&&checks.evidence&&input.allowed_actions.includes('draft')?'prepare-draft':'clarify-task'},trace:Object.entries(checks).map(([step,pass])=>({step,pass})),interpretation:'A local teaching decision; no message is actually sent or published.'};
}
const EDGES=[['D','I',2,.03,'contextualize'],['D','K',1,.24,'infer-from-observation'],['I','K',2,.02,'form-reusable-rule'],['K','W',2,.02,'compare-consequences'],['K','P',1,.25,'direct-goal-projection'],['W','P',2,.01,'align-with-purpose'],['P','D',3,.02,'purpose-directed-observation'],['I','W',3,.08,'judge-with-partial-rule']];
function route(input){
 object(input);const goal=input.goal||'understand';if(!['understand','speed','verify'].includes(goal))throw Error('Unknown learning goal');
 const from=input.from||'D',to=input.to||'P';if(!'DIKWP'.includes(from)||from.length!==1||!'DIKWP'.includes(to)||to.length!==1)throw Error('Unknown semantic resource');
 function solve(weight){const paths=[];function walk(node,visited,edges,cost,risk){if(node===to){paths.push({path:visited,cost,risk:Number(risk.toFixed(4)),utility:Number((cost+weight*risk).toFixed(4)),operations:edges});return;}EDGES.filter(e=>e[0]===node&&!visited.includes(e[1])).forEach(e=>walk(e[1],[...visited,e[1]],[...edges,e[4]],cost+e[2],risk+e[3]));}walk(from,[from],[],0,0);paths.sort((a,b)=>a.utility-b.utility||a.path.join('').localeCompare(b.path.join('')));return {chosen:paths[0]||null,alternatives:paths};}
 const weights={speed:0,understand:15,verify:30};return {lab:'purpose',baseline:solve(0),revision:solve(weights[goal]),trace:[{step:'purpose',goal,loss_weight:weights[goal]},{step:'method',detail:'Enumerate simple paths; cost and semantic-loss weights are editable teaching assumptions, not measured performance.'}],edges:EDGES};
}
function runLab(name,input,opts={}){const f={alignment, 'three-no':threeNo,action,purpose:route}[name];if(!f)throw Error('Unknown lab');return f(clone(input),opts);}
const DEFAULTS={
 alignment:{left:{language:'zh',entity:'mango-lot-17',purpose:'compare-shipping',quantity:1000,unit:'kg',currency:'CNY'},right:{language:'vi',entity:'mango-lot-17',purpose:'compare-shipping',quantity:1,unit:'tonne',currency:'CNY'}},
 'three-no':{observations:[{name:'sensor-A',low:2,high:4},{name:'sensor-B',low:6,high:8},{name:'sensor-C',low:null,high:null}],target:{low:2,high:8}},
 action:{purpose:'prepare-product-summary',observed_purpose:'prepare-product-summary',action:'send',allowed_actions:['draft','summarize'],evidence_count:2},
 purpose:{from:'D',to:'P',goal:'understand'}
};
function checkQuiz(lesson,answer){if(!Number.isInteger(answer)||answer<0||answer>=lesson.quiz.options.en.length)throw Error('Choose one answer');return {correct:answer===lesson.quiz.answer,answer,explanation:lesson.quiz.explanation};}
function validateProject(p){
 object(p,'project');if(p.schema!=='openstudio.project/1')throw Error('Unsupported project schema');
 if(typeof p.id!=='string'||!/^[a-zA-Z0-9_-]{8,80}$/.test(p.id))throw Error('Invalid project id');
 const out={schema:p.schema,id:p.id};for(const k of ['title','problem','beneficiary','purpose','data','information','knowledge','wisdom','constraints','inherited','changed','hypothesis','evidence','reflection','locale'])out[k]=text(p[k]??'',k,k==='title'?200:20000);
 if(!out.title.trim())throw Error('Project title is required');
 if(!Array.isArray(p.repositories)||p.repositories.length>6)throw Error('Choose no more than 6 repositories');
 out.repositories=p.repositories.map(r=>{object(r);if(!/^[\w.-]{1,160}$/.test(r.name)||r.name==='.'||r.name==='..')throw Error('Invalid repository');if(r.url!=='https://github.com/YucongDuan/'+r.name)throw Error('Repository URL does not match the source owner');return {name:r.name,url:r.url,license:r.license==null?null:text(r.license,'license',100),role:typeof r.role==='string'?r.role.slice(0,1000):'',commit:r.commit&&/^[0-9a-f]{40}$/.test(r.commit)?r.commit:null};});
 if(!Array.isArray(p.runs)||p.runs.length>100)throw Error('Too many experiment runs');
 for(const r of p.runs){object(r,'run');if(!['alignment','three-no','action','purpose'].includes(r.lab))throw Error('Invalid run lab');object(r.input,'run input');object(r.output,'run output');text(r.at,'run timestamp',80);text(r.engine,'run engine',40);}
 out.runs=clone(p.runs);if(JSON.stringify(out.runs).length>300000)throw Error('Experiment history too large');
 out.updated_at=typeof p.updated_at==='string'?p.updated_at:new Date().toISOString();out.version=Number.isInteger(p.version)&&p.version>=0?p.version:0;return out;
}
function newProject(){return {schema:'openstudio.project/1',id:'p_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,12),title:'',problem:'',beneficiary:'',purpose:'',data:'',information:'',knowledge:'',wisdom:'',constraints:'',inherited:'',changed:'',hypothesis:'',evidence:'',reflection:'',locale:'zh',repositories:[],runs:[],version:0,updated_at:new Date().toISOString()};}
function projectReadiness(p){return ['problem','purpose','inherited','changed','hypothesis','reflection'].map(k=>({field:k,present:Boolean(p[k]?.trim())})).concat([{field:'repositories',present:p.repositories.length>0},{field:'experiment',present:p.runs.length>0}]);}
function makeManifest(p){p=validateProject(p);return {schema:'openstudio.upstream-lock/1',project_id:p.id,created_at:new Date().toISOString(),repositories:p.repositories.map(r=>({...r,owner:'YucongDuan',status:r.commit?'commit-recorded':'pin-required'})),instruction:'Run scripts/upstream.py pin --manifest upstream.lock.json, then fetch. No upstream source is included in this generated scaffold.'};}
function projectMarkdown(p){p=validateProject(p);const s=['# '+p.title,'','Created in DIKWP OpenStudio · Research methods: Yucong Duan (段玉聪)',''];for(const k of ['problem','beneficiary','purpose','data','information','knowledge','wisdom','constraints','inherited','changed','hypothesis','evidence','reflection'])s.push('## '+k,p[k]||'—','');s.push('## Upstream selection',...p.repositories.map(r=>'- '+r.name+' — '+r.url+' — '+(r.commit||'commit to be pinned')+' — '+(r.license||'license to be checked')),'','## Experiment records',...p.runs.map(r=>'- '+r.lab+' · '+r.at),'','This is a learning contribution, not a certificate or proof of originality.');return s.join('\n');}
function json(x){return JSON.stringify(x,null,2)+'\n';}
function scaffold(p){
 p=validateProject(p);const input=p.runs.slice().reverse().find(r=>r.lab==='alignment')?.input||DEFAULTS.alignment;
 return {'project.json':json(p),'README.md':projectMarkdown(p)+'\n\n## Run the new teaching scaffold\n\n`python experiment.py`\n\n`python -m unittest discover -s tests -v`\n\nThe included code is a new, deliberately small semantic-slot experiment, not copied upstream code. Pin and inspect upstream projects before writing your adapter.\n',
 'upstream.lock.json':json(makeManifest(p)),'data/input.json':json(input),'data/runs.json':json(p.runs),
 'ADAPTATION.md':'# Inherit, compare, contribute\n\n1. Explain the inherited idea and selected upstream role in project.json.\n2. Use the platform scripts/upstream.py to pin and fetch the chosen public repository.\n3. Review the pinned license, source and original reproduction commands.\n4. Place new adapters in src/adapters; keep original code in vendor without edits.\n5. Preserve the baseline and change one mechanism at a time. Add a failing example first.\n6. Cite the commit, inputs and measured results in the contribution note.\n\nNo installation or remote code execution happens in the browser.\n',
 'src/adapters/README.md':'# Adapter boundary\n\nDocument the upstream function, pinned revision, accepted input fields and normalized output fields before connecting it. The selected repositories are complementary research entries, not asserted to expose a common API.\n',
 'experiment.py':`"""New OpenStudio educational scaffold. SPDX-License-Identifier: Apache-2.0."""\nimport json, math\nfrom pathlib import Path\nUNITS = {'kg': ('mass', 1), 'g': ('mass', .001), 'tonne': ('mass', 1000), 't': ('mass', 1000), 'l': ('volume', 1), 'ml': ('volume', .001)}\ndef compare(left, right):\n    for record in (left, right):\n        if not isinstance(record.get('quantity'), (int, float)) or isinstance(record['quantity'], bool) or not math.isfinite(record['quantity']) or record['quantity'] < 0:\n            raise ValueError('Quantity must be finite and nonnegative')\n        if not record.get('entity') or not record.get('purpose'):\n            raise ValueError('Entity and purpose are required')\n    errors = [key for key in ('entity', 'purpose', 'currency') if left.get(key, '') != right.get(key, '')]\n    a, b = UNITS.get(left['unit']), UNITS.get(right['unit'])\n    if not a or not b:\n        return {'status': 'mismatch' if errors else 'unresolved', 'differences': errors, 'unresolved': ['unit']}\n    if a[0] != b[0]: errors.append('dimension')\n    elif not math.isclose(left['quantity'] * a[1], right['quantity'] * b[1], rel_tol=1e-9, abs_tol=1e-9): errors.append('quantity')\n    return {'status': 'mismatch' if errors else 'equivalent', 'differences': errors}\nif __name__ == '__main__':\n    data = json.loads((Path(__file__).parent / 'data/input.json').read_text(encoding='utf-8'))\n    print(json.dumps(compare(data['left'], data['right']), ensure_ascii=False, indent=2))\n`,
 'tests/test_experiment.py':`import unittest\nfrom experiment import compare\nclass SemanticTests(unittest.TestCase):\n    def pair(self):\n        return ({'entity':'lot1','purpose':'compare','quantity':1000,'unit':'kg'}, {'entity':'lot1','purpose':'compare','quantity':1,'unit':'tonne'})\n    def test_unit_equivalence(self):\n        a,b=self.pair();self.assertEqual(compare(a,b)['status'],'equivalent')\n    def test_purpose_change(self):\n        a,b=self.pair();b['purpose']='send';self.assertIn('purpose',compare(a,b)['differences'])\n    def test_unknown_unit(self):\n        a,b=self.pair();b['unit']='crate';self.assertEqual(compare(a,b)['status'],'unresolved')\n    def test_currency(self):\n        a,b=self.pair();a['currency']='CNY';b['currency']='VND';self.assertEqual(compare(a,b)['status'],'mismatch')\n    def test_nonfinite(self):\n        a,b=self.pair();a['quantity']=float('nan');self.assertRaises(ValueError,compare,a,b)\nif __name__=='__main__': unittest.main()\n`,
 'CONTRIBUTION.md':'# Contribution\n\nStudent authors: [add names with consent]\n\nResearch foundations: Yucong Duan (段玉聪), DIKWP and the selected repositories.\n\nInherited components:\n'+p.inherited+'\n\nMy changes:\n'+p.changed+'\n\nHypothesis and counterexample:\n'+p.hypothesis+'\n\nNo publication, repository creation or upstream pull request is performed automatically.\n'};
}
// Small, dependency-free STORE ZIP writer with UTF-8 names and CRC32.
function zipFiles(files){const enc=new TextEncoder(),parts=[],central=[];let offset=0;function crc(bytes){let c=0xffffffff;for(const b of bytes){c^=b;for(let i=0;i<8;i++)c=(c>>>1)^(0xedb88320&-(c&1));}return(c^0xffffffff)>>>0;}function block(n){const a=new Uint8Array(n);return[a,new DataView(a.buffer)];}
 for(const[name,str]of Object.entries(files)){const n=enc.encode(name),b=enc.encode(str),c=crc(b);const[h,v]=block(30+n.length);v.setUint32(0,0x04034b50,true);v.setUint16(4,20,true);v.setUint16(6,0x800,true);v.setUint16(12,0x21,true);v.setUint32(14,c,true);v.setUint32(18,b.length,true);v.setUint32(22,b.length,true);v.setUint16(26,n.length,true);h.set(n,30);parts.push(h,b);
 const[ch,cv]=block(46+n.length);cv.setUint32(0,0x02014b50,true);cv.setUint16(4,20,true);cv.setUint16(6,20,true);cv.setUint16(8,0x800,true);cv.setUint16(14,0x21,true);cv.setUint32(16,c,true);cv.setUint32(20,b.length,true);cv.setUint32(24,b.length,true);cv.setUint16(28,n.length,true);cv.setUint32(42,offset,true);ch.set(n,46);central.push(ch);offset+=h.length+b.length;}
 const size=central.reduce((s,x)=>s+x.length,0),[end,ev]=block(22);ev.setUint32(0,0x06054b50,true);ev.setUint16(8,central.length,true);ev.setUint16(10,central.length,true);ev.setUint32(12,size,true);ev.setUint32(16,offset,true);const all=[...parts,...central,end],out=new Uint8Array(all.reduce((s,a)=>s+a.length,0));let pos=0;all.forEach(a=>{out.set(a,pos);pos+=a.length;});return out;
}
return {VERSION,norm,clone,findConcepts,rankRepositories,learningRoute,alignment,threeNo,action,route,runLab,DEFAULTS,checkQuiz,validateProject,newProject,projectReadiness,makeManifest,projectMarkdown,scaffold,zipFiles};
});
