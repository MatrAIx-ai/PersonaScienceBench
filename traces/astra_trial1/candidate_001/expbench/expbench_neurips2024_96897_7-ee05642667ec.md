# candidate_001 · expbench · neurips2024/96897/7

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **50/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
पहले उपलब्ध निर्देशों और इनपुट का निरीक्षण करें और संक्षिप्त प्रस्तावित दृष्टिकोण दें; अभी पूरा प्रयोग-डिज़ाइन नहीं चाहिए। प्रश्न है: MathInstruct पर Llama 3-70B को finetune करने पर क्या BAdam, LoRA से बेहतर zero-shot math प्रदर्शन देगा? यह design-only कार्य है; repository, डेटा या GPU जुटाना और प्रयोग चलाना आवश्यक नहीं है। बताएं कि निष्पक्ष तुलना, benchmark चयन, डेटा-overlap नियंत्रण, zero-shot मूल्यांकन, अनिश्चितता का विश्लेषण और संसाधन-व्यवहार्यता को कैसे संभालने का प्रस्ताव है। मॉडल संस्करण, BAdam की परिभाषा/configuration, LoRA setup और समान training-data बनाम समान compute बजट जैसे परिणाम बदल सकने वाले विकल्पों को स्पष्ट करें। उपलब्ध तथ्य, आपके प्रस्ताव और अज्ञात बातें अलग रखें; किसी अपेक्षित विजेता या unstated budget को तथ्य न मानें।
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
उपलब्ध brief केवल शोध-प्रश्न और design-only deliverable तय करता है। track.md के अनुसार repositories और compute आवश्यक नहीं हैं; अभी कोई प्रस्ताव या परिणाम प्राप्त नहीं हुआ है।
````

**Objectives Open**

````text
[
  "उपलब्ध इनपुट और सीमाओं का निरीक्षण",
  "तुलना के लिए प्रस्तावित दृष्टिकोण की समीक्षा",
  "महत्वपूर्ण मान्यताओं और अनिश्चितताओं की पहचान",
  "अंततः rationale, controls, analysis plan और feasibility सहित प्रयोग-डिज़ाइन"
]
````

### Event 2 — Actor

**Answer**

````text
**उपलब्ध तथ्य:** कार्य Llama 3-70B को MathInstruct पर finetune करके BAdam और LoRA के zero-shot math प्रदर्शन की तुलना का डिज़ाइन बनाना है। उपलब्ध workspace में केवल `task.json` है; उसमें embedded `track.md` स्पष्ट करता है कि repository/compute जुटाना आवश्यक नहीं। implementation, model revision, training configuration या परिणाम उपलब्ध नहीं हैं। अभी किसी विजेता का निष्कर्ष नहीं निकाला जा सकता।

