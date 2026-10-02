# candidate_001 · expbench · iclr2024/19281/1

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **33/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
पहले उपलब्ध brief और दस्तावेज़ों का निरीक्षण करके संक्षेप में बताएं कि क्या ज्ञात है और क्या केवल प्रस्तावित मान्यता होगी। यह design-only कार्य है; repository, compute या प्रयोग चलाना आवश्यक नहीं है। अभी पूरा प्रयोग-डिज़ाइन न दें। एक प्रस्तावित approach दें: feedback बनाम उपयुक्त controls की तुलना, property improvement के साथ real-world distribution alignment और structural diversity को अलग-अलग परखना, तथा molecular hallucination और अत्यधिक लंबी carbon chains की मापनीय परिभाषाएं। p-logP का अर्थ, affinity के proxy बनाम वास्तविक binding evidence, target/data/reference distribution का चुनाव, और reward optimization से उत्पन्न bias जैसी consequential uncertainties स्पष्ट करें। प्रस्तावित controls, analysis की रूपरेखा और feasibility बताएं ताकि मुख्य डिज़ाइन से पहले approach पर सहमति हो सके।
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
Brief केवल प्रयोग-डिज़ाइन मांगता है; कोई dataset, निश्चित target, feedback implementation या empirical result उपलब्ध नहीं है। track.md के अनुसार repository और compute आवश्यक नहीं हैं।
````

**Objectives Open**

````text
[
  "उपलब्ध inputs और consequential uncertainties की समीक्षा",
  "निष्पक्ष controls तथा स्वतंत्र मूल्यांकन वाला approach तय करना",
  "बाद में rationale, controls, analysis plan और feasibility सहित अंतिम प्रयोग-डिज़ाइन देना"
]
````

### Event 2 — Actor

**Answer**

````text
### निरीक्षण से क्या ज्ञात है
- उपलब्ध `task.json` में केवल मूल प्रश्न और design-only निर्देश हैं। उसमें `track.md` का उल्लेख/पाठ भी यही कहता है कि repository और compute आवश्यक नहीं हैं; अलग दस्तावेज़ उपलब्ध नहीं मिला।
- प्रश्न chemical feedback (p-logP, QED और binding affinity) से property improvement, real-world distribution alignment, structural diversity और hallucination reduction को जाँचना चाहता है। यह लाभ का प्रमाण नहीं, जाँचने योग्य दावा है।
- कोई model, feedback algorithm, target, dataset, reference distribution, score definition या experimental result नहीं दिया गया। कोई प्रयोग नहीं चलाया गया; केवल फ़ाइलों का निरीक्षण किया गया है।

### प्रस्तावित approach — अभी पूर्ण डिज़ाइन नहीं
**1. समान आधार से नियंत्रित तुलना।** एक ही pretrained generator/checkpoint, target conditioning, training data और generation budget के साथ: (A) बिना chemical feedback, (B) chemical feedback सहित, (C) बिना feedback उसी generator के samples को समान chemical scores से post-hoc rerank/filter करना। C बताएगा कि लाभ feedback embedding से है या केवल selection से। Feedback की अतिरिक्त training/sampling को ध्यान में रखकर समान oracle-call तथा compute-budget तुलना प्रस्तावित है; raw और selected outputs दोनों दिखाए जाएँ। संसाधन हों तो reward-permuted/sham-feedback control तथा individual reward-component ablations जोड़ें; sham को उपयोगी reward वाले मुख्य control का विकल्प न मानें।

**2. तीन अलग प्रश्न, एक composite success score नहीं।**
- **Property improvement:** p-logP, QED और target-specific affinity endpoints अलग-अलग, उनकी पूरी distributions और predeclared desirable ranges सहित। ऊँचा logP अपने-आप बेहतर नहीं माना जाएगा। Reward में प्रयुक्त scores और स्वतंत्र evaluation scores अलग रिपोर्ट हों।
- **Distribution alignment:** पहले से चुने, training से पृथक real-molecule reference से physicochemical descriptors, size/chain-tail frequencies और scaffold/fingerprint distributions की दूरी। समान sample sizes और reference-vs-reference baseline से दूरी की व्याख्या करें। Target-oriented improvement पूरे chemical universe की distribution की नकल के समान नहीं है।
- **Structural diversity:** validity के साथ uniqueness, novelty, scaffold richness/entropy, fingerprint-based internal diversity और duplicate/mode-collapse rates अलग रिपोर्ट हों। Alignment और diversity को एक-दूसरे का पर्याय न मानें।

