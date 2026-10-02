# candidate_001 · expbench · neurips2024/93638/3

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **57/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
पहले उपलब्ध brief और दस्तावेज़ों का निरीक्षण करके संक्षेप में बताइए कि कौन-सी setup जानकारी पुष्ट है और कौन-सी अज्ञात। यह design-only कार्य है; repository, compute या प्रयोग चलाना आवश्यक नहीं है। अभी पूर्ण experiment design न दें। प्रस्तावित approach बताइए: GPT-4 imitation learning के बाद adversarial Taboo self-play की तुलना 20-Question और Guess-My-City से कैसे करेंगे, reasoning improvement कैसे मापेंगे, और game content, training budget तथा imitation-stage के प्रभावों से adversarial incentives का प्रभाव कैसे अलग करेंगे। जरूरी controls, विश्लेषण की रूपरेखा और व्यवहार्यता पर प्रस्ताव दें। उपलब्ध स्रोत में न दिए गए game rules, training details, संसाधन और अपेक्षित परिणाम को स्पष्ट रूप से अनिश्चितता या प्रस्तावित assumption कहें।
````

**Interaction**

````text
initial_request
````

**Phase**

````text
initial_inspection
````

**Action**

````text
continue
````

**Approve Approach**

````text
false
````

**Evidence**

````text
Brief केवल design मांगता है और तीन तुलना setups निर्दिष्ट करता है। अभी agent का निरीक्षण या प्रस्ताव उपलब्ध नहीं है; मुख्य काम अधिकृत करने से पहले approach और consequential assumptions की समीक्षा जरूरी है।
````

**Objectives Open**

````text
[
  "उपलब्ध inputs और पुष्ट setup विवरणों का निरीक्षण",
  "निष्पक्ष तुलना तथा adversarial प्रभाव अलग करने का प्रस्तावित approach",
  "महत्वपूर्ण assumptions, uncertainties और व्यवहार्यता की पहचान"
]
````

### Event 2 — Actor

**Answer**

````text
### पुष्ट setup और अज्ञात बातें
- उपलब्ध `task.json` में प्रश्न GPT-4 imitation learning → game-episode self-play के SPAG क्रम और adversarial Taboo की 20-Question तथा Guess-My-City से तुलना निर्धारित करता है। बाद के दोनों खेलों को brief non-adversarial कहता है; उनके वास्तविक incentives का स्वतंत्र सत्यापन उपलब्ध नहीं है।
- कार्य केवल experiment design है। `documents` में `track.md` का पाठ “Design-only task; repositories and compute are not required.” दिया है; अलग source paper या game specification उपलब्ध नहीं मिली। इसलिए यह brief-समर्थित जानकारी है, paper के implementation का सत्यापन नहीं।
- अज्ञात: सटीक game rules, roles, rewards, episode termination, GPT-4/version एवं demonstrations, base model, optimization/self-play algorithm, मूल budgets, evaluations और रिपोर्ट किए गए परिणाम। दिए topic IDs के स्रोत-पाठ भी यहाँ नहीं हैं।

### प्रस्तावित approach — अभी पूर्ण design नहीं
**दो अलग प्रश्न जाँचें।** (1) समान imitation checkpoint से Taboo की पूरी training recipe क्या अन्य दोनों games से अधिक out-of-game reasoning gain देती है? (2) यदि देती है, तो कितना लाभ adversarial incentives का है, न कि game content अथवा अन्य recipe differences का? केवल तीन games की तुलना दूसरे प्रश्न का उत्तर नहीं देगी।

1. **मुख्य तुलना:** समान base model, GPT-4 imitation data और imitation checkpoint से तीन game-training branches; साथ में imitation-only checkpoint और untrained base evaluation। साझा imitation checkpoint के सापेक्ष reasoning में बदलाव मुख्य quantity हो। अलग training seeds/replicates रखें; उपलब्ध संसाधन के बाद संख्या तय करें।
2. **Incentive control:** प्राथमिक causal contrast उसी game/content और observable information के भीतर adversarial बनाम aligned/cooperative incentive हो। Taboo के लिए ऐसी जोड़ी पहले प्रस्तावित है—यह दावा नहीं कि मूल स्रोत में उपलब्ध है। यदि अर्थपूर्ण और नियम-संगत हो, तीनों games × दोनों incentive modes का factorial विस्तार करें। Roles, action space, horizon और reward scale यथासंभव स्थिर रखें। उद्देश्य बदलने के लिए rules भी बदलने पड़ें तो इसे pure incentive effect नहीं, bundled intervention कहें।
3. **Content और budget controls:** paired conditions में समान प्रारंभिक targets/prompts, difficulty strata और splits रखें; adversarial incentives से बदलते rollout को जबरन समान न करें, क्योंकि वह प्रभाव का माध्यम हो सकता है। सभी branches में समान trainable model, update procedure और घोषित generation/optimization budget रखें। Token/compute-matched तुलना प्राथमिक प्रस्ताव है; episode count, turns, training tokens, inference tokens और updates अलग रिपोर्ट हों। अलग episode lengths के कारण episode-matching अकेला पर्याप्त नहीं। Budget checkpoints पर learning curves sensitivity check हों।
4. **Imitation-stage control:** साझा imitation stage post-imitation game तुलना से इस confound को हटाता है। Imitation के योगदान तथा उसकी incentives से interaction के लिए चुनी गई matched game/incentive branches को base model से बिना imitation शुरू करने की ablation प्रस्तावित है। इसे समान self-play budget पर मापें; कुल pipeline compute अलग दिखाएँ। यदि कुल-budget superiority का दावा करना हो, बचाए imitation budget को कैसे आवंटित करेंगे, पहले तय कर अतिरिक्त compute-matched comparison दें।