**प्रस्तावित दृष्टिकोण—अनुमोदन के लिए, पूरा डिज़ाइन नहीं:**
1. **तुलना की परिभाषा पहले तय करें।** प्राथमिक प्रस्ताव original Meta Llama 3-70B **base** का एक pinned revision है, न कि Llama 3.1 या 70B-Instruct; Instruct चुनने पर अलग प्रश्न/अध्ययन होगा। BAdam को block-wise Adam full-parameter fine-tuning के रूप में operationalize करने से पहले उसका source/version सत्यापित करेंगे: block partition, सक्रिय block का आकार, switching interval/order, optimizer-state handling और Adam hyperparameters दर्ज होंगे। LoRA में rank, alpha, dropout, target modules, trainable exceptions और underlying optimizer स्पष्ट होंगे। दोनों में समान backbone precision रखें; quantized LoRA को चुपचाप LoRA का विकल्प न बनाएं। यह दो training recipes की तुलना होगी, optimizer का शुद्ध isolated causal test नहीं।
2. **निष्पक्षता के दो अलग estimands रखें।** प्राथमिक प्रस्ताव समान cleaned training examples/token exposure, tokenizer, sequence length, loss masking, effective batch और data order पर तुलना है। हर विधि को उसके लिए उपयुक्त learning-rate/configuration tuning दें, लेकिन समान पूर्वनिर्धारित search allowance और validation-only selection रखें। द्वितीयक, बजट अनुमति दे तो, समान hardware पर समान training GPU-hours की तुलना करें; tuning लागत अलग रिपोर्ट करें। समान डेटा और समान compute स्वतः समान नहीं होते। कोई budget अभी मानकर नहीं चलेंगे।
3. **Benchmark और overlap नियंत्रण।** उम्मीदवार GSM8K तथा MATH के आधिकारिक held-out test splits हैं; इन्हें MathInstruct के चुने गए revision/source inventory की जांच के बाद अंतिम करें। पहले training के भीतर तथा training–validation–test के बीच normalized exact और near-duplicate प्रश्न, variants और साझा solutions की जांच करें; संदिग्ध matches की adjudication तथा हटाए गए counts दर्ज करें। प्राथमिक training set से benchmark-overlapping items हटाएं, benchmark test को यथासंभव स्थिर रखें। यदि raw MathInstruct भी परखना हो तो उसे contamination-संवेदनशील secondary analysis कहें। Benchmark coverage के आधार पर complementary test चुन सकते हैं; pretrained model का अज्ञात contamination पूरी तरह हटाने का दावा नहीं होगा।
4. **Zero-shot को lock करें।** एक ही non-demonstration instruction/prompt, बिना few-shot examples, retrieval या external tools, समान deterministic decoding तथा generation budget का प्रस्ताव है। Reasoning मांगा जा सकता है, पर worked examples नहीं दिए जाएंगे। Answer extraction/equivalence नियम पहले तय करें; invalid outputs को असफल मानें। Untuned base checkpoint भी उसी harness से चलाने का प्रस्ताव है। Test results से prompt या checkpoint न चुनें।
5. **अनिश्चितता और निर्णय।** पहले primary metric—प्रस्तावित benchmark-wise accuracy का समान-भार macro-average—और practically meaningful improvement threshold तय करें; individual benchmark scores भी दें। संसाधन अनुमति पर कई training seeds, paired item-level comparison तथा seed और item variability को अलग दर्शाने वाले confidence intervals प्रस्तावित हैं। सीमित seeds पर निष्कर्ष की सीमा स्पष्ट होगी; inconclusive परिणाम स्वीकार्य है। Secondary comparisons को exploratory बताएं या multiplicity नियंत्रित करें।
6. **व्यवहार्यता।** अनुमोदित design में memory/compute worksheet जोड़ेंगे: weights, gradients, सक्रिय optimizer states, activations, LoRA adapters, sharding/offload, checkpointing और throughput assumptions। 70B मॉडल को केवल parameter-efficient या block-wise training कह देने से उपलब्ध memory में फिट मानना अनुचित होगा। वास्तविक hardware/budget मिलने पर छोटे pilot feasibility checks सुझाए जाएंगे; इस design-only कार्य में उन्हें चलाना आवश्यक नहीं।

**मुख्य अनुमोदन/स्पष्टीकरण:** क्या base original Llama 3-70B और equal-data प्राथमिक तुलना स्वीकार्य हैं? क्या BAdam का इच्छित source/config तथा MathInstruct revision निर्दिष्ट है? उपलब्ध budget/hardware ज्ञात हो तो उसके अनुसार equal-compute arm, tuning और seeds प्रस्तावित किए जाएंगे; अन्यथा इन्हें स्पष्ट conditional विकल्प रखेंगे। आपके अनुमोदन के बाद ही पूरा डिज़ाइन विकसित करूंगा।
````

**Stage**

````text
plan
````

**Evidence**

````text
inspect_repository से workspace में केवल task.json मिला। उसमें प्रश्न और embedded documents.track.md = 'Design-only task; repositories and compute are not required.' है। छोटे Python metadata check ने यही inventory पुष्ट की और बताया कि अलग track.md file मौजूद नहीं है। कोई implementation/config या dataset workspace में नहीं मिला। उपयोगकर्ता के supplied environment के अनुसार network disabled, GPU अनुपलब्ध और datasets सूची खाली है; training/evaluation नहीं चलाई गई।
````

**Assumptions**

````text
[
  "Original Llama 3-70B base को primary backbone रखना प्रस्ताव है, निश्चित task requirement नहीं।",
  "Equal-data primary तथा equal-compute optional secondary comparison प्रस्तावित हैं, स्वीकृत budget नहीं।",
  "GSM8K/MATH, BF16-जैसी साझा precision, multiple seeds और metric aggregation के अंतिम विकल्प source audit, अनुमोदन और व्यवहार्यता पर निर्भर होंगे।"
]
````

**Uncertainties**

````text
[
  "BAdam का intended implementation/version तथा block/state configuration निर्दिष्ट नहीं है।",
  "MathInstruct revision, preprocessing, overlap और exact model checkpoint अज्ञात हैं।",
  "LoRA rank/target modules तथा tuning, hardware और compute budget निर्दिष्ट नहीं हैं।",
  "Benchmark pretraining contamination पूर्णतः निरीक्षण योग्य नहीं हो सकता; actual performance और विजेता अज्ञात हैं।"
]
````

### Event 3 — Simulator

**Message**