**3. मापनीय, सीमित operational definitions।**
- **Molecular hallucination:** कम-से-कम दो पृथक श्रेणियाँ: (i) parse/sanitization/valence failure वाला invalid output; (ii) valid graph पर predeclared chemistry-plausibility alerts, जैसे स्पष्ट unstable/reactive motifs या constraint violations। इन्हें अलग rates में दिखाएँ; novelty, database में अनुपस्थिति, कम synthetic-accessibility score या कमजोर predicted affinity को अपने-आप hallucination न कहें। Valid-but-implausible श्रेणी के लिए blinded expert audit का छोटा stratified subset प्रस्तावित है; alert rules केवल proxy होंगे। Denominator सभी attempted outputs होगा, साथ में valid-output conditional rates भी।
- **अत्यधिक लंबी carbon chains:** प्रारंभिक graph definition: ring atoms को निकालकर बचे acyclic carbon–carbon subgraph में सबसे लंबे सरल carbon path की atom count (bond types की convention पूर्वनिर्धारित)। Reference के training-independent calibration भाग में इस length के predeclared upper quantile, जैसे 99वें percentile, से ऊपर वाले molecules का अनुपात और reference से excess rate मापें। Threshold result देखकर न चुनें। Absolute-length sensitivity check, total heavy-atom count और chain/heavy-atom ratio भी रखें ताकि केवल बड़े molecules या macrocycles के कारण गलत अर्थ न निकले। यह operational convention प्रस्ताव है, स्रोत-समर्थित स्थापित cutoff नहीं।

**4. विश्लेषण की रूपरेखा।** स्वतंत्र generation/training seeds पर paired contrasts और uncertainty intervals; molecules को स्वतंत्र training replicates न मानें। सारे outputs की accounting, invalid/duplicate/filtered fractions और accepted yield दिखाएँ। Property लाभ, alignment और diversity की trade-offs/Pareto view दें। Preservation के लिए पहले से चुने practical non-inferiority margins आवश्यक होंगे—केवल non-significant decline पर्याप्त नहीं। Margins, sample sizes और प्राथमिक endpoints मुख्य डिज़ाइन में reference variability और feasibility देखकर तय होंगे।

### सहमति से पहले consequential uncertainties
1. **p-logP किसे कहते हैं?** Predicted logP, penalized logP या अन्य quantity? Penalized logP हो तो exact equation, penalties, normalization और optimization direction चाहिए; केवल नाम देखकर formula मानना उचित नहीं।
2. **Affinity का evidence क्या है?** Docking/QSAR/learned score proxy है, वास्तविक binding प्रमाण नहीं। Target structure, assay endpoint (जैसे Kd/Ki), score direction और units तय हों। स्वतंत्र predictor/rescoring reward exploitation की जाँच कर सकता है, पर binding सिद्ध करने के लिए biochemical assay चाहिए।
3. **Target और references कौन-से होंगे?** Target-specific measured ligands और broad drug-like molecules दो उपयोगी लेकिन अलग references हो सकते हैं। उनकी provenance, assay consistency, standardization, scaffold/temporal split तथा training overlap जाँचना होगा। केवल high-score या active-only reference चुनना alignment के निष्कर्ष को पक्षपाती कर सकता है।
4. **Feedback implementation क्या है?** RL/fine-tuning, iterative prompting या rejection-based update, reward weights और normalization उपलब्ध नहीं हैं। सभी endpoints को एक ही reward predictor पर जाँचने से circular evaluation होगा। Independent held-out evaluation, frozen reward setup और size/chain-linked reward shortcuts की जाँच प्रस्तावित है।
5. **व्यावहारिक सीमा क्या होगी?** उपलब्ध model/data, future sampling/oracle budget और wet-lab access स्पष्ट नहीं हैं। इनके बिना power या वास्तविक affinity validation का वादा नहीं किया जा सकता।

### Feasibility और अगला निर्णय
यह design-only चरण किसी dataset download, model training, docking या assay पर निर्भर नहीं है। भविष्य में descriptor/graph checks CPU पर संभव हैं; generation, docking और assays की लागत चुने गए setup पर निर्भर होगी। कृपया core controls A/B/C, तीन अलग evaluation axes तथा उपर्युक्त operational definitions पर सहमति दें, और विशेषतः p-logP की परिभाषा, target/reference तथा affinity evidence की उपलब्धता स्पष्ट करें। स्वीकृति के बाद ही पूरा डिज़ाइन विकसित किया जाएगा।
````

**Stage**

````text
plan
````

**Evidence**

````text
`inspect_repository('.')` ने केवल task.json दिखाया। `inspect_repository('task.json')` में मूल प्रश्न, design-only context और documents.track.md में 'repositories and compute are not required' मिला। एक सीमित `find /workspace -maxdepth 2 -type f -print` जाँच में भी केवल /workspace/task.json मिला। किसी chemistry package, model, dataset या experiment का execution/validation नहीं हुआ। उपयोगकर्ता के environment विवरण में datasets खाली, network disabled, GPU disabled और project dependencies अनुपलब्ध हैं; ये वर्तमान exploration की सीमाएँ हैं, भविष्य के अध्ययन का निर्धारित setup नहीं।
````

**Assumptions**

````text
[
  "समान base generator और conditioning पर feedback toggle या तुलनीय variants बनाना संभव होगा; अभी इसका source evidence नहीं है।",
  "उपयुक्त independent reference/calibration/evaluation data और molecule standardization rules आगे चुने जा सकेंगे।",
  "99वें percentile का chain cutoff, independent seeds, sham control और expert audit प्रस्तावित choices हैं, fixed task requirements नहीं।",
  "वर्तमान fixed requirement केवल प्रश्न का experiment design है; लाभ सिद्ध करना या प्रयोग चलाना अपेक्षित नहीं है।"
]
````

**Uncertainties**