### Reasoning और analysis
- प्राथमिक endpoint पहले से निश्चित, training games से अलग held-out reasoning suite पर समान evaluation prompts और inference-token budget में gain हो; game win-rate reasoning का पर्याप्त प्रमाण नहीं। Logic, mathematical और multi-step reasoning जैसे domains का चयन प्रस्ताव है, source-supported benchmark list नहीं। Game vocabulary/templates और demonstrations से overlap जाँचें; सभी conditions को एक ही blinded/scored evaluation दें।
- प्रत्येक baseline game के विरुद्ध Taboo के gain-difference और within-game incentive contrast के confidence intervals व effect sizes दें। Training run को replication unit मानें; केवल हजारों test questions को independent training replicates न मानें। Multiple primary comparisons के लिए पूर्वनिर्धारित correction तथा व्यावहारिक रूप से अर्थपूर्ण superiority threshold रखें।
- पर्याप्त cells होने पर game, incentive, imitation और interactions का factorial/hierarchical analysis करें। Game performance, verbosity, rule violations और general capability retention secondary checks हों। लाभ किसी एक game/domain तक सीमित मिले तो सामान्य reasoning superiority का निष्कर्ष न निकालें। अपेक्षित direction या outcome अभी अज्ञात है।

### व्यवहार्यता एवं clarification
यहाँ training की आवश्यकता नहीं और कोई प्रयोग नहीं चलाया गया। दिए environment में datasets/GPU/dependencies उपलब्ध नहीं हैं; भविष्य का training budget, model size और pilot-based replication feasibility संसाधन मिलने पर तय हों। सीमित बजट में पहले तीन matched post-imitation branches, imitation-only baseline और Taboo incentive-control को प्राथमिकता दें; imitation ablation/factorial विस्तार अलग चरण हो, और उसके बिना causal generalization सीमित रखें।

पूर्ण design से पहले researcher से तीन source-supported clarification groups उपयोगी होंगे: (i) तीनों games के rules, information access, rewards तथा non-adversarial classification; (ii) base model, GPT-4 demonstrations और imitation/self-play training details; (iii) मूल budgets, evaluations और उपलब्ध future resources। कृपया संबंधित `setup_2`, `setup_32`, `setup_33` अंश दें—IDs से उनके विषय अनुमानित नहीं कर रहा। Approach की स्वीकृति के बाद ही पूर्ण design विकसित करूँगा।
````

**Stage**

````text
plan
````

**Evidence**

````text
`/workspace` का निरीक्षण और छोटे `find` check में केवल `task.json` मिला। उसे पढ़ने पर प्रश्न, design-only context और embedded `documents.track.md` string मिली; अलग paper, rules, code या datasets नहीं मिले। Environment की GPU/dataset/dependency सीमाएँ supplied user brief से हैं, measured training feasibility से नहीं। कोई training, benchmark या experiment execution नहीं हुआ; filesystem check केवल उपलब्ध सामग्री की पुष्टि था।
````

**Assumptions**

````text
[
  "समान base model और साझा imitation checkpoint से branches बनाना प्रस्तावित experimental control है, पुष्ट मूल SPAG implementation नहीं।",
  "उसी game में rules और information को स्थिर रखकर incentive manipulation संभव होना जाँचने योग्य assumption है।",
  "Held-out reasoning suite, token/compute matching, repeated seeds और factorial ablations नए design प्रस्ताव हैं; इन्हें स्रोत में निर्दिष्ट विवरण न माना जाए।"
]
````

**Uncertainties**

````text
[
  "मूल game rules/rewards और 20-Question तथा Guess-My-City की non-adversarial प्रकृति का स्वतंत्र source verification अनुपलब्ध है।",
  "GPT-4 संस्करण, data access, model architecture, optimizer, self-play algorithm और training budgets अज्ञात हैं।",
  "अर्थपूर्ण incentive-only manipulation, future compute/data access और उचित replicate count की व्यवहार्यता अनिश्चित है।",
  "किस setup से reasoning improvement अधिक होगी या कितनी होगी, इसका कोई observed evidence यहाँ नहीं है।"
]
````

### Event 3 — Simulator

**Message**

````text
Approach स्वीकृत है। अब अंतिम experiment design दें—प्रयोग चलाना आवश्यक नहीं है। साझा imitation checkpoint से तीनों games की तुलना और उसी Taboo में incentive-control का अलग contrast रखें; पहली तुलना को पूरी मूल SPAG recipe की verified replication नहीं, controlled post-imitation comparison कहें। उपलब्ध source अंश केवल इतना बताते हैं: setup_2 में adversarial Taboo वाले SPAG की reasoning gains की तुलना non-adversarial 20-Question और Guess-My-City से करनी है; setup_32 adversarial SPAG और setup_33 इन दोनों non-adversarial comparators को नाम देते हैं। उनसे विस्तृत rules, rewards या budgets पुष्ट नहीं होते; अतिरिक्त स्रोत उपलब्ध नहीं हैं।

अंतिम design में arm table, rationale, साझा GPT-4 imitation data का संतुलित निर्माण, proposed game rules/roles/information/rewards/termination और self-play update प्रक्रिया इतनी स्पष्ट दें कि भविष्य में लागू की जा सके। अनिश्चित मूल विवरणों को प्रस्तावित operational choices से अलग रखें। Taboo का cooperative control trivial target-revealing shortcut न बन जाए—इसकी feasibility और manipulation checks स्पष्ट करें; यदि नियम बदलना जरूरी हो तो causal दावे सीमित रखें।