````text
प्रस्ताव स्वीकृत है। अब rationale, controls, analysis plan और feasibility सहित अंतिम प्रयोग-डिज़ाइन दें; कोई प्रयोग चलाना आवश्यक नहीं है। Original Llama 3-70B base और equal-data प्राथमिक तुलना को इस अध्ययन के चुने हुए विकल्प मानें, मूल स्रोत की पुष्ट मंशा नहीं। GSM8K तथा MATH के आधिकारिक test splits का समान-भार macro-average प्राथमिक endpoint रखें; equal-compute तुलना optional secondary रहे। BAdam source/config, MathInstruct revision और hardware budget के बारे में कोई अतिरिक्त जानकारी उपलब्ध नहीं है; इन्हें अज्ञात बताएं और execution से पहले version-pinning तथा implementation verification की शर्त लिखें।

अंतिम डिज़ाइन को क्रियान्वयन योग्य बनाने के लिए स्पष्ट प्रस्तावित defaults या सीमित search space दें: BAdam blocks/switching/state handling, LoRA rank/targets, learning rates, training exposure, batch/sequence length, validation split, समान tuning allowance और checkpoint-selection नियम। समान exposure की तुलना में checkpoint चयन से अलग training budgets न बनें। MathInstruct की reasoning/code विविधता के लिए preprocessing और tool-free evaluation की संगति समझाएं। Overlap हटाने के नियम, fixed zero-shot prompt/decoding/scoring, untuned baseline और test से tuning न करने के नियंत्रण शामिल रखें।

Training seeds की प्रस्तावित संख्या, paired seed/item uncertainty की गणना, व्यावहारिक सुधार का प्रस्तावित threshold तथा superiority/inconclusive निर्णय-नियम स्पष्ट करें; benchmark-विशिष्ट जीत और aggregate जीत अलग हों। Memory/compute का अनुमान assumptions सहित दें और संभावित multi-GPU व्यवस्था को उपलब्ध संसाधन न बताएं। छोटे feasibility pilots केवल भविष्य की शर्त रहें। निष्कर्ष स्पष्ट हो कि यह डिज़ाइन प्रश्न का परीक्षण करेगा, अभी किसी विधि की श्रेष्ठता स्थापित नहीं हुई है।
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
एजेंट की रिपोर्ट में design-only निर्देश, अनुपलब्ध implementations/data और कोई training न चलने की स्थिति स्पष्ट है। प्रस्ताव समान-data तथा समान-compute प्रश्नों को अलग रखता है और contamination, zero-shot नियंत्रण, validation-only tuning तथा seed/item uncertainty को संबोधित करता है। मुख्य दृष्टिकोण उपयुक्त है; अंतिम deliverable में अब ठोस प्रस्तावित configurations और निर्णय-नियम चाहिए।
````

**Objectives Open**

````text
[
  "अंतिम प्रयोग-डिज़ाइन और rationale",
  "ठोस training/tuning configurations तथा तुलना के controls",
  "प्राथमिक endpoint, uncertainty और निर्णय-नियम",
  "संसाधन assumptions सहित feasibility और सीमाएं"
]
````

### Event 4 — Actor

**Answer**

````text
# अंतिम प्रयोग-डिज़ाइन

## 1. प्रश्न, अध्ययन के चुने हुए विकल्प और सीमा
क्या MathInstruct पर समान training-data exposure देकर finetune करने पर BAdam, LoRA से बेहतर zero-shot math accuracy देता है?

इस अध्ययन के **स्वीकृत विकल्प** original **Meta Llama 3-70B base**, equal-data प्राथमिक तुलना, और **GSM8K तथा MATH के आधिकारिक test splits की accuracy का समान-भार macro-average** हैं। ये मूल स्रोत की पुष्ट configuration नहीं हैं। Equal-compute तुलना optional secondary है। यह दो training recipes का परीक्षण है—सिर्फ optimizer के प्रभाव का पृथक causal परीक्षण नहीं, क्योंकि trainable parameterization भी अलग होगी।

अभी BAdam implementation/config, MathInstruct revision और hardware budget अज्ञात हैं। किसी training या evaluation के निष्पादन अथवा किसी विधि की श्रेष्ठता का दावा नहीं किया जा रहा है।

## 2. निष्पादन-पूर्व अनिवार्य specification gate
निम्न manifest को training शुरू होने से पहले freeze करें:
- Model/tokenizer का exact identifier, revision और file hashes; original Llama 3-70B **base**, न कि 3.1 या Instruct।
- MathInstruct snapshot/hash, source labels, schema, preprocessing तथा deduplication manifest।
- GSM8K/MATH releases, official split identifiers, scoring library/version और test counts।
- BAdam source URL/commit, license, algorithm तथा distributed implementation; LoRA/optimizer/framework versions; precision, kernels और hardware topology।
- सभी prompts, configurations, seeds, selection rules और statistical analysis script specification।