````text
[
  "p-logP की exact definition, desired range/direction और reward combination अज्ञात हैं।",
  "Target, generator, feedback mechanism और reference population निर्दिष्ट नहीं हैं।",
  "Affinity proxies और वास्तविक assay evidence की उपलब्धता अज्ञात है।",
  "Reward optimization bias, training/reference leakage तथा independent evaluator की विश्वसनीयता की जाँच भविष्य के setup पर निर्भर है।",
  "Budget, effect-size targets और preservation margins के बिना sample size या power तय नहीं की जा सकती।"
]
````

### Event 3 — Simulator

**Message**

````text
प्रस्तावित approach स्वीकृत है। A/B/C controls, raw तथा selected outputs का पृथक विश्लेषण, और property, alignment, diversity तथा hallucination के अलग endpoints बनाए रखें। अब rationale, controls, analysis plan और feasibility सहित पूर्ण अंतिम experiment design दें; प्रयोग चलाना आवश्यक नहीं है। अज्ञात setup के लिए स्रोत-पुष्टि का दावा न करें: एक स्पष्ट प्रस्तावित generator/feedback update, target एवं data-selection protocol और reward formula चुनें। p-logP का स्रोत-अर्थ अज्ञात ही रखें; मुख्य डिज़ाइन में अपनाई गई परिभाषा और वैकल्पिक अर्थ होने पर बदलाव स्पष्ट करें। Feedback में केवल property signals रखने और अतिरिक्त diversity/chain penalties जोड़ने का अंतर साफ रखें, ताकि distribution सुधार का श्रेय किसी छिपे structural constraint को न मिले। Oracle-call और compute budgets एक साथ ठीक बराबर न हो सकें तो अलग budget-matched contrasts दें। स्वतंत्र affinity evaluation की सीमाएं, leakage रोकथाम, तथा वास्तविक binding दावे के लिए वैकल्पिक assay validation बताएं। प्राथमिक endpoints और संयुक्त दावा स्वीकारने/अस्वीकारने के नियम, diversity non-inferiority margins तय करने की पूर्वनिर्धारित विधि, seed-level uncertainty और multiple comparisons योजना दें। प्रस्तावित replicate/sample counts तथा pilot-based precision या power योजना शामिल करें, लेकिन ज्ञात variance या पर्याप्त power का दावा न करें। सीमित-संसाधन core design और वैकल्पिक ablations/audit अलग दिखाएं।
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
प्रस्ताव में समान generator के A/B/C controls, स्वतंत्र evaluation, reference-calibrated chain metric, attempted-output denominators और seed-level analysis शामिल हैं। ये मूल प्रश्न के अनुरूप हैं। रिपोर्ट केवल निरीक्षण की है; कोई प्रयोग या लाभ का प्रमाण प्रस्तुत नहीं हुआ है। शेष अज्ञात बातें स्पष्ट प्रस्तावित choices के रूप में अंतिम डिज़ाइन में संबोधित की जा सकती हैं।
````

**Objectives Open**

````text
[
  "ठोस feedback intervention और budget-matched controls सहित अंतिम प्रयोग-डिज़ाइन",
  "पूर्वनिर्धारित endpoints, decision rules, uncertainty और sample-size योजना",
  "डेटा/संदर्भ चयन, स्वतंत्र validation तथा feasibility और सीमाएं"
]
````

### Event 4 — Actor

**Answer**

````text
# अंतिम प्रस्तावित प्रयोग-डिज़ाइन

**स्थिति:** यह design-only प्रस्ताव है। कोई molecule generation, docking, training या assay नहीं चलाया गया। नीचे चुना गया generator, target, reward और sampling protocol प्रस्तावित setup है, उपलब्ध स्रोतों से पुष्ट setup नहीं।

## 1. प्रश्न और attribution
मुख्य परीक्षण: **केवल chemical-property signals वाला feedback** क्या बिना feedback और समान scores से post-hoc selection के मुकाबले property scores सुधारता है, स्वतंत्र real-molecule reference के अधिक निकट जाता है, diversity बनाए रखता है और molecular hallucinations/बहुत लंबी chains घटाता है?

मुख्य feedback में novelty bonus, scaffold constraint, diversity reward, chain-length penalty, reference-distribution matching या molecular-size cutoff नहीं होगा। इससे alignment का लाभ किसी छिपे structural constraint को नहीं दिया जा सकेगा। QED स्वयं size/lipophilicity जैसी descriptors को शामिल करता है; अतः property-only का अर्थ structure से पूर्ण स्वतंत्रता नहीं है। इसे reward-mediated bias के रूप में स्पष्ट रिपोर्ट करेंगे।

## 2. प्रस्तावित generator, target और data

### Generator और update
- एक छोटा, लगभग 20–50M parameter का autoregressive SMILES Transformer; सामान्य molecule corpus पर next-token pretraining। सभी arms में समान checkpoint, tokenizer, decoding temperature और maximum token length। मुख्य तुलना में वही एक target रखा जाएगा और target conditioning सभी arms में समान होगी।
- यदि उपयुक्त pretrained weights उपलब्ध हों तो उनका उपयोग तभी, जब training-data provenance ज्ञात हो। अन्यथा corpus पर pretraining करना भविष्य के अध्ययन की अलग prerequisite है, सीमित-संसाधन core की उपलब्ध क्षमता का दावा नहीं।
- Feedback arm में छोटे batch REINFORCE updates, batch reward baseline और frozen base generator के प्रति KL regularization: `J = E[R(m)] − β KL(πθ || π0)`। आरंभिक प्रस्ताव `β=0.02`, batch 64, 32 updates; optimizer और learning rate development pilot में चुने और confirmatory generation से पहले freeze किए जाएँ। Reward gradients docking oracle से नहीं चाहिए। KL optimization-stability control है, chemical diversity reward नहीं।
- सभी arms unconstrained decoding करें; token-limit truncation को failure के रूप में गिनें। Maximum length और truncation rates प्रकाशित हों, क्योंकि token cap स्वयं extreme chains दबा सकता है।