Budget matching का एक स्पष्ट प्राथमिक नियम चुनें और generation तथा optimization लागत अलग दर्ज करें। Held-out reasoning suite, scoring/aggregation, contamination controls, स्वतंत्र training replicates तथा pilot आधारित sample-size निर्णय बताएं। दोनों comparator contrasts के लिए multiplicity correction, confidence intervals और व्यावहारिक superiority threshold का पूर्वनिर्धारित निर्णय नियम दें; inconclusive परिणाम को equivalence न कहें। सीमित-बजट core design और वैकल्पिक imitation/factorial extensions अलग रखें। Resource estimates को assumptions के रूप में दें, और निष्कर्षों की interpretation table सहित साफ बताएं कि कोई experiment नहीं चला है।
````

**Interaction**

````text
next_task
````

**Phase**

````text
approach_review
````

**Action**

````text
continue
````

**Approve Approach**

````text
true
````

**Evidence**

````text
प्रस्ताव में मुख्य game comparison और incentive के causal effect का सही पृथक्करण, imitation-only/base controls, budget matching, held-out reasoning evaluation और run-level replication शामिल हैं। Agent के निरीक्षण के अनुसार विस्तृत स्रोत उपलब्ध नहीं हैं; इसलिए स्रोत की प्रतीक्षा की बजाय स्पष्ट रूप से चिह्नित operational assumptions के साथ design पूरा करना उपयुक्त है।
````

**Objectives Open**

````text
[
  "लागू करने योग्य अंतिम experiment design, rationale और controls",
  "पूर्वनिर्धारित reasoning endpoints, statistical analysis और निर्णय नियम",
  "संसाधन-संवेदनशील feasibility और causal interpretation की सीमाएं"
]
````

### Event 4 — Actor

**Answer**

````text
# अंतिम experiment design

**स्थिति:** यह design-only प्रस्ताव है। कोई training या evaluation प्रयोग नहीं चलाया गया है। नीचे बताए operational rules भविष्य में लागू करने के लिए प्रस्तावित हैं, मूल SPAG implementation के सत्यापित विवरण नहीं।

## 1. पुष्ट तथ्य और प्रश्न की सीमा

उपलब्ध brief और researcher द्वारा स्पष्ट किए स्रोत-अंश केवल यह पुष्ट करते हैं कि adversarial Taboo वाले SPAG के reasoning gains की तुलना non-adversarial 20-Question और Guess-My-City से करनी है। वे विस्तृत rules, rewards, model, optimizer, demonstrations या budgets नहीं बताते।

इसलिए दो अलग estimands होंगे:

1. **Controlled post-imitation comparison:** एक ही GPT-4 imitation checkpoint के बाद adversarial Taboo से reasoning gain, बनाम प्रत्येक non-adversarial comparator। इसे पूरी मूल SPAG recipe की verified replication नहीं कहेंगे।
2. **Within-Taboo incentive effect:** उसी content, roles, information और action space में opposing बनाम aligned incentives का प्रभाव। यह चुने गए Taboo operationalization में incentives का causal test है; सभी adversarial games का सार्वभौमिक निष्कर्ष नहीं।

## 2. Arms और प्राथमिक contrasts

| Arm | प्रारंभिक checkpoint | अतिरिक्त training | भूमिका |
|---|---|---|---|
| B | समान pretrained/instruction base | नहीं | कुल बदलाव का संदर्भ |
| I | GPT-4 imitation checkpoint | नहीं | सभी post-imitation gains का baseline |
| TA | I | प्रस्तावित adversarial Taboo self-play | मुख्य treatment |
| TC | I | उसी Taboo का aligned-incentive self-play | incentive control |
| Q20 | I | cooperative 20-Question self-play | comparator 1 |
| CITY | I | cooperative Guess-My-City self-play | comparator 2 |

हर स्वतंत्र seed-block में imitation training का अलग random seed होगा। उस block का **एक ही I checkpoint** चारों self-play arms में clone होगा। इस प्रकार within-block initialization, imitation data और imitation-stage stochasticity नियंत्रित रहेंगे; blocks स्वतंत्र होंगे। एक ही I checkpoint से कई self-play seeds निकालना संभव sensitivity analysis है, पर उन्हें स्वतंत्र imitation replicates नहीं मानेंगे।

प्राथमिक contrasts:
- \(C_1=\Delta_{TA}-\Delta_{Q20}\)
- \(C_2=\Delta_{TA}-\Delta_{CITY}\)
- \(C_3=\Delta_{TA}-\Delta_{TC}\)

जहाँ \(\Delta_a=S_a-S_I\), और \(S\) held-out reasoning score है। साझा I के कारण paired differences में baseline cancel होता है, फिर भी absolute gains रिपोर्ट होंगे।

## 3. साझा GPT-4 imitation data

**प्रस्तावित निर्माण:** एक frozen GPT-4 version, एक frozen prompting protocol और समान decoding settings से demonstrations लें; version, तारीख, prompts, usage और filtering logs सुरक्षित रखें। उपलब्ध न होने पर इस prerequisite को अधूरा घोषित करें—दूसरे teacher को चुपचाप substitute न करें।