BAdam के नाम मात्र से algorithm मान्य न मानें। Source inspection और छोटे भविष्य के correctness checks से active/frozen parameters, switching, optimizer moments, bias-correction counters, gradient accumulation और distributed synchronization सत्यापित करें। नीचे के defaults **प्रस्तावित executable configuration** हैं, verified source facts नहीं। यदि intended BAdam source उनसे असंगत हो, तो implementation-संगत बदलाव दोनों विधियों के test खोलने से पहले amendment में दर्ज करें; silently अलग algorithm को BAdam न कहें।

## 3. डेटा और contamination नियंत्रण
### Preprocessing
1. Source metadata सुरक्षित रखकर प्रत्येक valid sample को question तथा supervised response में बदलें। समान fixed training wrapper रखें:
   `Question: {question}\nAnswer: {response}`
   Question/wrapper पर loss mask और response सहित EOS पर loss रखें। दोनों विधियों में tokenizer, masking और batching समान हों।
2. MathInstruct की प्राकृतिक-language reasoning और code/program-containing responses दोनों रखें। Code न चलाएं, synthetic chain-of-thought न बनाएं और code से answer निकालकर dataset को चुपचाप न बदलें। Malformed/empty question या response हटाएं। Source तथा response type के counts प्रकाशित करें।
3. Maximum sequence length 4,096 tokens रखें। इससे लंबे पूरे examples को दोनों arms से हटाएं, न कि response को बीच में काटें; हटाए गए अनुपात/source mix रिपोर्ट करें। यह परिणाम filtered MathInstruct पर लागू होगा। अत्यधिक filtering मिलने पर training से पहले common length बदलने का documented feasibility amendment हो सकता है।
4. Default में packing बंद, dynamic padding और per-example attention isolation रखें। Padding loss में शामिल न हो। इससे दोनों विधियों को समान actual supervised tokens मिलेंगे।

### Overlap protocol
- Training के भीतर तथा train/validation/test के बीच normalized question exact matching करें: Unicode, whitespace, formatting और LaTeX wrapper normalization; संख्याएं, operators और महत्वपूर्ण mathematical content न हटाएं।
- Near-duplicate candidates के लिए normalized token 5-gram Jaccard ≥0.80 प्रस्तावित threshold है। समान equations/numbers, renamed entities, partial question copying और shared solution text से अतिरिक्त candidates flag करें। Threshold एवं normalization को training-only duplicate examples से जांचकर test-result inspection से पहले freeze करें।
- Flagged pairs का method-blind manual adjudication करें। केवल समान विषय/सामान्य solution phrase के लिए removal नहीं; वही mathematical instance, answer-revealing variant, या substantial copied solution होने पर overlap मानें। निश्चित और unresolved plausible leakage वाले training items conservatively निकालें और category-wise counts दें।
- Official benchmark tests अपरिवर्तित रखें; removal training pool से हो। Test से overlap पहचानना अनुमति-प्राप्त contamination audit है, test correctness के आधार पर filtering या tuning नहीं। GSM8K–MATH के बीच duplicates भी audit करें; primary endpoint में official splits बनाए रखें और मिले duplicates पर sensitivity analysis दर्ज करें।
- बची training duplicate clusters से एक canonical item रखें। फिर source/response-type stratified, cluster-grouped deterministic **98% training / 2% validation** split करें। एक cluster दो partitions में न जाए। उसी validation पर दोनों विधियों का selection करें।
- Test-overlap audit के लिए labels देखने वाले curator और tuning analyst की भूमिकाएं जहां संभव हो अलग रखें। इससे hidden pretraining contamination समाप्त नहीं होती; उसकी सीमा स्पष्ट लिखें।

### Tool-free evaluation से संगति
Training में code-containing responses रखना MathInstruct के उपलब्ध supervision mix का हिस्सा है, external tool access नहीं। Evaluation में interpreter/tool कभी नहीं मिलेगा और executable code मात्र को सही उत्तर नहीं मानेंगे। अतः परिणाम dataset के इस मिश्रित supervision से **tool-free mathematical answer generation** पर transfer मापेगा। Natural-language-only dataset ablation चाहें तो बाद में अलग exploratory arm हो, primary comparison में न मिलाएं।