### Target और data-selection protocol
**प्रस्तावित target: human dopamine D2 receptor (DRD2)।** यह चयन ligand data और receptor structures मिलने की संभाव्यता के कारण है, अभी उनकी उपलब्धता सत्यापित नहीं की गई।
1. अध्ययन शुरू होने पर ChEMBL जैसे curated source का version और extraction date freeze करें। Single-protein human DRD2 के direct-binding, high-confidence, exact-value Ki/Kd records लें; cellular IC50/EC50 को बिना रूपांतरण इनके साथ न मिलाएँ। Endpoint strata अलग रहें। Salt removal, charge/tautomer handling, stereochemistry और conflicting measurements का पूर्वनिर्धारित protocol लागू करें। एक standardized molecule का एक grouping identifier हो।
2. Broad reference: उसी provenance-compatible source से experimental small organic molecules; केवल high-QED/high-affinity molecules चुनने वाला filter नहीं। Target reference: quality criteria पार करने वाले सभी DRD2 binding-tested molecules, केवल actives नहीं। यह measured medicinal chemistry का reference है, पूरे प्राकृतिक chemical universe का unbiased प्रतिनिधि नहीं।
3. Target reference को scaffold-grouped development/calibration/evaluation partitions में बाँटें, और पर्याप्त dates हों तो newest temporal block evaluation के लिए रखें। Same molecule, salts, stereochemical variants और close analogues के overlaps दर्ज करें; analog grouping threshold development से पहले freeze करें। Pretraining corpus और reward-model training से evaluation identities/scaffold groups निकालें। इसके बाद ही checkpoint train या स्वीकार करें।
4. Calibration reference cutoff/margin तय करने के लिए है; evaluation reference final alignment के लिए अछूता रहे। Broad reference भी अलग held-out sample हो। Primary alignment population DRD2 binding-tested evaluation set होगा; broad-reference alignment secondary और अलग claim होगा।
5. Proposed docking receptor: ligand-bound human DRD2 structure, complete orthosteric pocket वाली highest-resolution eligible structure; ties के लिए deposition date का नियम। Exact structure ID, protonation, ligand-defined box और software versions main generation से पहले freeze हों। दूसरे suitable receptor conformation को independent evaluation के लिए आरक्षित रखें।

**Go/no-go:** यदि विश्वसनीय checkpoint provenance, adequate target-reference sample या independent evaluation data न मिलें, तो confirmatory run न करें। Target/data बदलने पर संशोधित protocol पहले पंजीकृत हो; खराब नतीजों के बाद target बदलना स्वीकार्य नहीं।

## 3. p-logP और property-only reward

**स्रोत में p-logP का अर्थ अज्ञात है।** इस मुख्य प्रस्ताव में operational convention के रूप में इसे **predicted octanol/water logP**, RDKit Crippen MolLogP, कहा जाएगा। यह मूल लेखक के अभिप्राय का दावा नहीं है।

वैध molecule के लिए:
- `rL = exp[−0.5(d(logP,[1,3])/1)^2]`, जहाँ interval के भीतर `d=0`; बाहर निकटतम सीमा से दूरी। यह प्रस्तावित drug-like preference है, DRD2 के लिए सिद्ध optimal range नहीं।
- `rQ = QED`, सीमा 0–1।
- `rA = clip((D90 − D)/(D90 − D10),0,1)`, जहाँ `D` frozen docking protocol का score है और lower is better। `D10,D90` केवल development/calibration ligands के docking quantiles हैं। Quantiles बराबर या docking uninformative हो तो protocol fail/revise करें।
- `R = (rL+rQ+rA)/3`। Invalid output पर `R=−1`; valid molecule की docking failure पर `rA=0`, साथ में अलग failure flag। Unknown docking को मनमाने favorable score से न भरें।

Property weights, clipping और normalization final outcomes देखकर नहीं बदलेंगे। Invalid-output handling representation feasibility है, कोई scaffold/chain preference नहीं। SA penalty मुख्य reward में नहीं है।

**यदि p-logP का आशय penalized logP निकलता है:** source equation और normalization प्राप्त करके एक अलग, पूर्वपंजीकृत reward arm में अपनाएँ। प्रचलित logP−SA−cycle-penalty रूप को बिना पुष्टि canonical न मानें। उसमें structural penalties निहित हों तो उसे वर्तमान property-only hypothesis के समान न कहें। LogP maximization और desirable-range optimization अलग hypotheses होंगी।

## 4. A/B/C arms, budgets और output accounting