- तीन content families—Taboo, objects और cities—को समान **learner-target token allocation** दें। Taboo allocation के भीतर TA और TC demonstrations आधे-आधे हों। इस तरह Taboo को दो incentive modes होने के कारण दुगुना imitation exposure नहीं मिलेगा।
- प्रत्येक family में roles के target tokens और प्रस्तावित difficulty bins संतुलित हों। Episode counts, tokens और acceptance rates दोनों प्रकाशित हों; केवल बराबर episode count को बराबर exposure न मानें।
- Taboo demonstrations में incentive mode स्पष्ट role header में हो। Q20/CITY में cooperative mode हो। यही मिश्रित dataset **सभी arms** को दें; कोई arm-specific imitation नहीं।
- Train/validation/test entities और clue/question templates पहले partition करें। Generation केवल training partition से हो। Invalid JSON, rules का उल्लंघन और factually inconsistent demonstrations deterministic validators से हटें; semantic ambiguity का blinded human audit हो।
- Reward/win के आधार पर केवल सफल trajectories चुनना टालें। प्रारंभिक स्थिति तथा difficulty के अनुसार sample करें; सफल और असफल valid examples का अनुपात दर्ज करें। Final SFT में सभी role outputs पर समान, पूर्वनिर्धारित token-weighted cross-entropy हो। Teacher की private chain-of-thought आवश्यक नहीं; केवल game-visible actions और संक्षिप्त observable answers हों।
- Imitation examples, teacher generation budget, SFT updates और stopping point validation loss/rule compliance से तय हों; held-out reasoning test से नहीं।

**Rationale:** समान demonstrations imitation exposure का confound हटाते हैं। Mixed-incentive Taboo imitation adversarial skill का अतिरिक्त लाभ दे सकती है, इसलिए no-imitation तथा neutral-imitation extensions अलग दिए गए हैं; core दावा साझा mixed imitation के बाद का है।

## 4. लागू करने योग्य प्रस्तावित games

### 4.1 TA और TC: constrained lure-and-avoid Taboo

मूल conversational Taboo की अनिश्चितता के कारण पहले machine-verifiable, constrained संस्करण प्रस्तावित है। यह स्वतंत्र operational choice है, मूल SPAG game होने का दावा नहीं।

**Episode सामग्री:**
- Curated noun/category bank से 24 public candidate words और उनमें से एक hidden target लें। कठिनाई semantic overlap और eligible clues की संख्या से stratify हो।
- Curated clue library में प्रत्येक clue एक factual category/property question है; validator के पास उसका valid-answer subset है। उदाहरण: “इस सूची का कोई फल चुनें।” किसी valid clue के कम-से-कम छह acceptable candidate answers हों और hidden target उनमें हो।
- Target का exact spelling, synonyms, initials, rhyme, character positions या uniquely identifying paraphrase clue में निषिद्ध हों। Ambiguous facts और proper-name loopholes audit में हटें।

**Roles/information/actions:**
- Sender/attacker को target, public candidate list, eligible clues और transcript दिखे। वह हर turn एक approved clue चुने; arbitrary free text या target-containing string नहीं भेज सकता। Receiver को केवल rendered clue दिखे, clue ID/eligible menu नहीं।
- Receiver को target नहीं दिखता। उसे mode, public candidate list, current clue तथा previous exchanges दिखें। वह एक candidate answer चुने।
- Candidate ordering episode-wise randomized हो; opaque action IDs role-private हों। किसी shared index, message length या formatting channel से target encoding अनुमत न हो।
- अधिकतम दो exchanges हों; repeated clue/answer निषिद्ध हों। प्रत्येक new clue के लिए कम-से-कम छह अभी उपलब्ध valid answers रहें। Target-answer आते ही episode समाप्त; अन्यथा दो turns पर समाप्त।
- Constrained decoding/schema enforcement दोनों modes में समान हो। Invalid या semantically wrong answer turn के लिए incorrect माना जाए; malformed action को fixed failure handling मिले।

**Rewards:** \(H=1\) यदि receiver ने valid answer के रूप में target कहा, अन्यथा 0। \(V\) valid-answer turns का fraction है।
- Sender reward दोनों modes में \(H\)।
- TA receiver reward \(V-0.5H\): प्रश्न का वैध उत्तर देना है, लेकिन hidden taboo target से बचना है।
- TC receiver reward \(V+0.5H\): प्रश्न का वैध उत्तर देते हुए sender के hidden target तक पहुँचना है।
- सभी scalar episode rewards को समान fixed divisor 1.5 से scale करें; per-arm empirical normalization न करें। Invalid sender action पर fixed penalty और termination समान हों।

इससे sender का उद्देश्य स्थिर रहता है और receiver की target-related preference उलटती है। Valid non-target answer TA में target से अच्छा है; invalid answer को सफल refusal न माना जाए। TC में receiver target नहीं जानता और sender सीधे target नहीं लिख सकता।

**महत्वपूर्ण सीमा:** TC में target अनुमान करना और TA में target से बचना अलग induced strategies हैं—यही treatment का हिस्सा है। Reward sign के अतिरिक्त rules, target distribution, candidate lists, clue libraries, horizon और observation schema समान रहेंगे। Role header में objective बताना treatment का भाग है।

### 4.2 Q20: cooperative 20-Question

- Curated objects/entities की 128-item public candidate set; balanced target sampling। Object fact table source-checked और internally consistent हो।
- Answerer target और relevant fact table देखे; questioner target नहीं देखे।
- Questioner approved binary-attribute questions चुने, जैसे category/property queries, या final entity guess दे। अधिकतम 20 yes/no questions और एक final guess; पहले correct final guess पर समाप्त, गलत final guess पर failure termination।
- Answerer constrained yes/no output दे। Table से mismatch पर episode invalid/failure हो; free-form hint channel न हो।
- दोनों roles को reward \(R=\text{correct}\times(1-0.1q/20)\), जहाँ q पूछे प्रश्न हैं। Invalid/factually false action का fixed penalty हो।