## 4. Primary training protocol
### साझा defaults
- Backbone एवं forward/backward computation BF16; कोई backbone quantization नहीं। Optimizer moments और आवश्यक numerical accumulations FP32। Distributed layout दोनों में जहां संभव हो समान रखें और अंतर दर्ज करें।
- Training exposure: cleaned training partition के **दो पूर्ण epochs**, हर run में वही examples और non-padding token exposure। Effective batch **64 examples**, microbatch **1 example/GPU**, gradient accumulation से effective batch पूरा करें। अंतिम partial batch retain करें; loss normalization और schedule denominator समान हों।
- Adam-family common settings: β₁=0.9, β₂=0.999, ε=1e−8; weight decay 0; global gradient norm clipping 1.0; first 3% optimizer updates linear warmup, फिर cosine decay से अंतिम LR=peak LR का 10%। LR schedule global updates पर चले।
- Activation checkpointing और memory-efficient attention दोनों में enabled। Gradient accumulation के बीच BAdam block न बदलें।
- Exact example order, dropout RNG policy और initialization seeds manifest में हों। प्रत्येक paired run में same data-order seed हो; method-specific randomness अलग substream में रहे।

### BAdam प्रस्तावित defaults/search
- सभी backbone parameter groups training के दौरान update के पात्र हों, पर एक समय पर **एक block** सक्रिय हो। प्रत्येक transformer layer एक block; embeddings और output head अलग blocks; final normalization अंतिम layer block में। Tied/shared tensors को source/model inspection के बाद ठीक एक group में रखें।
- Cyclic deterministic block order; seed से starting offset चुनें और record करें। हर switch के बाद अगले block पर जाएं।
- **Inactive parameters frozen; inactive gradients तथा optimizer states GPU पर न रखें।** प्रस्तावित state policy: block छोड़ने पर moments discard; activation पर zero moments और block-local Adam step counter reset; global scheduler reset न हो। यह source verification का विशेष gate है—persistent moments वाली implementation से इसे समतुल्य न कहें।
- Peak LR ∈ **{5e−6, 1e−5, 2e−5}**; switch interval ∈ **{50, 100 optimizer updates}**: कुल **6 configurations**।
- Training-step count निकालकर पहले जांचें कि हर candidate में प्रत्येक block कम से कम एक बार सक्रिय होगा। यदि दो epochs में पूरा cycle भी संभव न हो, intervals को common shorter pair में पूर्व-पंजीकृत amendment से बदलें; unvisited blocks वाला run full-model blockwise tuning के रूप में न पेश करें। प्रति-block updates प्रकाशित करें।

### LoRA प्रस्तावित defaults/search
- Backbone frozen; attention `q_proj, k_proj, v_proj, o_proj` तथा MLP `gate_proj, up_proj, down_proj` पर adapters; exact module names model inspection से सत्यापित करें। Embeddings, head, normalization तथा biases frozen।
- Rank ∈ **{16, 64}**, alpha=2×rank, dropout=0.05; standard LoRA scaling alpha/r और standard zero initial adapter contribution। Optimizer केवल adapter parameters पर AdamW, ऊपर के common moment settings/zero decay के साथ।
- Peak LR ∈ **{5e−5, 1e−4, 2e−4}**: कुल **6 configurations**। QLoRA/DoRA को इस arm का विकल्प न बनाएं।

### समान tuning allowance और checkpoint selection
- प्रति विधि **6 full-exposure tuning runs**, एक common tuning seed **11**; प्रत्येक run दो पूरे epochs। यह समान configuration-count और data exposure allowance है, समान GPU-hours नहीं। Failed runs/resource errors और retry लागत भी log करें।
- Validation selection metric: source-macro-averaged supervised response token NLL; lower is better। Code responses पर unreliable answer extraction को selection criterion बनाने से बचने के लिए NLL चुना गया है। यह downstream accuracy का अपूर्ण proxy है; वही proxy दोनों arms में लागू होगा।
- **केवल अंतिम two-epoch checkpoint eligible है**। Intermediate checkpoints recovery/diagnostics के लिए, early stopping या best-epoch selection के लिए नहीं। इससे selection द्वारा training exposure नहीं बदलता। Tie पर पहले से सूचीबद्ध configuration order उपयोग करें। Test metric या test-derived prompt tuning निषिद्ध है।
- चुने हुए configuration से प्रत्येक विधि के **5 नए runs**, paired seeds **101, 202, 303, 404, 505**। Hyperparameters final seeds में पुनः tune न करें।
- कुल प्रस्तावित training workload: **12 tuning + 10 final = 22 runs**। Budget कम होने पर पहले protocol संशोधन हो; बाद में चुपचाप seed count घटाकर वही evidential claim न करें।

## 5. Fixed zero-shot evaluation
सभी final checkpoints और **untuned original base checkpoint** पर ठीक समान harness चलाएं। Base model के लिए chat template न जोड़ें। Fixed prompt:

`Solve the following mathematics problem. Show your reasoning without using external tools or code execution. End with exactly one line of the form Final answer: <answer>.\n\nQuestion: {question}\nAnswer:`

- कोई demonstrations, retrieval, calculator, code execution, self-consistency या resampling नहीं। Greedy decoding, sampling off, max_new_tokens=2,048; EOS पर रोकें। Prompt और generation को समाहित करने वाला context limit verify करें; long-item policy test चलने से पहले freeze करें।
- प्रत्येक item पर एक output: pass@1 accuracy। Length-limited, refusal, empty और unparseable outputs गलत गिने जाएं; rate अलग दें।
- Predetermined extraction: अंतिम `Final answer:` line; वह न हो तो अंतिम well-formed boxed answer। Ambiguous multi-answer outputs को incorrect मानें; method-specific repair या retry नहीं।
- GSM8K: official numeric answer के विरुद्ध exact rational/decimal normalization; harmless commas/currency formatting हटाएं, arbitrary numeric tolerance नहीं। MATH: pinned deterministic mathematical-equivalence scorer; symbolic expressions को timeout-सहित sandbox में जांचें, model-generated code execute न करें। Scorer failure को incorrect और अलग count करें।
- Extraction/scorer को synthetic cases और training/validation examples पर पहले test करें। Human correctness overrides प्राथमिक score में न हों। Error audit method-blind और secondary हो।
- MATH subject/difficulty, response-format errors तथा generation lengths secondary diagnostics हैं। Test से tuning न हो; frozen artifacts के बाद ही test evaluation शुरू हो।

## 6. Endpoint, uncertainty और निर्णय
प्रत्येक seed s के लिए:

`Δ_s = 0.5 × [(Acc_BAdam,GSM8K,s − Acc_LoRA,GSM8K,s) + (Acc_BAdam,MATH,s − Acc_LoRA,MATH,s)]`.

Primary estimate पांच paired seeds का mean Δ है, **percentage points (pp)** में। उदाहरण के लिए 1 pp absolute improvement है, 1% relative नहीं। सभी seed scores, benchmark-specific means, baseline gains और item counts दें।

### Paired uncertainty
- **10,000 crossed paired-bootstrap replicates**: पांच seed pairs को replacement के साथ sample करें; प्रत्येक benchmark के test items को स्वतंत्र replacement sampling दें। किसी replicate में sampled items सभी sampled seeds और दोनों methods के लिए समान हों; pairing कभी न तोड़ें। Seed pairs को दोनों benchmarks में भी समान रखें। इससे item तथा training-seed variation दोनों शामिल होंगे।
- Exact/near-duplicate test groups हों तो item की जगह audit में frozen clusters resample करें और item-weighted accuracy बनाए रखें। Primary benchmark macro weights हमेशा 1/2 रहें।
- Bootstrap Δ distribution से two-sided percentile **95% CI** दें। साथ में item-only bootstrap, पांच paired Δ_s की SD/range और seed-only paired-t interval sensitivity दें। पांच seeds में tail uncertainty कमजोर हो सकती है; disagreement छिपाएं नहीं।
- यह interval चुने हुए configurations और एक tuning search पर conditional है; repeated hyperparameter-search uncertainty या सभी संभावित math benchmarks पर generalization नहीं मापता।

### पूर्वनिर्धारित निर्णय
व्यावहारिक superiority margin **δ=+1.0 pp** प्रस्तावित है।
- Primary CI का lower bound **>+1.0 pp**: इस protocol पर BAdam की practically meaningful aggregate superiority का समर्थन।
- Lower bound **>0**, लेकिन ≤+1.0 pp: positive aggregate difference का समर्थन, पर निर्धारित practical superiority स्थापित नहीं।
- CI में 0: direction पर inconclusive; `not significant` को equivalence न कहें।
- Upper bound <0: LoRA-पक्षीय difference; upper bound <−1.0 pp होने पर उसी margin पर practical LoRA superiority।
- Entire CI [−1,+1] के भीतर हो तो practically small difference की संगति नोट करें; औपचारिक equivalence claim अलग पूर्वनिर्धारित परीक्षण के बिना न करें।

GSM8K और MATH की अलग जीत aggregate जीत नहीं है। Individual estimates/95% CIs descriptive दें; benchmark-specific confirmatory claims चाहिए हों तो दोनों contrasts के लिए Bonferroni-adjusted **97.5% two-sided CIs** उपयोग करें। Aggregate जीत पर भी दोनों में जीत घोषित न करें।