| Arm | प्रक्रिया | क्या पहचानता है |
|---|---|---|
| A | Frozen base generator, chemical scores का update/selection में उपयोग नहीं | बिना feedback baseline |
| B | उसी generator पर ऊपर का property reward और REINFORCE | Embedded feedback का प्रभाव |
| C | Frozen base से candidates; वही reward लगाकर post-hoc ranking | Update के बजाय केवल oracle-guided selection का लाभ |

हर seed में A और B के **2,000 fresh attempted outputs** निकालें। C के लिए A की वही raw candidate pool इस्तेमाल की जा सकती है: C अलग trained model नहीं, selection policy है। Ranking invalids को नीचे रखे; ties का fixed random rule हो। Fixed 25% retention पर top 500 slots लें। A के random 500 slots selection-free control हैं; B के raw 2,000 और reward-ranked top 500 दोनों रिपोर्ट हों। Unique valid set 500 से छोटा हो तो उसे silently refill न करें—yield failure दिखाएँ।

मुख्य comparisons:
1. B-raw बनाम A-raw: generation distribution में बदलाव।
2. B-selected बनाम C-selected: समान final retention पर feedback का अतिरिक्त उपयोग।
3. C-selected बनाम A-random तथा B-selected बनाम B-raw: selection से कितना लाभ/विकृति आई।

**Budget fairness:** Training/update cost और oracle cost को एक साथ बराबर करने का झूठा दावा नहीं होगा।
- **Oracle-matched contrast:** B के update में 2,048 attempted proposals और terminal 2,000, कुल 4,048 proposal slots/seed। Frozen baseline को उतने ही proposals तथा अधिकतम उतने ही docking-call slots मिलें; C उस पूरी pool से top 500 दे। B अपनी terminal pool से top 500 दे; update samples से selection करना अलग secondary analysis होगा। Calls में failed calls/retries और cache hits अलग दर्ज हों; invalids को artificial docking calls से budget भरने की जरूरत नहीं। B के वास्तविक oracle खर्च से अधिक C को न दें।
- **Compute-matched contrast:** समान hardware पर B का actual adaptation+generation+scoring wall-time/CPU/GPU allocation budget हो। A/C उस budget तक sampling/scoring कर सकें। Pool sizes तब अलग हो सकती हैं; अंतिम selected count समान होगा। Random subsamples के equal-size distribution metrics साथ दें।
- स्वतंत्र evaluation-oracle खर्च intervention budget से बाहर, arms के लिए समान sampling नियम से हो। Pretraining sunk cost अलग प्रकाशित हो। Docking को cache करने के बावजूद duplicate generation attempts गिने जाएँ।

Core में oracle-matched contrast प्राथमिक होगा। Compute-matched contrast उसी अध्ययन में संभव हो तो करें; अन्यथा oracle-limited निष्कर्ष दें, compute efficiency का दावा नहीं।

## 5. Endpoints: अलग-अलग मापन

### A. Property improvement
प्राथमिक property endpoints:
1. Attempts पर mean bounded property utility, जिसमें invalid/failure को zero रखा जाए; valid-conditional mean अलग।
2. Independent affinity evaluation में matched-count difference।

Component-wise logP desirability, QED, reward docking, failures और quantiles अनिवार्य हों। संयुक्त reward बढ़ना सभी components बढ़ने का प्रमाण नहीं। यदि किसी component में meaningful degradation हो, तो रिपोर्ट केवल composite improvement की होगी। Heavy-atom count, formal charge और lipophilicity strata में affinity effects की secondary जाँच reward shortcuts उजागर करेगी; इन्हें मुख्य causal contrast का post-hoc replacement न बनाएँ।

**Independent affinity evaluation:** दूसरी docking engine/protocol और held-out receptor conformation, frozen before evaluation। पर्याप्त independent scaffold-held-out binding data मिले तो reward में न प्रयुक्त calibrated affinity predictor भी लगाएँ। Generated OOD structures पर applicability-domain flags दें। Docking engines आपस में correlated हो सकती हैं; दूसरी docking/QSAR agreement भी वास्तविक binding evidence नहीं है। Independent score model की measured-ligand validation असफल हो तो affinity endpoint exploratory होगा और पूर्ण affinity claim 'अनिर्णीत' होगा।

### B. Real-world distribution alignment
दो co-primary distances:
- Calibration-scaled physicochemical descriptors—MW, logP, QED, TPSA, HBD/HBA, rotatable bonds, charge, ring count और chain length—पर fixed-kernel MMD।
- Frozen Morgan fingerprints पर Tanimoto-kernel MMD।

Kernel settings calibration-only हों। Equal-size repeated subsampling और reference-vs-reference split distances से finite-sample bias दिखाएँ। प्राथमिक population target-tested reference होगी; broad reference secondary। Descriptor distance का कुछ हिस्सा reward से सीधे overlap करता है; fingerprint distance के बिना 'structural alignment' का दावा न करें। Valid molecules पर distances के साथ all-attempt validity/yield दें; filtering से सुधरे distance को raw generator की उपलब्धि न मानें।

### C. Diversity preservation
Co-primary:
- Unique-valid molecules/attempts।
- Equal-size unique-valid samples की mean pairwise Tanimoto distance।
- Equal-size samples की effective Bemis–Murcko scaffold count, `exp(Shannon entropy)`; acyclic/no-scaffold category अलग दर्ज करें।