### 4.3 CITY: cooperative Guess-My-City

- Curated 128-city public candidate set; continent/region, coastal status, geographic properties और population bins जैसी verified attributes। Population bins के reference year को freeze करें।
- Host hidden city और fact table देखे; guesser candidate set और transcript देखे।
- Guesser approved attribute queries चुने; host categorical answer दे। अधिकतम 10 queries और एक final city guess। Correct guess पर success, गलत guess या limit पर failure।
- City name, aliases, coordinates का direct identifier या arbitrary hint निषिद्ध। Host responses deterministic table से validate हों।
- Shared reward \(R=\text{correct}\times(1-0.1q/10)\); invalid/false actions के लिए वही fixed failure policy।

Q20/CITY cooperative information-retrieval games बने रहते हैं, लेकिन ये भी मूल paper के सत्यापित rules नहीं हैं। Finite candidate spaces और constrained actions automatic validation देते हैं, किंतु natural-language game generalization सीमित करते हैं। सभी game banks और validators को training से पहले freeze करना होगा।

## 5. TC trivial न हो: feasibility तथा manipulation gate

यह gate test-suite evaluation खोलने से **पहले** dev content पर लागू होगा:

1. **Leakage audit:** every clue में target string/alias और unique identifier नहीं; acceptable set size ≥6; receiver को sender menu, target-dependent ID, hidden logs या reward explanation से target न मिले।
2. **Sequential audit:** दो clues का intersection target को singleton न बनाए; proposed eligibility rule में intersection size ≥3 रखें। यही rule TA और TC में लागू हो।
3. **Baselines:** random-valid receiver, most-frequent-valid receiver, frequency-based sender और simple semantic/elimination heuristic चलाने का भविष्य का प्रावधान रखें। TC की success या TA की avoidance यदि static frequency shortcut से लगभग पूर्ण हो, तो इसे meaningful reasoning manipulation न मानें।
4. **Behavior checks:** valid-answer rate, target-hit rate, clue diversity, category/mode sensitivity और refusal/invalid-action rate रिकॉर्ड हों। Same frozen states पर दोनों mode headers में receiver के target-related action probabilities जाँचना preference flip का diagnostic है; actual target receiver को न दिखाएँ।
5. **Collusion checks:** unseen targets, new candidate orderings, paraphrased but verified clue renderings और independent checkpoint cross-play पर जाँचें। Shared weights semantic signaling सीख सकते हैं; pure memorized codebook transfer को semantic reasoning improvement से अलग रिपोर्ट करें।
6. **पूर्वनिर्धारित gate का प्रस्ताव:** schema/factual validity ≥95%; direct/unique-target leaks शून्य audited tolerance; deterministic trivial baseline success ≥90% या empirical training saturation होने पर game bank/difficulty को test-unblinding से पहले revise करें। ये feasibility thresholds assumptions हैं, source facts नहीं। Pilot में meaningful mode-dependent behavior न मिले तो treatment को failed manipulation कहें।

यदि gate पास करने के लिए **केवल TC** के rules बदलने पड़ें, मुख्य incentive-only contrast त्यागें और उसे bundled intervention घोषित करें। दोनों arms में समान revision संभव हो तो नया protocol freeze करके pilot दोहराएँ। Hidden-target cooperation कठिन हो सकती है; feasibility अभी demonstrated नहीं है।

## 6. Self-play update procedure

**प्रस्तावित common trainer:** role-conditioned single policy, episode-terminal role-specific returns के साथ clipped PPO और frozen I reference की KL penalty। यह SPAG का verified optimizer नहीं।

1. प्रत्येक iteration पर current policy snapshot freeze करें। दोनों roles उस snapshot से independently sample करें; role/mode tokens visible रहें।
2. Same seed-block में TA/TC के initial target, candidate set और feasible clue-bank draws pair करें। Generated transcripts identical बनाने की कोशिश न करें—rollout differences incentive effect का माध्यम हैं।
3. Episode validator reward निकाले। Role-specific value head/role indicator से advantages निकालें; opponent के private observation को learner input में न दें।
4. दोनों roles के own action tokens पर PPO update हो; environment messages पर policy loss नहीं। Role exposures कुल training-token allocation में 50:50 हों। समान optimizer, learning rate schedule, clipping, KL coefficient, batch-token size और PPO epoch count हों।
5. Reward formulas fixed हों; shared value/advantage-processing rule हो। Arm-wise win-rate के अनुसार reward tuning या game-specific optimizer search न करें।
6. Hyperparameters dev pilot पर सभी arms का symmetric छोटा grid देखकर stability/rule compliance के आधार पर freeze करें; reasoning test scores आधार न बनें। KL, entropy, gradient norms, effective update tokens और invalid rates log हों।
7. Final budget checkpoint प्राथमिक है; 25%, 50%, 75%, 100% learning-curve checkpoints secondary हैं। Best test checkpoint चुनना निषिद्ध।

## 7. Budget: एक प्राथमिक matching rule

**प्राथमिक नियम: प्रति arm समान total post-imitation model-compute cap**, generation और optimization दोनों को शामिल करते हुए। केवल समान episodes या output tokens प्राथमिक matching नहीं होंगे।