## 7. संसाधन-व्यवहार्यता और optional equal-compute arm
### अनुमान—उपलब्ध hardware का दावा नहीं
- 70B parameters ×2 bytes ≈ **140 GB decimal** केवल BF16 weights। पूर्ण gradients BF16 में लगभग 140 GB; पूर्ण FP32 Adam moments लगभग 560 GB; FP32 master weights लागू हों तो अतिरिक्त 280 GB। इसलिए conventional fully resident Adam लगभग 0.84–1.12 TB model/optimizer state तक पहुंच सकता है, activations/communication के बिना।
- BAdam में यदि active block ~0.8–1.0B parameters का हो, तो BF16 gradient ~1.6–2 GB, FP32 moments ~6.4–8 GB तथा optional active FP32 master copy ~3.2–4 GB होंगे। ये rough assumptions हैं; embeddings/head सहित **सबसे बड़ा वास्तविक block** manifest से निकालना जरूरी है। Full persistent master copies या source द्वारा retained states होने पर memory बहुत बढ़ सकती है।
- LoRA trainable count exact shapes से `Σ r(d_in+d_out)` निकालें। Llama-जैसे 70B dimensions तथा ऊपर के seven targets के rough उदाहरण में rank 16/64 पर लगभग 0.21/0.83B adapter parameters हो सकते हैं; actual config से पुनर्गणना अनिवार्य है। Parameters, gradients, moments और possible masters का लगभग 12–16 bytes/trainable-parameter footprint क्रमशः ~2.5–3.3 / 10–13.3 GB है, base weights और activations अलग।
- Sequence length 4,096 के activations, temporary all-gathers, attention workspaces, fragmentation और communication buffers अभी अज्ञात हैं। Frozen base होने से सभी activation/backprop costs समाप्त नहीं होते।
- **उदाहरण candidate**, उपलब्ध व्यवस्था नहीं: 8×80-GB GPUs, BF16, activation checkpointing तथा verified FSDP/ZeRO-style weight sharding। Model state पर्याप्त रूप से shard होने, largest block/gather fit होने और bandwidth स्वीकार्य होने की जांच चाहिए; fit/throughput का आश्वासन नहीं। BAdam का dynamic freezing distributed optimizer के साथ विशेष compatibility जोखिम है।

### Compute accounting
Clean training pool के non-padding tokens T हों तो प्रति run exposure 2T और primary 22 runs का कुल training exposure **44T** होगा। साथ में padding, validation और test-generation work अलग log करें। Full dense training का मोटा reference `6NT` FLOPs है; N=70B पर ~4.2×10¹¹ FLOPs/token। इसे BAdam/LoRA का measured cost न मानें: frozen weights, active block position, recomputation और communication दोनों की वास्तविक लागत बदलते हैं। Wall time या डॉलर budget अभी नहीं निकाला जा सकता।

भविष्य के pilot में small-model update-mask/state checks, फिर target-model load, few optimizer steps तथा एक block-switch boundary तक peak memory/throughput मापें। इन्हें अभी चलाने की आवश्यकता नहीं। Actual train/validation tokens/sec, GPU-hours, peak device/host memory, checkpoint storage और tuning खर्च दर्ज करें। Protocol को resource कारणों से बदलना पड़े तो दोनों arms के साझा exposure settings फिर freeze करें।

Optional secondary equal-compute study में वही hardware/topology और पहले से चुना हुआ per-run training GPU-hour cap C लें; cap/data traversal/checkpoint policy तथा tuning allowance पहले तय हों। प्रत्येक विधि cap से पहले का अंतिम completed update checkpoint दे; exposure अलग होगा और रिपोर्ट किया जाएगा। समान tuning trial-count समान tuning cost नहीं है—पूर्ण-budget comparison करना हो तो tuning का अलग समान GPU-hour cap भी निर्धारित करें। Primary और secondary निष्कर्ष न मिलाएं।

## 8. अपेक्षित deliverables और निष्कर्ष की सीमा
Manifest, overlap/filtering counts, all tuning configurations/validation scores, per-block update counts, paired-seed benchmark table, primary Δ/CI, baseline results, scoring failures और resource ledger प्रकाशित करें। Model-selection bias, residual pretraining contamination, filtered dataset coverage और seed-count सीमा साथ दें।

यह डिज़ाइन प्रश्न का नियंत्रित परीक्षण करेगा: चुने हुए backbone, data exposure, tuning space और tool-free zero-shot evaluation में कौन-सी recipe बेहतर है। **अभी BAdam या LoRA में से किसी की श्रेष्ठता स्थापित नहीं हुई है।**
````

**Stage**

````text
result
````

**Evidence**