Secondary: scaffold richness, nearest-training similarity, novelty, duplicate rates और size-stratified diversity। Finite-sample metrics के sample sizes हर arm में समान हों। यदि किसी arm में पर्याप्त unique-valid molecules नहीं हों तो यह yield failure है, चुपचाप बहुत छोटा common sample बनाकर preservation घोषित नहीं करेंगे।

### D. Hallucination और ultra-long chains
- **H1 hard failure:** SMILES parsing, graph sanitization या valence failure; rate/attempts। Truncation अलग subtype।
- **H2 plausibility alerts:** chemically valid graph पर पहले से freeze किए गए unstable/reactive/forbidden-valence-pattern alerts। PAINS अथवा synthetic-accessibility difficulty अकेले hallucination का प्रमाण नहीं; उन्हें अलग flags रखें। H2/attempts और H2/valid दोनों दें।
- Novel molecule, database से अनुपस्थिति या खराब predicted affinity को hallucination न कहें। Broad chemical plausibility reduction के लिए alert validation/expert audit चाहिए; core H1 claim को 'invalid-output reduction' तक सीमित रखेगा।
- **Chain length L:** ring atoms हटाने के बाद C–C induced acyclic subgraph का longest simple path, carbon atoms में; सभी C–C bond orders गिने जाएँ। Aromatic/ring traversal शामिल नहीं। Calibration target-reference में `T = 99th percentile(L)` freeze करें और `L>T` को ultra-long कहें। Tail rate, reference से excess rate, chain/heavy-atom ratio और absolute cutoffs 15/20/25 carbons पर sensitivity report हों; बाद वाले universal chemical truth नहीं हैं।
- Chain tail valid-conditional भी दें, ताकि invalid generation के कारण all-attempt tail कृत्रिम रूप से कम न दिखे।

## 6. Primary decision rules
Confirmatory परिवार में B-raw बनाम A-raw पर property utility, independent affinity, दोनों alignment distances, H1, chain-tail और तीन diversity-preservation endpoints आएँगे। पहले से दिशा और practically relevant thresholds freeze हों।

**पूरा संयुक्त operational दावा तभी स्वीकार होगा जब:**
1. Property utility और independent affinity proxy में सुधार के confidence bounds zero से बेहतर हों; अलग component losses छिपाए न जाएँ।
2. दोनों target-reference alignment distances घटें।
3. तीनों diversity endpoints अपने non-inferiority margins के भीतर हों।
4. H1 घटे और H2 में meaningful वृद्धि न हो। Expert validation न होने पर 'मolecular hallucination' के बजाय H1-specific wording हो।
5. यदि A में reference से chain over-representation मौजूद है तो B का excess घटे; यदि baseline में excess ही नहीं है तो reduction का दावा न करें, केवल no-emergent-excess की equivalence/non-inferiority जाँच करें।

यह intersection–union निर्णय है: सभी gates चाहिए। CI अनिर्णीत हो तो 'दावा स्थापित नहीं', दावा झूठा सिद्ध हुआ नहीं। स्पष्ट adverse bound संबंधित subclaim को खारिज करेगा। Independent evaluation न उपलब्ध हो तो पूर्ण दावा स्थापित नहीं होगा, भले reward बढ़े।

इसके बाद gated B-selected बनाम C-selected परीक्षण होगा। Selection-matched और oracle-matched तुलना में अतिरिक्त लाभ न मिले तो कहेंगे कि feedback ने base output बदला, पर post-hoc selection से बेहतर होने का प्रमाण नहीं। Broad-reference लाभ अलग बताया जाएगा। True binding improvement केवल assay evidence से।

### Diversity और अन्य preservation margins
Final data देखने से पहले calibration/reference resampling से natural between-sample variation निकालें। उसी n पर 1,000 independent equal-size resamples के metric differences का 95वाँ absolute percentile `v` लें। प्रस्तावित margin `δ=min(v, practical cap)`:
- unique-valid yield के लिए 2 percentage points का cap; reference valid-only होने से यह margin स्वतंत्र development baseline replicates से calibrate होगा;
- mean fingerprint distance के लिए 0.02 absolute;
- effective scaffold count के लिए 5% relative, log scale पर परीक्षण।

ये caps प्रस्तावित tolerances हैं, साहित्य से सत्यापित constants नहीं। Stakeholder स्वीकृति और freeze आवश्यक है। बहुत छोटा δ/ceiling variance हो तो preservation साबित करना कठिन माना जाए, margin बड़ा करके सुविधा न बनाएँ। H2/tail no-worsening caps अलग calibration में तय हों, प्रस्तावित upper caps क्रमशः 1 percentage point और 0.5 percentage point; zero-event स्थितियों में upper bounds दें।