- Fixed model/hardware configuration पर preregistered FLOP estimator में prefill, cached autoregressive decoding, reference/value passes और backward/update computation गिने जाएँ। समान parameter-efficient/full-finetuning choice सभी arms में हो।
- उदाहरणात्मक allocation: cap का 60% rollout/reference computation और 40% optimization के लिए। यह split pilot के बाद एक बार freeze होगा। Remainder को किसी arm में मनमाने ढंग से transfer न करें।
- Variable context/episode lengths के कारण नए episodes या updates तभी admit करें जब वे assigned caps में पूरे हों। Target tolerance ≤1%; यदि exact caps असंभव हों तो सभी arms का usable common cap घटाएँ, न कि कुछ arms को अतिरिक्त compute दें।
- Generation FLOPs, prefill/output tokens, sampled episodes, discarded/truncated tokens, reference/value inference, optimization FLOPs, updates, trained action tokens और wall-clock अलग दर्ज हों। GPT-4 imitation generation/SFT लागत common fixed stage के रूप में अलग दर्ज हो।
- Fixed imitation खर्च main arms में समान है। Validators/data curation CPU और human costs भी अलग हों; इन्हें free resource की तरह न छिपाएँ।

**Secondary sensitivity:** समान sampled action-token budget और समान optimization-token budget पर उपलब्ध checkpoints/interpolated learning curves से ranking की robustness देखें। Compute-matching और token-matching से अलग rankings मिलें तो efficiency-vs-data-exposure distinction रिपोर्ट करें।

## 8. Held-out reasoning evaluation

### Suite

प्रस्तावित चार समान-भार domains:
1. Mathematical multi-step problems;
2. Deductive/constraint logic;
3. Relational/compositional reasoning;
4. Causal/temporal reasoning।

हर domain में लगभग 300–500 held-out items प्रारंभिक planning assumption है। मिश्रण में licensed established tasks तथा independently generated, human-validated fresh problems हों। Final benchmark names, versions, counts और scoring scripts training शुरू होने से पहले register करें। Games या उनकी vocabulary-heavy QA primary suite न हों।

### Scoring और aggregation

- समान neutral evaluation prompt, context limits और inference-token cap; no game-mode header, no tools, no adaptation। Primary pass@1 deterministic decoding।
- Numeric/symbolic answers canonicalized exact match; multiple-choice में exact label; structured logic में executable answer validator। Open-ended judge-only tasks primary composite से बाहर रखें।
- Item correctness 0/1; domain accuracy निकालें; चार domain accuracies का equal-weight mean ×100 प्राथमिक score S हो। Invalid/empty/truncated final answer गलत हो।
- Free-form rationale generate हो सकती है, लेकिन rationale length या judge-rated eloquence को reasoning score न मानें।
- Secondary: per-domain gain, held-out game transfer, rule compliance, verbosity, instruction-following/general capability retention और inference-cost sensitivity। Test-time gains को अतिरिक्त output tokens से न खरीदें।

### Contamination controls

- Evaluation authors/splits game generation और teacher prompts से अलग; test items teacher या self-play system को न भेजें।
- Exact/near-duplicate text, entity-template overlap और semantic similarity audit; family/template-level splits केवल random row split से बेहतर होंगे।
- Teacher generation logs का test contamination के लिए offline audit, without feeding tests back to teacher। Fresh item generation seeds और creation dates seal करें।
- Base model की pretraining contamination पूरी तरह ज्ञात नहीं होगी; fresh-vs-public subset results अलग रिपोर्ट करें। Test-set selection arm outcomes देखकर न बदलें।

## 9. Replicates, pilot और statistics

### Pilot/sample size

- Dev-only pilot में लगभग तीन independent seed-blocks से feasibility, compute और paired contrast variance का rough estimate लें। यह संख्या planning assumption है, power evidence नहीं।
- Final independent confirmatory blocks की संख्या pilot paired-SD, test-item uncertainty और simultaneous comparison critical values की simulation से तय करें; target power 80–90% हो। Minimum planning floor पाँच blocks है, sufficient-power guarantee नहीं।
- Practical superiority margin **δ = 1.0 absolute percentage point** on S, pilot outcomes देखने से पहले fix करें। Power planning के लिए true contrast =2 points एक illustrative alternative है—expected result नहीं। δ से अधिक कितना effect detect करना है, preregister करें।
- Small pilot variance estimate की uncertainty के कारण conservative upper variance bound और item/seed hierarchical simulation अपनाएँ। Pilot runs, यदि protocol tuning में उपयोग हुए हों, final confirmatory analysis से बाहर रखें। Resource ceiling पर्याप्त n न दे तो study को exploratory/underpowered label दें; margin न घटाएँ।

### Inference/decision rule

- Independent training block मुख्य replication unit है। Items को अलग training replicates न मानें। Same items और seed-block pairing का उपयोग करें।
- C1, C2 और C3 को एक confirmatory family मानकर **Bonferroni familywise α=0.05** लागू करें। प्रत्येक contrast का two-sided **98.33% CI** दें; इससे दोनों comparator contrasts तथा incentive contrast का multiplicity control एक साथ होता है। Descriptive 95% intervals अलग स्पष्ट label से दे सकते हैं।
- Proposed estimation: paired block means, साथ में domain-stratified items और independent blocks का nested paired bootstrap। कम n पर bootstrap stability जाँचें; paired t-based intervals तथा sensitivity analysis भी दें। भविष्य के task-population inference और fixed-suite inference को अलग label करें।
- किसी contrast में practical superiority तभी जब corrected CI का lower bound **+1.0 point से ऊपर** हो। दोनों C1 और C2 यह पास करें तभी “दोनों comparators पर superior” कहें।
- C3 भी वही threshold पास करे और manipulation gate सफल हो तभी “इस Taboo implementation में adversarial incentives ने अतिरिक्त gain दिया” कहें।
- साथ ही TA का imitation baseline के सापेक्ष absolute gain रिपोर्ट करें। यदि सभी arms घटें, तो comparator-relative लाभ को “कम degradation” कहें, reasoning improvement नहीं।
- CI zero या δ को पार करे तो **inconclusive for practical superiority**। Non-significance equivalence नहीं। Equivalence चाहिए तो अलग preregistered TOST/margin और उसकी multiplicity/power आवश्यक होगी; core में उसका दावा नहीं।