````text
Repository inspection में केवल task.json उपलब्ध था। उसमें मूल तुलना-प्रश्न और embedded documents.track.md का पाठ 'Design-only task; repositories and compute are not required.' मिला। Python metadata check ने workspace inventory तथा standalone track.md के अभाव की पुष्टि की। कोई BAdam implementation, model config, MathInstruct files या experiment results उपलब्ध नहीं मिले। Supplied environment में network disabled, datasets खाली और GPU unavailable हैं। Researcher ने original Llama 3-70B base, equal-data primary तथा GSM8K/MATH equal-weight macro endpoint को अध्ययन के चुने हुए विकल्प के रूप में अनुमोदित किया; source की पुष्ट मंशा के रूप में नहीं। Final design का rationale: अंतिम समान-exposure checkpoints budget confounding रोकते हैं; balanced six-trial searches method-specific LR/rank/switch tuning देते हैं; test-independent validation और contamination audit leakage कम करते हैं; paired seeds/items एवं fixed prompt/scoring comparison variance और evaluation discretion कम करते हैं। Numerical memory figures byte arithmetic तथा स्पष्ट architectural assumptions के अनुमान हैं, benchmarked measurements नहीं। Training, scoring, hardware pilots या source verification नहीं चलाए गए।
````

**Assumptions**

````text
[
  "प्रस्तावित BF16, दो epochs, 4,096-token sequence, effective batch 64, 2% validation, छह tuning trials और पांच final seeds design defaults हैं, मूल task में दिए गए तथ्य नहीं।",
  "BAdam का cyclic one-layer block तथा reset-on-switch state policy execution से पहले intended source के विरुद्ध verify/amend होना आवश्यक है।",
  "LoRA all-seven-projection targets, rank/LR search तथा NLL selection चुने हुए controls हैं; अन्य setups पर निष्कर्ष स्वतः लागू नहीं होगा।",
  "1.0 percentage-point practical margin एक पूर्वनिर्धारित प्रस्तावित decision threshold है, domain stakeholder से प्राप्त value judgment नहीं।",
  "8×80-GB topology और adapter/block sizes feasibility illustrations हैं; hardware allocation या verified fit नहीं।"
]
````

**Uncertainties**

````text
[
  "Exact model/tokenizer/source commits, MathInstruct revision, source mix तथा overlap counts अभी अज्ञात हैं।",
  "BAdam reference semantics, distributed compatibility और full FP32 master/state allocation सत्यापित नहीं हैं।",
  "Cleaned token count, exposure में पूरे block cycles की संख्या, long-example exclusions और target-model throughput अज्ञात हैं।",
  "Hardware budget के बिना 22 runs की affordability तथा optional equal-compute cap तय नहीं किए जा सकते।",
  "Pretraining contamination, tuning-search variability और केवल पांच training seeds से inference की सीमाएं बनी रहेंगी।",
  "किसी विधि का actual zero-shot score या विजेता ज्ञात नहीं है।"
]
````

### Event 5 — Simulator

**Message**

````text
अंतिम प्रयोग-डिज़ाइन अनुरोधित deliverable को पूरा करता है: rationale, निष्पक्ष तुलना के controls, स्पष्ट training तथा evaluation protocol, uncertainty और निर्णय-नियम, तथा assumptions सहित feasibility शामिल हैं। इसे अंतिम डिज़ाइन के रूप में रखें। Source/version सत्यापन और संसाधन-जाँच निष्पादन से पहले की शर्तें रहेंगी; इस design-only कार्य में उन्हें चलाना आवश्यक नहीं है। अभी BAdam या LoRA की श्रेष्ठता का कोई अनुभवजन्य निष्कर्ष नहीं निकाला जा सकता।
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
प्रस्तुत डिज़ाइन सहमत original Llama 3-70B base, equal-data primary comparison और GSM8K/MATH macro-average का पालन करता है। इसमें समान अंतिम exposure checkpoints, छह tuning configurations प्रति विधि, पाँच paired final seeds, overlap audit, fixed tool-free zero-shot scoring, baseline, paired uncertainty तथा practical margin दिए गए हैं। Memory अनुमानों और optional equal-compute arm को वास्तविक उपलब्ध संसाधन या मापे गए परिणाम नहीं बताया गया है। अज्ञात implementation विवरण स्पष्ट verification gates हैं; प्रयोग चलने का दावा नहीं है।
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
  "event_log": "runs/openai-astra-top10-trial-1-batch-2/episodes/expbench_neurips2024_96897_7-ee05642667ec/candidate_001/attempt-1/output/neurips2024__96897__7/events.jsonl",
  "event_log_sha256": "c362428a0c3a0e59d8da3b6d19a4de44b1919be516747cf1be91d0fe642eff60",
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