## 7. Replicates, sample size और inference
- **Pilot:** दो अलग development seeds, लगभग 500 terminal outputs/arm/seed, अधिकतम आठ feedback batches। केवल numerical stability, time/oracle cost, failure rates और variance के planning estimates; pilot confirmatory evidence में शामिल नहीं।
- **प्रस्तावित core:** आठ स्वतंत्र adaptation/generation seeds, प्रत्येक 2,048 update proposals और 2,000 terminal attempted outputs per applicable arm। Same seed block में shared base और matched RNG streams जहाँ संभव हों; independence across seed blocks। Reference छोटा होने पर equal-size metric sample `n=min(1,000, eligible held-out reference size)` पहले freeze हो। Reference बहुत छोटा हो तो scale घटाने के बजाय go/no-go पुनरावलोकन करें।
- Independent costly affinity evaluation के लिए प्रत्येक seed/arm के raw तथा selected outputs से 200 random slots का predeclared subset, shared molecules का cached evaluation; cherry-picking नहीं। Large subsets का option pilot में cost देखकर freeze हो।
- Seed-level paired differences inference unit होंगे। Stratified/hierarchical resampling में seed blocks outer level, molecule/reference sampling inner level हो; molecule counts को independent training replicates न मानें। Small-seed limitations के कारण paired randomization/sign-flip sensitivity और individual-seed plots भी दें; eight seeds से uncertainty स्वतः छोटी नहीं होती। एक checkpoint पर नतीजे checkpoint-conditional हैं।
- **Precision/power planning:** pilot variance के conservative upper estimate से simulation या paired-difference calculation द्वारा detectable changes और CI widths प्रस्तुत करें। प्राथमिक target: preservation CI half-width लगभग δ/2 और superiority endpoints के stakeholder-chosen minimum relevant effect को discern करने योग्य precision। Prespecified विकल्प: seeds 8 से 12 या 16 बढ़ाना; generation noise मुख्य हो तो terminal n 2,000 से 5,000। अंतिम N और compute ceiling confirmatory outputs से पहले freeze हों। इस समय variance/power ज्ञात होने का दावा नहीं। Ceiling पर अपर्याप्त precision मिले तो अनिर्णीत निष्कर्ष स्वीकारें, favorable stopping नहीं।
- सभी primary constituent comparisons के लिए one-sided familywise 5% control, Holm adjustment तथा compatible adjusted confidence bounds; preservation को absence of significance से नहीं घोषित करें। Joint all-pass gate conservative होगा। B/C superiority परिवार पहली gate के बाद; secondary components/ablations के लिए अलग घोषित FDR नियंत्रण या स्पष्ट exploratory CIs।

## 8. Bias, leakage और failure controls
- Dataset hashes, versions, excluded overlaps, checkpoint provenance, reward code और receptor preparation freeze/archive करें। Unknown-pretraining contamination को resolved न बताएँ।
- Reference calibration/evaluation, reward fitting और evaluator validation की भूमिकाएँ अलग हों। Frozen evaluation distribution से reward weights, thresholds, decoding या target न चुनें।
- हर attempt का stage, parse result, duplicate identity, reward components, docking failure, selection status और resource counters log हों। Missing affinity पर favorable imputation न करें; missingness bounds और failure-as-unfavorable sensitivity दें।
- Docking redocking/enrichment checks तथा score-versus-heavy-atom-count relationship development में देखें। Reward saturation, extrapolation, size growth और chain-tail drift को seed-level diagnostics में प्रकाशित करें। Repeated docking of a small fixed ligand panel oracle stability जाँचेगा।

## 9. सीमित-संसाधन core और optional extensions

**Core:** एक target/checkpoint, A/B/C, property-only B, oracle-matched control, आठ seeds का provisional plan, graph/descriptor metrics, frozen reference, independent computational affinity subset। Existing checkpoint उपलब्ध होना आवश्यक है; docking calls की समय-लागत pilot से ही ज्ञात होगी। वर्तमान no-GPU/no-network environment में इसे चलाना न आवश्यक है, न यहाँ feasible होने का दावा किया जाता है। Pure graph/descriptor analyses CPU-compatible होंगे।

**Optional, अलग arms/budget:**
- Sham/permuted reward updates: optimization मात्र के प्रभाव का diagnostic, meaningful feedback का primary comparator नहीं।
- Individual reward-component removals तथा alternative weights; extra comparisons exploratory/gated।
- Explicit chain penalty, diversity bonus या distribution regularizer वाली B+structure arm। इसका लाभ property-only B को श्रेय नहीं दिया जाएगा।
- अन्य pretrained checkpoints और दूसरा target: generalizability, core claim की prerequisite नहीं।
- Blind expert plausibility audit: proposed 100 molecules/arm, alert-positive/negative तथा long-chain strata से sample, दो chemists और disagreement adjudication; population rates हेतु sampling weights।

**वैकल्पिक वास्तविक binding validation:** पहले feasibility/synthesis filter सभी arms पर समान, blind और predeclared हो। लगभग 24 molecules/arm में आधे ranked candidates और आधे random eligible outputs चुनें; acquisition/synthesis failures तथा tested-subset bias रिपोर्ट करें। DRD2 biochemical competition-binding assay से dose–response Ki/Kd-compatible endpoint, positive/negative controls, technical replicates, independent assay days और orthogonal confirmation करें। Aggregation/interference checks और relevant off-target counter-screen रखें। IC50 को Ki में केवल आवश्यक assay assumptions/constants उपलब्ध होने पर बदलें। Assay sample size अलग pilot-based planning माँगेगा; यह प्रस्ताव पर्याप्त power का दावा नहीं। Selected molecules का measured binding पूरे generator distribution की binding सिद्ध नहीं करेगा, और binding अपने-आप efficacy/selectivity नहीं है।