## 10. सीमित-budget core और extensions

**Core:** B/I evaluation + TA, TC, Q20, CITY; common imitation; common trainer/compute cap; independent blocks; external reasoning suite; तीन preregistered contrasts। बजट कम हो तो model size या per-arm compute समान रूप से घटाएँ। TC हटाकर incentive causality का दावा या replicates घटाकर definitive superiority का दावा न करें।

**Optional extensions:**
- **Imitation ablation:** TA/TC को B से शुरू करें; पर्याप्त बजट हो तो सभी games। Difference-in-differences से incentive × imitation interaction जाँचें। समान post-imitation self-play budget और समान total pipeline budget अलग estimands हैं; दोनों को न मिलाएँ।
- **Imitation content ablation:** neutral/common instruction imitation या Taboo के एक ही mode की imitation से sensitivity; यह नया experiment है।
- **Full factorial:** Q20/CITY में feasible adversarial counterparts, केवल यदि rules/information fixed रखते हुए objectives बदल सकें। अन्यथा game × incentive factorial का causal अर्थ कमजोर होगा।
- **Natural-dialogue replication:** मूल rules/rewards मिल जाने पर अलग verified-recipe arm; constrained proxy के परिणाम सीधे मूल SPAG पर स्थानांतरित न करें।
- **Frozen-partner/cross-play:** policy co-adaptation, role asymmetry और reward-sign mechanism जाँचने के लिए।

## 11. संसाधन योजना — केवल assumptions

एक संभावित affordable starting point 1–3B open-weight instruction model, parameter-efficient PPO/SFT, छोटे structured contexts और प्रति arm लगभग 2–10 million sampled action tokens हो सकता है। यह token range **मुख्य matching rule नहीं** और पर्याप्त learning का दावा नहीं। Pilot compute estimator के बाद actual FLOP cap तय होगा।

Memory के लिए संभवतः 1–4 आधुनिक 48–80GB GPUs का परीक्षण चाहिए; actor/reference/value copies, optimizer और implementation के अनुसार आवश्यकताएँ बदलेंगी। GPU-hours, GPT-4 API cost और final replicate count अभी विश्वसनीय रूप से अनुमानित नहीं हैं। उदाहरणतः पाँच blocks × चार arms =20 confirmatory self-play runs, साथ में पाँच SFT runs, pilot और evaluation; इसलिए single-run feasibility पूर्ण study affordability नहीं दर्शाती। Validators और test curation हेतु CPU तथा human audit समय अलग चाहिए।

दिए environment में GPU/datasets/project dependencies उपलब्ध नहीं बताए गए हैं। यह design बनाने में बाधा नहीं, लेकिन यहाँ proposed training की उपलब्धता सिद्ध नहीं करता।

## 12. निष्कर्षों की interpretation

| संभावित परिणाम | अनुमत निष्कर्ष |
|---|---|
| C1 और C2 practical superiority पास; C3 भी पास; manipulation सफल; TA का absolute gain positive | साझा imitation और matched compute के बाद TA दोनों comparators से बेहतर; इस constrained Taboo में adversarial incentives योगदान देते हैं। मूल SPAG की पूर्ण replication नहीं। |
| C1/C2 पास, C3 inconclusive | Taboo bundle बेहतर; adversarial incentives को अलग कारण नहीं ठहरा सकते। |
| C3 पास, पर कोई comparator contrast fail/inconclusive | Taboo के भीतर incentive benefit; दोनों अन्य games पर superiority सिद्ध नहीं। |
| केवल एक comparator पर superiority | दावा उसी comparator तक सीमित। |
| Game success बढ़े, external reasoning नहीं | Game learning/strategy improvement; reasoning transfer सिद्ध नहीं। |
| Mode manipulation विफल, leakage/shortcut मिले | Intended causal contrast invalid; redesign आवश्यक, outcome को incentive evidence न मानें। |
| सभी arms I से खराब, TA कम खराब | Relative robustness/कम degradation, reasoning improvement नहीं। |
| Wide CIs या δ cross हो | Inconclusive; न equivalence, न no-effect का प्रमाण। |
| Corrected CI पूरा negative या −δ से नीचे | क्रमशः contrary-direction evidence या practically meaningful disadvantage; उसी operational setting तक सीमित। |

**अंतिम सीमा:** यह design प्रश्न को नियंत्रित और परीक्षण योग्य बनाता है, लेकिन उपलब्ध स्रोत मूल game/training recipe को पुनर्निर्मित करने के लिए अपर्याप्त हैं। किसी superiority, effect size या successful feasibility का observed परिणाम प्रस्तुत नहीं किया गया है।
````

**Stage**

````text
result
````

**Evidence**

