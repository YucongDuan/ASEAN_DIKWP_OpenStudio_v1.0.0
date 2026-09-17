"""Build the traceable offline learning corpus from the supplied report catalogue."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
def load(n):return json.loads((ROOT/'data'/n).read_text(encoding='utf-8'))
def save(n,d): (ROOT/'data'/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=load('mesh98_portfolio.json'); curated={x['name']:x for x in p['curated']}
areas=[('foundations','DIKWP与语义架构','DIKWP & semantics'),('consciousness','人工意识与数字生命','Consciousness & digital life'),('mathematics','语义数学与证明','Semantic mathematics & proofs'),('evidence','证据与测评','Evidence & evaluation'),('security','安全与韧性','Security & resilience'),('health','健康与照护','Health & care'),('education','教育与能力','Education & capability'),('economy','经济与价值','Economy & value'),('society','社会与基础设施','Society & infrastructure'),('physics','物理与宇宙','Physics & cosmos'),('memory','记忆与身份','Memory & identity'),('standards','标准与互操作','Standards & interoperability')]
markers=[('数学','mathematics'),('意识','consciousness'),('生命','consciousness'),('证据','evidence'),('治理','evidence'),('安全','security'),('正义','security'),('医学','health'),('健康','health'),('教育','education'),('能力','education'),('经济','economy'),('社会','society'),('文明','society'),('物理','physics'),('宇宙','physics'),('记忆','memory'),('身份','memory'),('标准','standards'),('互操作','standards')]
concepts={
 'purpose':['purpose','intent','目标','目的','意图','mục tiêu','ý định','tujuan','niat','เป้าหมาย','เจตนา','layunin','objetivo','objetivu','ရည်ရွယ်ချက်','គោលបំណង','ເປົ້າໝາຍ','நோக்கம்'],
 'education':['learn','education','student','campus','teaching','学习','学生','教育','教学','học','sinh viên','giáo dục','belajar','siswa','pendidikan','pelajar','นักเรียน','เรียนรู้','การศึกษา','ການສຶກສາ','ការអប់រំ','ပညာရေး','educação','edukasyon','edukasaun','pag-aaral','estudante','aprende','ပညာ','ការរៀន','ຮຽນ','கற்றல்'],
 'language':['language','translation','multilingual','语种','语言','翻译','跨境','ngôn ngữ','dịch','bahasa','terjemah','ภาษา','แปล','wika','tradução','lian','ဘာသာ','ភាសា','ພາສາ','மொழி'],
 'evidence':['evidence','audit','trace','verify','whitebox','white-box','证据','验证','白盒','可解释','bằng chứng','kiểm chứng','bukti','หลักฐาน','ตรวจสอบ','ebidensya','evidência','prova','အထောက်အထား','ភស្តុតាង','ຫຼັກຖານ','ஆதாரம்'],
 'mathematics':['math','proof','certificate','semanticmath','数学','证明','语义数学','toán','chứng minh','matematika','bukti formal','matematik','คณิตศาสตร์','matematika','matemática','သင်္ချာ','គណិតវិទ្យា','ຄະນິດສາດ','கணிதம்'],
 'health':['health','care','medicine','medical','健康','医学','照护','sức khỏe','y tế','kesehatan','perubatan','สุขภาพ','kalusugan','saúde','saude','ကျန်းမာရေး','សុខភាព','ສຸຂະພາບ','நலம்'],
 'economy':['economy','trade','commerce','demand','value','跨境电商','贸易','经济','需求','thương mại','kinh tế','perdagangan','ekonomi','การค้า','เศรษฐกิจ','kalakalan','comércio','ekonomia','ကုန်သွယ်','ពាណិជ្ជកម្ម','ການຄ້າ','வணிகம்'],
 'memory':['memory','identity','continuity','记忆','身份','连续性','trí nhớ','bộ nhớ','memori','ingatan','ความจำ','alaala','memória','memoria','မှတ်ဉာဏ်','ការចងចាំ','ຄວາມຈຳ','நினைவகம்'],
 'consciousness':['consciousness','cognition','life','意识','认知','生命','ý thức','nhận thức','kesadaran','kesedaran','สำนึก','kamalayan','consciência','konsiensia','အသိစိတ်','មនសិការ','ສະຕິ','உணர்வு'],
 'security':['security','safety','permission','gate','安全','权限','授权','an toàn','bảo mật','keamanan','keselamatan','ความปลอดภัย','seguridad','segurança','seguransa','လုံခြုံ','សុវត្ថិភាព','ຄວາມປອດໄພ','பாதுகாப்பு'],
 'industry':['industry','industrial','agriculture','robot','energy','transport','工业','农业','制造','机器人','能源','交通','nông nghiệp','công nghiệp','pertanian','industri','เกษตร','อุตสาหกรรม','agrikultura','agricultura','industria','စိုက်ပျိုး','កសិកម្ម','ກະສິກຳ','விவசாயம்'],
 'innovation':['innovation','create','triz','创新','创造','发明','đổi mới','sáng tạo','inovasi','นวัตกรรม','paglikha','inovação','inovasaun','ဆန်းသစ်','នវានុវត្តន៍','ນະວັດຕະກຳ','புதுமை']}
area_tags={'foundations':['purpose','language'],'consciousness':['consciousness','memory'],'mathematics':['mathematics','innovation'],'evidence':['evidence','security'],'security':['security','purpose'],'health':['health','evidence'],'education':['education','innovation'],'economy':['economy','purpose'],'society':['economy','language'],'physics':['mathematics','industry'],'memory':['memory','consciousness'],'standards':['evidence','language']}
featured_extra={
'DIKWP-PACT-v0.1.0':['purpose','evidence','security'], 'DIKWP-MESH-':['language','purpose','mathematics'],
'DIKWP-VERITYWEAVE-v2.0.0':['evidence','language','security'],
'DIKWP-Chinese-LearnLab-2026-V1':['language','education'], 'DIKWP-English-LearnLab-2026-V1':['language','education'],
'DIKWP-LLM-WhiteBox-EvalLab-V1':['evidence','education'], 'DIKWP-CLEARPATH-TRANSPARENT-ECONOMY':['economy','industry'],
'DIKWP-DEMANDPROOF-COMMONS':['economy','industry'], 'DIKWP-AgentTrace-OS':['evidence','purpose','memory']}
records=[]
for row in p['records']:
 name=row['name'];c=curated.get(name,{});text=(name+' '+row.get('description','')).lower()
 area=next((a for m,a in markers if m in row.get('category','')),'foundations')
 tags=set(area_tags[area])
 for tag,words in concepts.items():
  if any(w.lower() in text for w in words[:12]):tags.add(tag)
 tags.update(featured_extra.get(name,[]))
 lic=row.get('license','');spdx='Apache-2.0' if 'Apache' in lic else 'MIT' if lic=='MIT' else None
 records.append({'id':row['id'],'name':name,'url':row['url'],'area':area,'description':row.get('description',''),'license':spdx,'license_note':lic or 'Not recorded in source catalogue','tags':sorted(tags),'featured':bool(c),'role':c.get('role',''),'explore':c.get('explore',''),'work':c.get('work',''),'source':row.get('source',row['url']),'verification':'report_catalogue','difficulty':1 if ('learnlab' in text or name=='DIKWP-PACT-v0.1.0') else 2 if c else 3,'readme_check': '2026-09-16' if name=='DIKWP-PACT-v0.1.0' else None})
assert len(records)==len({r['name'] for r in records})==483
save('catalog.json',{'schema':'openstudio.catalog/1','snapshot_date':'2026-09-08','packaged':'2026-09-16','owner':'YucongDuan','scope':p['scope'],'official_directory':p['current_directory_source'],'areas':[{'id':a,'zh':z,'en':e} for a,z,e in areas],'repositories':records})
save('concepts.json',concepts)
# A lesson is a question, a worked example, a misconception, a practice, a quiz and a project bridge.
rows=[
('dikwp','五类语义资源，而非五级阶梯','Five semantic resources, not five rungs','Năm loại tài nguyên ngữ nghĩa, không phải năm bậc',[],['purpose','language'],[5,6,7],
'同一个“30”，怎样变成有意义的判断？','How can the same “30” become a meaningful decision?',
'把观测记录为D，把语境中的差异与关联组织为I，把可复用关系表达为K，把目标冲突下的权衡表达为W，把希望实现的变化及受益对象写成P。五类资源允许双向转换，而不是只向上爬升。',
'Represent observations as D, contextual differences as I, reusable relations as K, trade-offs as W, and the intended change and beneficiary as P. Resources can transform in multiple directions; they are not a one-way ladder.',
'D：教室传感器读数30 °C。I：比目标范围高4 °C。K：通风会影响温度与噪声。W：兼顾舒适、能耗与邻班安静。P：改善学习环境，而不是单纯把温度降到最低。',
'D: a classroom sensor reads 30 °C. I: this is 4 °C above the target range. K: ventilation affects temperature and noise. W: balance comfort, energy and nearby classes. P: improve learning conditions, not minimize temperature at any cost.',
'误区：把所有文本都称作知识，或认为P天然拥有执行权限。','Pitfall: calling every text knowledge, or treating a purpose as permission to act.',
'在作品工作室把自己的问题分别填进D/I/K/W/P，再修改P观察仓库推荐为何变化。','Describe your own problem in D/I/K/W/P in the studio; change P and examine why the project choices change.',
'哪一项最直接表达Purpose？','Which item expresses Purpose most directly?', ['传感器读数','一条转换规则','希望为谁实现什么变化'], ['A sensor reading','A transformation rule','The intended change and its beneficiary'],2,
'P明确期望与受益者，D和K提供支持而不能替用户决定目的。','P identifies an intended change and beneficiary. D and K support it rather than decide it for the person.', ['DIKWP-MESH-','DIKWP-PACT-v0.1.0']),
('context','语境、单位与跨语言意义','Context, units and cross-language meaning','Ngữ cảnh, đơn vị và ý nghĩa đa ngôn ngữ',['dikwp'],['language','evidence'],[60,65,66],
'翻译正确的句子为什么仍可能引起错误行动？','Why can an apparently correct translation still cause a wrong action?',
'将实体标识、单位、币种、数量、目标与任务角色分开保存。语言展示可以变化，关键语义槽位不应被默默修改。对未识别单位保留“待解释”，不要猜测为等价。',
'Keep entity identifiers, units, currency, quantities, goals and roles separate. Language presentation may change while critical semantic slots remain explicit. Unknown units remain unresolved instead of being guessed equivalent.',
'中方记录1000 kg，越方记录1 tonne，两者质量等价；1000 kg与1000 g不等价。人民币100与越南盾100也不等价，除非明确记录汇率与日期。',
'1000 kg and 1 tonne are equal in mass; 1000 kg and 1000 g are not. CNY 100 and VND 100 are not equivalent unless an explicit dated conversion is supplied.',
'误区：字面一致就是意义一致；用综合相似度抵消关键金额错误。','Pitfall: equating similar words with equivalent meaning or letting an average score hide a critical quantity error.',
'运行语义对齐实验，先测试单位等价，再改变币种、Purpose或实体标识。','Run the alignment lab; test equivalent units, then change currency, purpose or entity identity.',
'1000 kg与1 tonne应该如何处理？','How should 1000 kg and 1 tonne be treated?', ['总是冲突','按质量单位规范化后等价','只能靠字面匹配'],['Always conflicting','Equivalent after mass normalization','Only string matching can decide'],1,
'先检查维度，再做确定的单位转换；不要替换币种或实体。','Check dimension first, then apply the defined conversion without silently replacing currency or entity.', ['DIKWP-MESH-','DIKWP-Chinese-LearnLab-2026-V1','DIKWP-English-LearnLab-2026-V1']),
('three-no','3-No：不完备、不一致、不精确','3-No: incompleteness, inconsistency, imprecision','3-No: thiếu, mâu thuẫn và không chính xác',['dikwp'],['mathematics','evidence'],[8,9,36,37],
'面对缺失与矛盾，系统如何继续给出有用结果？','How can a system remain useful when records are missing or conflicting?',
'不完备是缺少必要信息，不一致是相互冲突的断言，不精确是区间或模糊边界。分别建模后，可以保留多个解释，定位最有价值的补充信息，并在条件明确的范围内继续计算。',
'Incompleteness means required information is missing; inconsistency means assertions conflict; imprecision means intervals or fuzzy boundaries. Model them separately to preserve alternatives, identify valuable missing information and compute conditional results.',
'两个冷链传感器分别报告[2,4]与[6,8] °C。区间不相交说明当前不能给出单一一致温度；若第二个未上报，则是缺失而不是冲突。',
'Two cold-chain sensors report [2,4] and [6,8] °C. Disjoint intervals do not support a single consistent temperature. An absent second report is missing information, not a contradiction.',
'误区：简单取平均值消除所有矛盾；给缺失数据补零。','Pitfall: averaging away every contradiction or replacing missing data with zero.',
'在3-No实验中改变区间、移除观测，比较简单均值基线与区间交集方法。','Change intervals and remove observations in the 3-No lab; compare a mean baseline with interval intersection.',
'观测缺失与观测冲突应该怎样处理？','How should missing and conflicting observations be handled?', ['都补零','分别记录原因与后续问题','都取平均'],['Fill both with zero','Record distinct reasons and follow-up questions','Average both'],1,
'不同原因要求不同信息补充，不能用同一种修补掩盖。','Different causes require different follow-up information.', ['DIKWP-SemanticMath-LearnLab-2026-V1','Complete-Information-Theoretic-Mathematics-Problem-to-Certificate-Compiler']),
('purpose','目的驱动：先回答为谁、为何','Purpose-driven design: for whom and why','Thiết kế theo mục đích: cho ai và vì sao',['dikwp'],['purpose','education'],[6,10,11],
'回答看似正确，为什么还可能偏离学生的真实问题？','How can a correct-looking answer still miss the student’s problem?',
'把任务目的写成可修改的契约：受益者、希望改变的状态、约束、成功证据与允许的操作。修改目的要记录版本，不把对目标的推测当成学生已经做出的选择。',
'Write purpose as a revisable contract: beneficiary, intended state change, constraints, evidence of success and permitted operations. Version changes; do not convert an inferred goal into a decision already made by the student.',
'学生想理解算法而不是获得作业答案。合适路径可能是解释、反例和可改实验，而不是直接输出最终代码。',
'A student wants to understand an algorithm, not receive a finished answer. An appropriate route may provide explanations, counterexamples and an editable experiment instead of only final code.',
'误区：最大化某个分数就等于实现人的目的。','Pitfall: maximizing a single score is not identical to realizing a person’s purpose.',
'建立一个校园问题的目的卡，再对比“学懂”和“尽快给结果”两种目的。','Create a campus purpose card and contrast understanding with fastest completion.',
'谁有权修订学生自己的实质目标？','Who should revise the student’s substantive goal?', ['系统自动替换','学生本人，或有明确范围的授权者','仓库热度排行榜'],['The system silently','The student or an explicitly authorized party','A repository popularity ranking'],1,
'系统应帮助澄清与比较，不擅自替换本人选择。','The system supports clarification and comparison without silently replacing the person’s choice.', ['DIKWP-PACT-v0.1.0','DIKWP-LearnPath-OS']),
('pact','PACT：把目的放进行为轨迹','PACT: connect purpose to action traces','PACT: liên kết mục đích với dấu vết hành động',['purpose'],['security','evidence','purpose'],[54,75],
'怎样看见智能体在哪一步偏离任务？','How can we locate the step at which an agent deviates?',
'保留目的契约、输入证据、计划动作、实际动作与结果。逐步检查Purpose是否保留、操作是否被允许、证据是否支持结论。教学实验同时报告误放行与误阻断，避免只追求拒绝更多。',
'Keep the purpose contract, evidence, proposed actions, actual actions and outcomes. Check purpose preservation, permission and evidence step by step. Report both false acceptance and false blocking instead of treating more refusals as better.',
'允许整理跨境商品资料，不意味着允许代替商家发送报价。系统可继续生成草稿，同时把发送动作单独交给有权者。',
'Permission to organize cross-border product data does not imply permission to send an offer. The system can still prepare a draft while leaving transmission to an authorized person.',
'误区：把研究基准的规则成绩直接写成真实模型性能。','Pitfall: treating rule-based benchmark scores as real-model performance.',
'运行行动实验：保持目的与证据不变，只改变allow_send，比较基线与条件检查。','Run the action lab; keep purpose and evidence fixed and vary allow_send.',
'不能发送时，仍可提供什么？','What useful work can continue when sending is not permitted?', ['什么也不做','生成供本人检查的草稿','绕过权限发送'],['Nothing','Prepare a draft for review','Bypass permission and send'],1,
'把操作分开，既保留帮助又尊重实质选择。','Separating actions preserves useful assistance and substantive choice.', ['DIKWP-PACT-v0.1.0','DIKWP-AgentTrace-OS']),
('evidence','证据、来源与白盒解释','Evidence, provenance and white-box explanation','Bằng chứng, nguồn gốc và giải thích hộp trắng',['dikwp'],['evidence','language'],[13,14,55],
'十个转载页面是否等于十份独立证据？','Do ten copied pages provide ten independent sources?',
'把来源、观察、推断和结论分别记录。为转载内容保留相同来源簇，支持与反驳分别展示。一个判断需要能回到具体输入与规则，而不是只显示总分。',
'Separate sources, observations, inferences and conclusions. Group republications by origin and display support and counterevidence separately. A judgment should be traceable to specific inputs and rules, not only a total score.',
'某篇论文被三个新闻页面转载，仍然主要来自同一研究。另一独立实验复现成功，则增加不同类型的证据。',
'Three news pages repeating one paper still share a research origin. An independent successful replication adds a different kind of evidence.',
'误区：把来源数量、机构名气与证据独立性混成同一指标。','Pitfall: conflating source count, institutional reputation and independence.',
'在作品中写下继承主张、证据来源与尚待比较的反例；把每次实验结果保存在版本中。','Record an inherited claim, sources and counterexamples to investigate. Save each experiment with its input version.',
'三篇转载同一研究的文章应该怎样计数？','How should three republications of one study be represented?', ['三个独立实验','同源传播，保留三个入口和一个来源簇','没有任何价值'],['Three independent experiments','Three dissemination links, one origin group','No value'],1,
'传播价值可以充分展示；证据独立性另行判断。','Dissemination can be valuable while independence is assessed separately.', ['DIKWP-VERITYWEAVE-v2.0.0','DIKWP-LLM-WhiteBox-EvalLab-V1']),
('triz','DIKWP-TRIZ：把矛盾变成创新入口','DIKWP-TRIZ: turn contradictions into design questions','DIKWP-TRIZ: biến mâu thuẫn thành câu hỏi thiết kế',['three-no','purpose'],['innovation','mathematics'],[9,57,93],
'提高准确性却增加成本，应该只选一边吗？','Must improving accuracy at higher cost be a simple either-or?',
'先明确谁的目的、哪种资源与哪一条关系发生冲突，再构造多条可比较路径：分离条件、改变表示、改变阶段或重新组合资源。候选方案应形成可以被反例检验的假设。',
'Identify whose purpose conflicts, which resources are involved and which relation causes the trade-off. Compare routes such as separating conditions, changing representation, separating stages or recombining resources. Turn each candidate into a testable hypothesis.',
'跨语种商品核验既要快又要可靠：先做轻量单位与实体检查，将歧义项交给人工，而不是对所有条目使用同等复杂处理。',
'Cross-language product checks must be fast and reliable: run lightweight unit and entity checks first, then route ambiguous cases to people rather than treating every item with equal complexity.',
'误区：列出创意名称就等于创新被证明。','Pitfall: listing attractive ideas does not establish an improvement.',
'在工作室填写继承部分、改变部分与反例；使用实验对照支撑你的设计选择。','Document inherited and changed parts plus counterexamples in the studio; support your choice with a comparison.',
'怎样让创新主张更可检验？','How can an innovation claim become testable?', ['只换名字','保留基线、明确改变、比较结果','只增加功能数量'],['Rename it','Preserve a baseline, specify the change and compare outcomes','Only add more features'],1,
'创新需要说明变化产生了什么差异，而不是只说明做了修改。','An innovation claim should explain what difference the change makes.', ['DIKWP-HumanInnovation-Studio-OS','DIKWP-University-Innovation-Studio-V1']),
('repo','仓库选择：问题优先，热度次之','Repository choice: problem fit before popularity','Chọn kho mã: phù hợp vấn đề trước độ phổ biến',['purpose'],['education','innovation'],[52,53,54,58],
'483个入口，怎样选出适合我的组合？','How can I choose an appropriate combination from 483 entries?',
'先写问题、可用数据、预期输出、能力基础与计算条件。比较仓库的作用、输入输出、运行方式、许可与待补工作。推荐分是透明的匹配提示，不是对仓库科学价值的排名。',
'Describe the problem, available data, expected output, prior skills and computing constraints. Compare roles, inputs and outputs, execution requirements, licensing and adaptation needs. Recommendation scores express transparent fit, not scientific merit.',
'跨语言任务可能组合MESH²的语义组织、PACT的目的检查和VerityWeave的来源结构；这是一份组合设计，接口仍要由作品明确。',
'A cross-language task may combine MESH² semantic organization, PACT purpose checks and VerityWeave provenance structures. This is a design proposal whose interfaces must be specified in the project.',
'误区：看到项目名就认定已经可以直接拼接。','Pitfall: assuming project names imply plug-and-play compatibility.',
'用母语描述问题，比较三个候选仓库并写出选择理由。','Describe a problem in your language, compare three repositories and record why you chose them.',
'推荐分代表什么？','What does a recommendation score represent?', ['科学贡献排名','当前问题与目录标签的匹配','商业成功概率'],['A scientific contribution ranking','Fit between the current problem and catalogue tags','Probability of commercial success'],1,
'分数帮助选择，应结合源码和任务条件判断。','A score supports selection and must be interpreted with source code and task constraints.', ['RepoProof-OS','DIKWP-LearnPath-OS']),
('inherit','继承：版本、署名与可重建输入','Inheritance: versions, credit and reproducible inputs','Kế thừa: phiên bản, ghi công và đầu vào tái tạo',['repo','evidence'],['evidence','innovation'],[58,59,98],
'怎样让别人知道我继承了什么，而不是只有一个链接？','How can another researcher know exactly what I inherited?',
'记录仓库URL、提交SHA、许可证、取得日期、文件散列和本地修改说明。上游代码与自己的新代码分开保存，保留来源文件。每次比较使用同一输入，并导出可重建的作品包。',
'Record repository URL, commit SHA, license, retrieval date, file hashes and local modifications. Keep upstream and new code distinct and preserve notices. Use identical inputs for comparisons and export a reproducible project package.',
'使用main作为阅读入口方便，但实验引用应锁定提交；同一仓库的不同版本可能改变行为。',
'The main branch is convenient for browsing, but an experiment should pin a commit because different revisions can behave differently.',
'误区：平台的许可证可以覆盖所有外部仓库。','Pitfall: a platform license does not replace the licenses of external repositories.',
'导出作品包，运行upstream工具锁定选定仓库；之后再审读源码、安装依赖并执行其原有测试。','Export a project and use the upstream tool to pin a selected repository. Review its source, dependencies and original tests before execution.',
'哪一种标识更适合可重现实验？','Which identifier is appropriate for a reproducible experiment?', ['可变main分支','固定提交SHA并保留输入','网页访问量'],['A moving main branch','An immutable commit SHA with recorded inputs','Page views'],1,
'固定版本与输入，使后续差异可以归因。','Fixed versions and inputs make later differences interpretable.', ['RepoProof-OS','DIKWP-AgentTrace-OS']),
('evaluate','比较、消融与反例','Comparisons, ablations and counterexamples','So sánh, loại bỏ thành phần và phản ví dụ',['inherit','three-no'],['evidence','innovation'],[73,76,98],
'系统变复杂了，怎样知道增加的机制真的有帮助？','How can we tell whether an added mechanism helps?',
'保留简单基线，使用相同样本与指标。一次移除一个机制进行消融，分析成功与失败案例。小型合成实验用于理解机制，不自动推导到真实业务效果。',
'Preserve a simple baseline with the same examples and metrics. Remove one mechanism at a time for ablations and inspect successes and failures. Small synthetic experiments explain mechanisms without automatically establishing real-world outcomes.',
'语义对齐中去掉单位规范化，会把1000 kg与1 tonne误判不一致；去掉币种检查，则可能把不同币种错判等价。',
'Removing unit normalization falsely rejects 1000 kg versus 1 tonne; removing currency checks may falsely accept amounts in different currencies.',
'误区：只展示最好的一次结果或不断调整测试集追求满分。','Pitfall: reporting only the best run or repeatedly editing the test set to achieve a perfect score.',
'在实验室保留基线、改进与消融三组输出，写出一个改进仍然失败的情况。','Keep baseline, revised and ablated outputs, and describe a case in which the revision still fails.',
'消融实验应该优先怎样做？','How should an ablation be designed?', ['同时改变所有组件','一次移除一个机制并保持输入','删除失败样本'],['Change every component','Remove one mechanism while holding inputs fixed','Delete failed examples'],1,
'控制变化范围才能解释结果差异。','Controlled changes make differences interpretable.', ['DIKWP-LLM-WhiteBox-EvalLab-V1','Open-Research-Benchmark-Impact-and-Translation-OS']),
('consciousness','人工意识：从理论到可操作问题','Artificial consciousness: from theory to operational questions','Ý thức nhân tạo: từ lý thuyết đến câu hỏi thao tác',['evidence','purpose'],['consciousness','memory'],[10,11,38,94],
'怎样研究记忆、目的与身份连续性，而不是只争论标签？','How can memory, purpose and identity continuity be studied beyond labels?',
'把宏观理论转为可观察任务：记忆更新是否保留来源，目的改变是否能解释，冲突是否被记录，自我描述是否与行为一致。把行为指标与主观体验主张分开，允许不同理论给出不同预测。',
'Translate broad theories into observable tasks: provenance-preserving memory updates, explainable purpose changes, recorded conflicts and consistency between self-description and behavior. Distinguish operational measures from claims of subjective experience and compare theoretical predictions.',
'代理在两次对话中保持同一项目目的，但能根据新增证据修订结论。这是连续性与修订能力的研究对象。',
'An agent preserves a project purpose across conversations while revising a conclusion based on new evidence. This provides a task for studying continuity and revision.',
'误区：一个高指标就证明了主观意识。','Pitfall: a high operational measure alone does not prove subjective consciousness.',
'用作品版本历史记录目的、记忆与证据的变化，构造“应保持”和“应修订”两类任务。','Use project history to record purpose, memory and evidence changes; construct both preservation and revision tasks.',
'什么是可操作研究问题？','Which is an operational research question?', ['仅凭名称宣称有意识','在证据变化后能否解释目的保持与结论修订','只比较界面外观'],['Declare consciousness from a name','Explain purpose preservation and conclusion revision after new evidence','Only compare visual appearance'],1,
'明确输入、输出与区分证据，让理论能够进入实验。','Explicit inputs, outputs and discriminating evidence let theories enter experiments.', ['DIKWP-Consciousness-Futures-Studio-V1','DIKWP-Consciousness-Science-Lab-V1','DIKWP-AGI-Continuity-Ark-OS']),
('create','从学习者到贡献者','From learner to contributor','Từ người học đến người đóng góp',['evaluate','triz'],['innovation','education'],[97,98,99,100],
'解决自己的问题，怎样同时帮助后来者？','How can solving my own problem help future learners?',
'将作品组织为问题、继承、改动、结果、局限与下一问题。贡献不必只是一篇论文：一个可复现反例、一组高质量双语术语、一个更清晰的教程或一个修复都能使研究生态进步。',
'Organize a contribution as problem, inheritance, change, results, limitations and the next question. A reproducible counterexample, bilingual terminology set, clearer tutorial or repair can advance the research ecosystem alongside papers.',
'一名学生发现越南语商品记录中单位歧义，增加了带语境的对齐规则与失败测试，并保留原始例子和贡献署名。',
'A student finds unit ambiguity in Vietnamese product records, adds a contextual alignment rule and a failing test, and preserves the original example and contributor credit.',
'误区：只有完全推翻前人或规模巨大才算有价值。','Pitfall: a contribution is valuable only when it overturns prior work or is very large.',
'导出作品与贡献说明，邀请教师基于理解、选择、继承、验证与创新逐项反馈。','Export the project and contribution note; invite feedback on understanding, choice, inheritance, validation and innovation.',
'下面哪一种可以成为有价值的贡献？','Which can be a valuable contribution?', ['带输入与复现步骤的反例','只修改项目名称','隐藏所有来源'],['A counterexample with inputs and reproduction steps','Only renaming a project','Hiding all sources'],0,
'可复现、可理解、可继续使用的增量同样重要。','Reproducible, understandable and reusable increments matter.', ['WorkProof-Campus-OS-v1.0.0','DIKWP-University-Innovation-Studio-V1'])]
lessons=[]
for row in rows:
 (id,z,en,vi,pre,tags,slides,qz,qe,bz,be,ez,ee,mz,me,pz,pe,qzz,qee,oz,oe,answer,rz,rex,repos)=row
 lessons.append({'id':id,'title':{'zh':z,'en':en,'vi':vi},'prerequisites':pre,'tags':tags,'slides':slides,'question':{'zh':qz,'en':qe},'body':{'zh':bz,'en':be},'example':{'zh':ez,'en':ee},'misconception':{'zh':mz,'en':me},'practice':{'zh':pz,'en':pe},'quiz':{'question':{'zh':qzz,'en':qee},'options':{'zh':oz,'en':oe},'answer':answer,'explanation':{'zh':rz,'en':rex}},'repositories':repos})
save('lessons.json',lessons)
scenarios=[
 {'id':'trade','title':{'zh':'中越跨境商品语义核验','en':'Cross-border product meaning checks','vi':'Kiểm tra ngữ nghĩa hàng hóa xuyên biên giới'},'problem':{'zh':'比较中文和越南语商品资料中的重量、币种、实体与交易目的，发现误解并保留证据。','en':'Compare quantities, currency, entity identity and purpose in Chinese and Vietnamese product records.','vi':'So sánh khối lượng, tiền tệ, định danh và mục đích trong hồ sơ sản phẩm tiếng Trung và tiếng Việt.'},'tags':['language','evidence','economy','purpose'],'lab':'alignment','repos':['DIKWP-MESH-','DIKWP-PACT-v0.1.0','DIKWP-VERITYWEAVE-v2.0.0']},
 {'id':'learning','title':{'zh':'能解释选择理由的学习伙伴','en':'A learning partner that explains choices','vi':'Bạn học giải thích lựa chọn'},'problem':{'zh':'帮助不同语言背景的学生理解DIKWP并选择匹配基础与目标的学习资源。','en':'Help students with different language backgrounds understand DIKWP and choose resources that match their goals.','vi':'Giúp sinh viên nhiều ngôn ngữ hiểu DIKWP và chọn tài nguyên phù hợp mục tiêu.'},'tags':['education','purpose','language'],'lab':'purpose','repos':['DIKWP-LearnPath-OS','EduWeave-Global-Personalized-Education-OS','DIKWP-Algorithm-LearnLab-V1']},
 {'id':'coldchain','title':{'zh':'农业冷链的3-No观测分析','en':'3-No analysis of agricultural cold chains','vi':'Phân tích 3-No trong chuỗi lạnh nông sản'},'problem':{'zh':'在温度观测缺失、区间不精确或多传感器冲突时，解释可以判断什么、还需补充什么。','en':'Explain what can be concluded when temperature observations are missing, interval-valued or inconsistent.','vi':'Giải thích kết luận khi nhiệt độ bị thiếu, theo khoảng hoặc mâu thuẫn.'},'tags':['industry','evidence','mathematics'],'lab':'three-no','repos':['DIKWP-MESH-','DIKWP-SemanticMath-LearnLab-2026-V1','DIKWP-VERITYWEAVE-v2.0.0']},
 {'id':'agent','title':{'zh':'校园智能体：有帮助，也有目的','en':'Campus agents: helpful and purpose-aware','vi':'Tác tử trong trường: hữu ích và có mục đích'},'problem':{'zh':'智能体能够整理资料并生成草稿，发送与公开发布须符合本人所给范围。','en':'An agent organizes information and prepares drafts while respecting the stated scope for sending and publishing.','vi':'Tác tử sắp xếp tài liệu, tạo bản nháp và tôn trọng phạm vi gửi hoặc công bố.'},'tags':['purpose','evidence','security'],'lab':'action','repos':['DIKWP-PACT-v0.1.0','DIKWP-AgentTrace-OS']},
 {'id':'math','title':{'zh':'语义数学与可检验的创新假设','en':'Semantic mathematics and testable innovation','vi':'Toán học ngữ nghĩa và giả thuyết đổi mới'},'problem':{'zh':'把不完备、不一致、不精确分开建模，用反例与对照评价新的处理方法。','en':'Model incompleteness, inconsistency and imprecision separately and evaluate changes with controlled comparisons.','vi':'Mô hình hóa sự thiếu, mâu thuẫn và không chính xác rồi đánh giá bằng so sánh.'},'tags':['mathematics','innovation','evidence'],'lab':'three-no','repos':['DIKWP-SemanticMath-LearnLab-2026-V1','Complete-Information-Theoretic-Mathematics-Problem-to-Certificate-Compiler']},
 {'id':'memory','title':{'zh':'长期研究伙伴的记忆与修订','en':'Memory and revision in a research companion','vi':'Trí nhớ và sửa đổi của bạn đồng hành nghiên cứu'},'problem':{'zh':'研究伙伴保留项目目的和证据来源，又能对新证据解释性地修订结论。','en':'A research companion preserves project purpose and sources while explaining revisions prompted by new evidence.','vi':'Bạn đồng hành giữ mục đích và nguồn trong khi giải thích sửa đổi theo bằng chứng mới.'},'tags':['memory','consciousness','purpose','evidence'],'lab':'purpose','repos':['DIKWP-AGI-Continuity-Ark-OS','DIKWP-Consciousness-Futures-Studio-V1']}
]
save('scenarios.json',scenarios)
sources=load('mesh98_sources.json')
sources += [ {'id':'OS01','title':'DIKWP-PACT current README and reproduction interface','url':'https://github.com/YucongDuan/DIKWP-PACT-v0.1.0/blob/main/README.md','kind':'作者仓库原文','checked':'2026-09-16','status':'本次GitHub连接器读取','position':'Purpose contract, trace, standard-library runtime and reproduce command'}, {'id':'OS02','title':'Guangxi AI Institute: Vietnam education and industrial exchange','url':'https://www.guet.edu.cn/2026/0522/c6357a154010/page.htm','kind':'学院官方记录','date':'2026-05-22','checked':'2026-09-16'}, {'id':'OS03','title':'GitHub REST repository contents and immutable ref support','url':'https://docs.github.com/en/rest/repos/contents','kind':'官方技术文档','checked':'2026-09-16'}]
save('sources.json',sources)
save('research.json',{'books':load('mesh98_books.json'),'articles':load('mesh98_articles.json'),'conferences':load('mesh98_conferences.json'),'network':load('mesh98_network.json')})
print('Built',len(records),'repositories;',len(lessons),'lessons;',len(sources),'source records')