## 10. अनुमत निष्कर्ष
निष्कर्ष अलग clauses में होगा: generation property scores, independent affinity proxies, target-reference alignment, diversity preservation, graph-invalid outputs और chain tails। Joint claim तभी जब सभी relevant gates पास हों। Reward improvement अकेले chemical realism नहीं; computational affinity agreement अकेले binding नहीं; चुने target/reference पर सफलता सभी real-world molecular distributions पर सफलता नहीं।
````

**Stage**

````text
result
````

**Evidence**

````text
Repository inspection में केवल /workspace/task.json मिला; उसमें मूल प्रश्न और design-only निर्देश हैं। documents.track.md का inline पाठ कहता है कि repositories और compute आवश्यक नहीं हैं; कोई अलग source document, implementation, molecular dataset, target structure या reward formula उपलब्ध नहीं मिला। सीमित filesystem check ने इसी एक file की पुष्टि की; कोई वैज्ञानिक experiment नहीं चलाया गया। उपयोगकर्ता ने A/B/C controls, raw/selected separation, अलग endpoints और final design पर स्पष्ट स्वीकृति दी। इसी कारण generator, DRD2, REINFORCE, predicted-logP convention, reward weights, thresholds और counts को प्रस्तावित choices के रूप में रखा गया है। A/B/C attribution, independent evaluation, held-out references, seed-level inference और explicit structural-penalty exclusion मूल प्रश्न के causal तथा distributional भागों को अलग करते हैं; ये repository में स्थापित results नहीं हैं।
````

**Assumptions**

````text
[
  "भविष्य के अध्ययन में known-provenance SMILES generator/checkpoint तथा उपयुक्त cheminformatics/docking software प्राप्त होंगे; वर्तमान environment में वे सत्यापित नहीं हैं।",
  "Human DRD2 के sufficiently curated binding records और eligible receptor structures उपलब्ध हो सकेंगे; exact versions/IDs data-selection protocol के बाद freeze होंगे।",
  "मुख्य operational p-logP definition predicted Crippen logP है; स्रोत का अभिप्राय अज्ञात है।",
  "Reward weights, desirable logP interval, provisional sample counts, diversity caps और update hyperparameters प्रस्तावित पूर्वपंजीकरण choices हैं, fixed task requirements या ज्ञात optimum नहीं।",
  "आठ seeds और दिए counts प्रारंभिक feasibility targets हैं; precision/power स्वतंत्र pilot पर निर्भर होगी।",
  "Fixed task requirement experiment design है, न execution और न अपेक्षित लाभ की पुष्टि।"
]
````

**Uncertainties**

````text
[
  "Independent docking तथा affinity predictor समान biases साझा कर सकते हैं; assays के बिना वास्तविक binding claim नहीं होगा।",
  "Target-tested reference medicinal-chemistry selection bias रखता है और सार्वभौमिक real-world distribution नहीं है।",
  "Unknown pretraining provenance या अपर्याप्त held-out scaffold coverage मिलने पर confirmatory claim रोकना या संशोधित करना पड़ेगा।",
  "Oracle-call और compute budgets सामान्यतः एक साथ बराबर नहीं होंगे; contrasts और resource-specific निष्कर्ष अलग हैं।",
  "Reward optimization QED, size, lipophilicity अथवा docking shortcuts exploit कर सकती है; property-only feedback का लाभ अनुमानित नहीं माना गया है।",
  "Zero baseline hallucinations/chain excess, छोटे reference या कड़े preservation margins के कारण reduction/preservation अनिर्णीत रह सकते हैं।"
]
````

### Event 5 — Simulator

**Message**

````text
अंतिम डिज़ाइन इस design-only कार्य की अपेक्षाएं पूरी करता है: rationale, A/B/C controls, स्वतंत्र मूल्यांकन, distribution और diversity मापन, seed-level analysis तथा feasibility स्पष्ट हैं। इसे अंतिम deliverable मानें। प्रस्तावित setup और अज्ञात स्रोत-अर्थ अलग रखे गए हैं; किसी प्रयोग या लाभ की पुष्टि का दावा नहीं है। निष्कर्ष चुने हुए target/reference और computational proxies तक सीमित रहें; वास्तविक binding तथा व्यापक chemical plausibility के दावों के लिए वर्णित अतिरिक्त validation आवश्यक होगा।
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
प्रस्तुत अंतिम उत्तर में property-only feedback और structural penalties का पृथक्करण, raw/selected तथा oracle/compute-budget contrasts, held-out references, chain और invalid-output definitions, non-inferiority योजना, multiplicity control, pilot-based sampling और संसाधन-सीमाएं शामिल हैं। उपलब्ध सामग्री प्रयोग-डिज़ाइन है, निष्पादित परिणाम नहीं; यही submission contract है।
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
  "event_log": "runs/openai-astra-top10-trial-1-batch-2/episodes/expbench_iclr2024_19281_1-0aedaf6a9390/candidate_001/attempt-1/output/iclr2024__19281__1/events.jsonl",
  "event_log_sha256": "56c58193f4758a008ee0555d6082850056e791b69b7fdd757149250cd30a178d",
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