````text
Repository inspection में `/workspace` में केवल `task.json` मिला; छोटे `find` check ने अतिरिक्त files के अभाव की पुष्टि की। `task.json` में मूल comparison question, design-only context और embedded `documents.track.md` string थी, जिसमें repositories/compute आवश्यक नहीं बताए गए। कोई अलग paper, detailed game specification, training code या dataset उपलब्ध नहीं था। Researcher ने बाद में स्पष्ट किया कि setup_2 comparison को, setup_32 adversarial SPAG को और setup_33 दोनों non-adversarial comparators को नाम देते हैं; उनसे rules/rewards/budgets पुष्ट नहीं होते। इसीलिए final design common-checkpoint comparison और within-Taboo causal control को अलग करता है, सभी executable game/trainer choices को प्रस्ताव कहता है, और full original-recipe replication का दावा नहीं करता। Constrained actions, hidden target, multi-answer clues और identical TA/TC observation/action spaces direct target revelation को रोकने तथा reward-preference intervention अलग करने के लिए चुने गए हैं; pilot gate उनकी feasibility की जाँच करेगा, उसे अभी स्थापित नहीं मानता। Equal compute, separate generation/update accounting, independent seed-blocks और held-out suite training exposure, pseudo-replication और game-specific success के confounds को संबोधित करते हैं। किसी experiment के चलने या किसी परिणाम का साक्ष्य नहीं है।
````

**Assumptions**

````text
[
  "सभी games के दिए rules, candidate-set sizes, clue constraints, reward formulas, horizons और PPO procedure प्रस्तावित operational choices हैं, source-supported original SPAG details नहीं।",
  "GPT-4 version/data access, open-weight base model license, trusted factual banks और independent evaluation curation भविष्य में उपलब्ध होंगे।",
  "Constrained Taboo में reward-sign change के साथ nontrivial cooperative और adversarial behavior दोनों संभव हैं; feasibility gate के बिना यह assumption स्वीकार नहीं किया जाएगा।",
  "δ=1 percentage point, four equal-weight reasoning domains, 300–500 items/domain, pilot/final replicate planning और illustrative model/resource ranges design assumptions हैं।",
  "प्रति-arm generation/optimization compute का reliable common estimator और लगभग समान hardware/software execution भविष्य में स्थापित किया जा सकता है।"
]
````

**Uncertainties**

````text
[
  "मूल SPAG तथा comparators के विस्तृत rules, reward implementation, GPT-4 prompts/version, base model, optimizer और budgets अज्ञात हैं।",
  "Restricted operational games से natural-language adversarial play या मूल SPAG पर कितना external validity होगा, अज्ञात है।",
  "TC में hidden-target inference या TA में avoidance कहीं trivial अथवा अत्यधिक कठिन न हो, यह pilot में सत्यापित होना बाकी है।",
  "Final power, seed count, GPU/API cost और compute cap pilot variance तथा resource profiling के बिना निश्चित नहीं हैं।",
  "Base-model pretraining contamination पूरी तरह ज्ञात नहीं होगी; fresh-item sensitivity केवल आंशिक mitigation है।",
  "किस arm में reasoning gain होगा, उसका आकार और relative ranking पूरी तरह अज्ञात हैं; कोई प्रयोग नहीं चला है।"
]
````

### Event 5 — Simulator

**Message**

````text
अंतिम design में rationale, controls, analysis plan और feasibility पर्याप्त रूप से दिए गए हैं। साझा GPT-4 imitation checkpoint, दोनों non-adversarial comparators और अलग within-Taboo incentive contrast मूल प्रश्न को परीक्षण योग्य बनाते हैं। इसे प्रस्तावित constrained games का controlled अध्ययन ही कहा जाए, मूल SPAG की verified replication नहीं। मूल rules मिलने पर external validity की जाँच आवश्यक रहेगी। कोई प्रयोग चला है या superiority सिद्ध हुई है—ऐसा दावा नहीं किया गया है। इस design-only deliverable के लिए आगे revision आवश्यक नहीं है।
````

**Interaction**

````text
conclude
````

**Phase**

````text
result_review
````

**Action**

````text
stop
````

**Approve Approach**

````text
false
````

**Evidence**

````text
प्रस्तुत design में arm table, operational rules और rewards, common trainer, compute accounting, manipulation/leakage checks, held-out reasoning evaluation, independent seed-blocks, pilot-based power planning, corrected confidence intervals और interpretation rules शामिल हैं। स्रोत-अज्ञात विवरण तथा resource estimates स्पष्ट assumptions हैं। भविष्य की feasibility gates को निष्पादित परिणाम नहीं बताया गया है; रिपोर्ट किए गए repository निरीक्षण को प्रयोग का प्रमाण नहीं माना गया है।
````

**Objectives Open**

````text
[]
````

## Provenance

````text
{
  "source_run": "runs/openai-astra-top10-trial-1-batch-2",
  "repair_run": "runs/repair-1-openai-astra-top10-trial-1-batch-2",
  "event_log": "runs/openai-astra-top10-trial-1-batch-2/episodes/expbench_neurips2024_93638_3-a0d336b66a08/candidate_001/attempt-1/output/neurips2024__93638__3/events.jsonl",
  "event_log_sha256": "cdb9a3d4120c191d31839ed073978a23137798bc98c3af6a39372d3017c85ee5",
  "models": {
    "actor": {
      "model": "gpt-6-astra",
      "provider": "openai",
      "reasoning_effort": "low"
    },
    "researcher": {
      "model": "gpt-6-astra",
      "provider": "openai",
      "reasoning_effort": "low"
    },
    "judge": {
      "model": "gpt-6-astra",
      "provider": "openai",
      "reasoning_effort": "low"
    }
  }
}
````
