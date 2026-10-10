# candidate_001 · expbench · neurips2024/94328/4

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **44/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
पहले उपलब्ध brief और input दस्तावेज़ों का निरीक्षण करें और केवल प्रस्तावित approach तथा महत्वपूर्ण assumptions/अनिश्चितताएँ दें; अभी पूरा experiment design न लिखें। यह design-only कार्य है—repository, compute या प्रयोग चलाना आवश्यक नहीं है। निश्चित सीमाएँ: केवल weights quantize हों और precision {4, 3, 2} bits हो (neurips2024/94328/4:setup_5, neurips2024/94328/4:setup_7, neurips2024/94328/4:setup_11)। प्रस्ताव में बताएं कि RTN और GPTQ के साथ Hadamard transformation जोड़ने का अलग प्रभाव कैसे पहचानेंगे, कौन-से full-precision और बिना transformation वाले controls उचित होंगे, और quality तथा stability कैसे मापेंगे। Model/data चयन, quantization settings, transformation की function-preserving implementation और संभावित संसाधन जरूरतों को पुष्ट तथ्य नहीं, प्रस्तावित विकल्प के रूप में स्पष्ट करें। उपलब्ध स्रोतों से क्या निश्चित है और क्या अज्ञात है, अलग रखें; सुधार होने का पूर्वनिर्णय न लें।
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
Brief design-only deliverable मांगता है; weights-only और 2–4 bit precision निर्धारित हैं। अभी agent की inspection या proposed approach प्राप्त नहीं हुई है।
````

**Objectives Open**

````text
[
  "उपलब्ध inputs और consequential uncertainties की समीक्षा",
  "Hadamard के प्रभाव को अलग पहचानने वाली नियंत्रित तुलना पर approach तय करना",
  "अंतिम design में rationale, controls, analysis plan और feasibility देना"
]
````

### Event 2 — Actor

**Answer**

````text
### निश्चित जानकारी और स्रोत सीमा
- यह केवल experiment-design कार्य है; कोई model experiment नहीं चलाया गया है।
- आपके दिए निश्चित constraints: **केवल weights quantize होंगे, precision 4, 3 और 2 bits होगी** (setup_5, setup_7, setup_11 के संदर्भ)। Activations और KV cache quantize नहीं करेंगे।
- उपलब्ध task.json प्रश्न और design-only निर्देश की पुष्टि करता है। संबंधित setup topics का वास्तविक पाठ, model/data/config विवरण या QuaRot implementation उपलब्ध नहीं है। इसलिए प्रश्न में उल्लिखित RTN/GPTQ failure या QuaRot improvement को स्थापित परिणाम नहीं मानेंगे।

### प्रस्तावित approach — स्वीकृति के लिए
1. **Matched factorial तुलना:** प्रत्येक चुने हुए model और प्रत्येक bit-width पर RTN तथा GPTQ को (i) बिना Hadamard और (ii) Hadamard सहित तुलना करें। इससे छह within-method Hadamard contrasts मिलेंगे। समान method और bits के भीतर quality/stability का अंतर मुख्य प्रभाव होगा; RTN और GPTQ में इन अंतरों की तुलना interaction बताएगी। केवल RTN बनाम GPTQ+Hadamard की तुलना causal attribution के लिए पर्याप्त नहीं होगी।
2. **दो unquantized controls:** मूल full-precision model तथा वही model function-preserving Hadamard reparameterization के साथ, पर weight quantization के बिना। दोनों समान floating-point dtype में चलें; strict FP32 equivalence check छोटे, संभव परीक्षण का विकल्प है। इससे quantization लाभ और transformation implementation से उत्पन्न बदलाव अलग होंगे। यहाँ full-precision का अर्थ unquantized reference है; dtype अंतिम design में स्पष्ट करेंगे। प्रत्येक method/bit का बिना-transformation variant अलग quantized control होगा।
3. **केवल transformation बदलें:** primary contrasts में quantizer grouping/axis, scale/zero-point scheme, clipping policy, layer coverage, tuning budget और GPTQ calibration data समान रखें। RTN की अपनी baseline और GPTQ की अपनी baseline हों; GPTQ-specific settings केवल GPTQ के दोनों arms में matched हों। किसी अतिरिक्त QuaRot activation/KV quantization अथवा kernel change को intervention में न मिलाएँ।
4. **Function preservation पहले सत्यापित करने का प्रस्ताव:** compatible transformer में orthogonal Hadamard basis change को adjacent linear weights में fuse करें और जहाँ आवश्यक हो matching online transforms दें। Residual paths, normalization, nonlinearities, attention, biases और tied embeddings पर compatibility की समीक्षा जरूरी होगी—मनमाने रूप से हर weight पर Hadamard लगाना पर्याप्त नहीं है। Quantization से पहले fixed inputs पर logits और loss की numerical equivalence, dtype-उपयुक्त पूर्वनिर्धारित tolerance में, gate होगी। यह gate विफल हो तो quantization-quality निष्कर्ष रोकें। Exact transformation placement अभी निश्चित नहीं है।
5. **Quality:** held-out language-modeling NLL/perplexity प्राथमिक विकल्प; सीमित downstream zero/few-shot accuracy द्वितीयक विकल्प। हर arm का मूल unquantized reference से degradation और उसी method/bit के बिना-transformation arm से paired अंतर रिपोर्ट करने का प्रस्ताव है। Calibration/tuning और evaluation data अलग रखें; tokenization, context length और evaluation protocol समान हों। Document-level paired uncertainty intervals का विकल्प रखें।
6. **Stability को स्पष्ट अलग मापें:** (a) fixed evaluation inputs पर NaN/Inf, failed runs और पूर्वनिर्धारित severe-degradation सीमा पार करने की दर; (b) GPTQ calibration resamples और randomized Hadamard seeds के पार quality spread तथा worst-case/tail behavior। Deterministic RTN को उसी setting पर बार-बार चलाकर कृत्रिम seed variance न बनाएँ। Calibration और rotation randomness को अलग दर्ज करें; seed-variation तथा evaluation-sampling uncertainty अलग रिपोर्ट हों। सभी failures denominator में रहें।
7. **व्याख्या, न कि पूर्वनिर्णय:** layer-wise weight outlier statistics, quantization reconstruction error और activation-weighted output error सहायक diagnostics के विकल्प हैं। इन्हें task quality का substitute नहीं मानेंगे। सुधार, null effect, method-dependent परिणाम और गिरावट—सभी स्वीकार्य outcomes होंगे; किसी एक model पर सफलता से सार्वभौमिक 2–4-bit stability का दावा नहीं करेंगे।

### प्रस्तावित विकल्प और महत्वपूर्ण अनिश्चितताएँ
- **Model/data:** उदाहरणतः compatible open decoder model से प्रारंभ, संसाधन मिलने पर दूसरा आकार/परिवार; held-out WikiText-जैसा corpus और छोटी downstream suite विकल्प हैं, स्रोत-पुष्ट चयन नहीं। Model access, license, architecture और data availability की पुष्टि बाकी है।
- **Quantization:** group size, symmetric/asymmetric scheme, clipping, GPTQ damping/order/calibration count, embeddings तथा output head का coverage अभी तय नहीं हैं। प्रस्ताव है कि primary analysis में एक घोषित matched configuration हो; सीमित sensitivity checks अलग हों। चुने गए coverage से बाहर weights unquantized रहें तो उसे स्पष्ट घोषित करें।
- **Transformation:** deterministic बनाम randomized signed Hadamard, rotation locations और non-power-of-two dimensions का exact treatment source/implementation से पुष्टि माँगते हैं। Randomized variant हुआ तो rotation seeds matched और दर्ज हों।
- **संसाधन:** वर्तमान environment में GPU, datasets और installed project dependencies नहीं हैं; केवल CPU उपलब्ध होना LLM evaluation की व्यवहार्यता का प्रमाण नहीं। बाद में execution हो तो model-size के अनुसार accelerator memory, GPTQ calibration workspace, storage और repeats का budget आवश्यक होगा; अभी निश्चित GPU-hours/VRAM का दावा नहीं करेंगे।

### पूर्ण design से पहले आवश्यक पुष्टि
कृपया उपलब्ध होने पर setup_5/7/11 का मूल विवरण और setup_16/17 से model/data, quantizer settings तथा transformation scope संबंधी जानकारी दें। जो विवरण स्रोत में नहीं हैं, उन्हें प्रस्तावित choices ही रखेंगे। इस approach की स्वीकृति मिलने तक पूरा experiment design नहीं लिखूँगा।
````

**Stage**

````text
plan
````

**Evidence**

````text
inspect_repository से workspace में केवल task.json मिला; उसमें मूल प्रश्न, design-only context और documents के भीतर 'track.md': 'Design-only task; repositories and compute are not required.' inline entry है। छोटे read-only check 'find . -maxdepth 2 -type f -print' ने केवल ./task.json की पुष्टि की; कोई अलग track.md, source paper, implementation या dataset नहीं मिला। Weight-only और {4,3,2}-bit constraints शोधकर्ता के संदेश से निश्चित हैं, स्थानीय source-topic पाठ से स्वतंत्र रूप से सत्यापित नहीं। कोई model load, quantization या evaluation नहीं किया गया।
````

**Assumptions**

````text
[
  "Architecture-compatible orthogonal Hadamard reparameterization चुने जाने पर unquantized model का function numerical tolerance तक preserve किया जा सकेगा; इसे जाँचेंगे, मानकर निष्कर्ष नहीं निकालेंगे।",
  "आगे execution की आवश्यकता हो तो licensed model/data और पर्याप्त accelerator संसाधन अलग से उपलब्ध कराने होंगे।",
  "Matched quantizer configuration प्राथमिक तुलना का प्रस्ताव है; source-supported settings मिलने पर उसे संशोधित किया जा सकता है।"
]
````

**Uncertainties**

````text
[
  "setup_5/7/11/16/17 के मूल पाठ उपलब्ध नहीं; मॉडल, datasets तथा implementation particulars अज्ञात हैं।",
  "पूर्ण layer coverage, quantization grouping/clipping और GPTQ calibration protocol अभी निर्धारित नहीं हैं।",
  "Numerical tolerance, failure threshold, repeat count और uncertainty estimation का अंतिम specification approval तथा source clarification के बाद होगा।",
  "Hadamard से quality या stability में सुधार होगा या नहीं, और किस bit-width/method पर होगा, खुला empirical प्रश्न है।"
]
````

### Event 3 — Simulator

**Message**

````text
प्रस्तावित matched factorial approach स्वीकृत है। अब अंतिम experiment design दें—rationale, controls, analysis plan और feasibility सहित; कोई प्रयोग चलाना आवश्यक नहीं है। स्रोत-स्पष्टीकरण: neurips2024/94328/4:setup_5 और neurips2024/94328/4:setup_7 केवल weight-only quantization बताते हैं; neurips2024/94328/4:setup_11 में W bits ∈ {4,3,2} है। neurips2024/94328/4:setup_16 RTN को बिना calibration वाला Round-to-Nearest और neurips2024/94328/4:setup_17 GPTQ को Hessian approximation से error-minimizing quantization बताता है। इनसे model/data या अन्य settings निर्धारित नहीं होतीं; अतिरिक्त स्रोत विवरण उपलब्ध नहीं है।

आपके within-method contrasts, दोनों unquantized controls, equivalence gate और quality तथा stability को अलग मापने के विकल्प उचित हैं। अंतिम design में शेष विकल्प स्पष्ट प्रस्तावों के रूप में निश्चित करें: नामित model और datasets, split/context protocol, weight coverage तथा exclusions, dtype, group/scale/clipping policy, GPTQ settings और calibration sample count, rotation तथा calibration repeats, failure threshold और paired uncertainty analysis। RTN calibration-free रहे; GPTQ के दोनों arms में समान calibration examples हों, लेकिन Hessian statistics प्रत्येक arm की अपनी transformed या original activations से बनें।

Hadamard का exact scope और function-preserving placement स्पष्ट करें, non-power-of-two dimensions का व्यावहारिक treatment बताएं, और केवल generic rotation प्रस्तावित हो तो उसे सत्यापित QuaRot implementation न कहें। मूल hypothesis समझाएं कि weight outliers फैलने से quantization error घट सकता है, पर यह सुनिश्चित लाभ नहीं है। Improvement और stabilization के निर्णय नियम पूर्वनिर्धारित हों; deterministic RTN की नकली repeats न बनें और infrastructure failures को quantization failures से अलग रखें। लागत-संवेदी न्यूनतम design तथा वैकल्पिक विस्तार, configuration/run counts और संभावित memory/workspace जरूरतें दें; उपलब्ध compute या अनुभवजन्य सफलता का दावा न करें।
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
Agent ने design-only सीमा स्वीकार की और 2 methods × 3 precisions × 2 transformation conditions, unquantized equivalence controls, matched settings और अलग stability diagnostics प्रस्तावित किए हैं। यह मूल उद्देश्य के अनुरूप है; अब अनिर्धारित setup विकल्पों को प्रस्तावित, पुनरुत्पाद्य design में बदलना शेष है। स्थानीय निरीक्षण और अनुपलब्ध implementation संबंधी बातें agent की रिपोर्ट हैं, स्वतंत्र सत्यापन नहीं।
````

**Objectives Open**

````text
[
  "स्पष्ट transformation scope और quantization configuration सहित अंतिम experiment design",
  "Quality तथा stability के पूर्वनिर्धारित निर्णय नियम, controls और uncertainty analysis",
  "व्यावहारिक संसाधन योजना तथा स्रोत-तथ्यों और प्रस्तावित विकल्पों का स्पष्ट विभाजन"
]
````

### Event 4 — Actor

**Answer**

````text
## 1. उद्देश्य, निश्चित सीमाएँ और hypothesis

यह **design-only प्रस्ताव** है; कोई quantization या evaluation प्रयोग नहीं चलाया गया है। स्रोत-स्पष्टीकरण से केवल ये बातें निश्चित हैं:
- setup_5 और setup_7: weight-only quantization।
- setup_11: W bits ∈ {4, 3, 2}।
- setup_16: RTN, calibration के बिना Round-to-Nearest।
- setup_17: GPTQ, Hessian approximation से quantization error कम करने की विधि।

नीचे दिए model, datasets और सभी numerical settings **इस प्रयोग के प्रस्तावित निर्णय हैं, स्रोत से प्राप्त configuration नहीं**।

Hypothesis: orthogonal Hadamard mixing से कुछ बड़े weight coordinates अधिक coordinates में फैल सकते हैं; इससे fixed low-bit quantizer की range का उपयोग बेहतर और rounding/clipping error कम हो सकता है। लेकिन grouped quantization, activation geometry और GPTQ compensation के कारण लाभ सुनिश्चित नहीं है। 2-bit पर असफलता या गिरावट भी संभव परिणाम हैं।

यह न्यूनतम design **स्पष्ट रूप से परिभाषित, QuaRot-प्रेरित local Hadamard intervention** का परीक्षण करेगा। उपलब्ध repository में QuaRot code नहीं है, इसलिए इसे verified QuaRot reproduction या उसके सभी rotations का परीक्षण नहीं कहेंगे। असली QuaRot implementation के बारे में निष्कर्ष इस सीमा सहित ही होंगे।

## 2. प्रस्तावित model और data protocol

**Model:** `TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T`, pretrained base checkpoint और उसी का tokenizer। Execution के समय checkpoint/tokenizer revision, configuration, package versions और dataset fingerprints manifest में pin करें। Architecture inspection से अपेक्षित hidden dimension 2048 और intermediate dimension 5632 की पुष्टि करें; भिन्न configuration मिले तो प्रयोग शुरू करने से पहले amendment करें।

**Primary quality data:** `Salesforce/wikitext`, configuration `wikitext-2-raw-v1`।
- Train split: केवल GPTQ calibration।
- Validation split: data/implementation smoke checks; settings चुनने या test परिणाम देखकर tuning करने के लिए नहीं।
- Test split: अंतिम NLL/perplexity।
- Evaluation में शीर्ष-स्तरीय article headings से articles निर्धारित करें; tokenizer में automatic special-token insertion बंद रखें और प्रत्येक article के शुरू में एक BOS जोड़ें। Articles को अधिकतम 1024-token, nonoverlapping segments में काटें; दो से कम tokens वाले segments छोड़ें। एक article से दूसरे में context न ले जाएँ। प्रत्येक segment में first token के बाद के tokens score करें। सभी arms में वही segments और scored-token masks हों। NLL सभी scored tokens का weighted mean हो, perplexity = exp(NLL)। Article parsing और token counts को manifest में जाँचकर जमा करें।

**Calibration:** train articles को EOS separator के साथ जोड़कर nonoverlapping 1024-token candidate windows बनाएँ। प्रत्येक calibration seed में बिना replacement **128 windows** चुनें; seeds 101 और 202। Seeds के बीच overlap स्वीकार्य है और दर्ज होगा। Evaluation/test text calibration में नहीं आएगा। GPTQ के दोनों arms में प्रत्येक seed के लिए exactly वही token windows और order होंगे।

**Secondary quality:** `Rowan/hellaswag` validation से seed 303 द्वारा चुने गए 1,000 examples, zero-shot, token-count-normalized conditional log-likelihood से answer ranking। Prompt template और truncation rule freeze करें: चारों endings intact रखते हुए आवश्यक हो तो prompt के बाएँ हिस्से को काटें ताकि total context ≤1024 हो। Accuracy report करें; generation sampling न करें। इसे primary endpoint का विकल्प नहीं बनाएँ।

## 3. Hadamard का exact intervention और equivalence gate

हर transformer block में attention के Q/K/V, attention output projection, MLP gate/up और MLP down projection के **input basis** को बदलेंगे। Embeddings, normalization, RoPE, attention softmax, residual additions और LM head पर rotation नहीं लगाएँगे।

किसी linear layer के लिए row-vector convention में मूल गणना `y = x Wᵀ + b` है। Orthogonal block matrix R के साथ:

`x′ = xR`, `W′ = WR`, और `y = x′ W′ᵀ + b`।

इससे exact arithmetic में मूल function सुरक्षित रहता है। W′ offline तैयार होगा, xR runtime floating-point operation होगा; bias अपरिवर्तित रहेगा। प्रत्येक linear output अपनी मूल basis में लौट आता है, इसलिए residual या nonlinear operations के पार rotation commute कराने की जरूरत नहीं है। Q/K/V एक input rotation साझा करेंगे; gate/up भी साझा करेंगे। Attention output और MLP down के अपने input rotations होंगे: कुल चार rotation sites प्रति transformer block।

R में input axis पर contiguous **128-dimensional blocks** होंगे; प्रत्येक block `D H128` होगा, जहाँ D independent ±1 diagonal signs और H128 normalized Sylvester Hadamard है। Rotation seeds 11, 22, 33; site/block-specific random streams manifest में deterministic रहें। वही seed सभी bits, quantization methods और calibration seeds में वही R देगा।

**Non-power-of-two treatment:** पूरी dimension को power of two होना जरूरी नहीं। पूर्ण 128-blocks लगाएँ; यदि remainder हो तो उसे घटते power-of-two blocks में विभाजित करें, और अंतिम singleton पर identity रखें। कोई padding या dimension बदलना नहीं होगा। प्रस्तावित model की अपेक्षित dimensions 128 से divisible हैं, लेकिन इसकी जाँच अनिवार्य है। यह full-dimension dense Hadamard के समान intervention नहीं है।

**Numerics:** primary quality प्रयोग में unquantized weights, activations, KV cache, online Hadamard, quantizer scales और dequantized matmuls FP32 हों। TF32 और dropout बंद हों। Low-bit weights integer codes के रूप में quantize होंगे, फिर FP32 में dequantize करके reference inference होगा। यह accuracy experiment है, packed-kernel speed या memory-saving benchmark नहीं।

**Gate, quantization से पहले:** हर rotation seed के unquantized rotated model को मूल unquantized model से 16 fixed validation segments पर तुलना करें। आवश्यक दोनों सीमाएँ:
- concatenated logits का relative RMS difference ≤ 10⁻⁴;
- mean NLL का absolute difference ≤ 10⁻⁴ nats/token।

साथ में FP32 isolated linear-layer identity checks करें। कोई seed gate fail करे तो evaluation conclusions रोकें और implementation/numerics diagnose करें; test results देखकर tolerance न बढ़ाएँ। Full-test rotated-unquantized results भी report होंगे ताकि छोटे residual floating-point drift स्पष्ट रहें।

## 4. Weight quantization settings

**Coverage:** सभी transformer blocks के Q, K, V, O, gate, up और down dense weight matrices। Embedding table, LM head, normalization parameters और किसी bias को exclude करें और FP32 में रखें। Quantized parameter fraction report करें। इस अध्ययन का 'W2/W3/W4' label इसी coverage के लिए है, पूरे model के हर parameter के लिए नहीं।

सभी arms में:
- प्रत्येक output row के input axis पर contiguous group size **128**;
- unsigned affine integer grid, q ∈ {0,…,2ᵇ−1}; per-row/per-group FP32 scale और integer zero-point;
- a = min(group minimum, 0), c = max(group maximum, 0), s = (c−a)/(2ᵇ−1), z = clip(round(−a/s), 0, 2ᵇ−1);
- encode `clip(round(w/s)+z)` और decode `s(q−z)`; all-zero group के लिए zero reconstruction और सुरक्षित conventional scale;
- round-to-nearest, ties-to-even; **कोई percentile clipping, MSE scale search या learned tuning नहीं**। Grid saturation से होने वाली clipping मात्र लागू होगी।

Rotated weights पर scales उनके अपने W′ से बनें; baseline में W से। हर group के scale/zero-point quantization से पहले freeze हों, GPTQ updates के दौरान दोबारा fit न हों। इससे दोनों methods में grid policy स्पष्ट रहती है।

**RTN:** केवल उपर्युक्त weight statistics; calibration inputs, Hessian या activation-based clipping बिल्कुल नहीं।

**GPTQ:** layer-sequential reconstruction, FP32 Hessian approximation `H = XᵀX/N`; dampening λ = 0.01 × mean(diag(H)); Cholesky-based damped inverse handling; natural input-column order, activation-order sorting बंद; processing block size 128; static groups और ऊपर के frozen grids। Earlier layers quantized होने के बाद subsequent-layer calibration activations फिर compute करें; Q/K/V तथा gate/up को उनके साझा input stages के अनुसार संभालें। Implementation और processing order pin करें।

महत्वपूर्ण: दोनों GPTQ arms में token examples समान होंगे, **Hessian statistics समान करके reuse नहीं किए जाएँगे**। प्रत्येक arm अपने actual input activations से H बनाएगा—rotated linear के लिए xR सहित और अपने preceding quantized layers के प्रभाव सहित। Cholesky failure पर चुपचाप damping बदलना नहीं; इसे numerical failure दर्ज करें। अलग damping sensitivity study हो तो नई, अलग घोषित configuration हो।

## 5. Controls, repeats और run counts

तीन bits में प्रत्येक पर ये arms होंगे:

| Arm | प्रति bit configurations |
|---|---:|
| RTN, बिना transformation | 1 |
| RTN + Hadamard | 3 rotation seeds |
| GPTQ, बिना transformation | 2 calibration seeds |
| GPTQ + Hadamard | 3 rotations × 2 calibration seeds = 6 |

अर्थात **12 × 3 = 36 quantized model/evaluation configurations**। चार अतिरिक्त controls: एक original unquantized model और तीन rotated-unquantized models। **कुल 40 configurations**, प्रत्येक पर वही primary और secondary evaluation। Equivalence checks इनमें prechecks हैं, अतिरिक्त independent experimental repeats नहीं।

Deterministic RTN baseline एक बार quantize/evaluate होगा; एक ही परिणाम को तीन स्वतंत्र baseline runs नहीं मानेंगे। GPTQ rotation और calibration factors crossed होंगे। सभी seed results दिखाएँगे, केवल best seed नहीं।

## 6. Quality और stability का पूर्वनिर्धारित analysis

### Primary contrasts

प्रत्येक method और bit के लिए:

`ΔNLL = NLL(Hadamard) − NLL(no transformation)`।

ऋणात्मक मान लाभ है। GPTQ में पहले समान calibration seed के भीतर तुलना, फिर calibration और rotation factors पर equal-weight average करें। RTN में तीन rotated results को एक shared deterministic baseline से तुलना करें। Unquantized reference से NLL degradation और perplexity ratio भी दें।

Method interaction, `ΔGPTQ − ΔRTN`, secondary analysis होगा। Layer-wise weight max/RMS, reconstruction error और validation activations पर output reconstruction error exploratory mechanism diagnostics होंगे; इन्हें task-quality प्रमाण नहीं कहेंगे।

### Paired uncertainty

10,000 paired bootstrap resamples, fixed analysis seed। Primary text के लिए article clusters को resample करके token-weighted NLL फिर compute करें; हर resample सभी arms में समान articles रखे। HellaSwag में examples paired resample हों।

इन **evaluation-sampling intervals को fixed tested configurations के लिए conditional** कहेंगे। Seed uncertainty अलग दिखेगी: सभी rotation/calibration cells, ranges और descriptive crossed-factor decomposition। केवल दो calibration seeds और तीन rotations से व्यापक seed-population inference नहीं करेंगे; bootstrap में run cells को independent observations मानकर sample size नहीं बढ़ाएँगे।

छह primary method×bit contrasts के लिए family-wise 95% coverage हेतु Bonferroni-adjusted, two-sided **99.167% paired bootstrap intervals** report करें। Secondary accuracy और interaction के 95% intervals exploratory label से हों।

### Quality improvement rule

किसी method×bit पर औसत quality improvement तभी घोषित करें जब:
1. सभी संबद्ध runs technically valid हों और equivalence gate pass हो;
2. औसत ΔNLL ≤ −0.01 nats/token हो;
3. adjusted interval का upper bound <0 हो।

साथ में हर seed का sign दिखाएँ; mixed signs होने पर 'औसत सुधार, seed-robust नहीं' कहें। Downstream accuracy यदि कम हो तो trade-off report करें—blanket performance improvement नहीं। Interval zero को पार करे तो 'लाभ स्थापित नहीं', equality सिद्ध नहीं। यदि कोई arm fail हो तो successful-only औसत से यह rule लागू न करें; failures और conditional survivor results अलग दें।

### Stability और failure rule

पहले दो अलग failure categories:
- **Infrastructure:** OOM, dataset download/access failure, interruption, storage error। Same-config rerun अनुमति है; unresolved हो तो missingness और feasibility failure, quantization instability नहीं।
- **Quantization/numerical:** nonfinite weights/scales/logits/loss, fixed damping पर GPTQ factorization failure, या finite test NLL degradation ≥ ln(2) nats/token, यानी मूल unquantized model से perplexity कम-से-कम दोगुनी। अंतिम सीमा इस अध्ययन की प्रस्तावित 'severe degradation' operational definition है, कोई स्रोत-आधारित सार्वभौमिक मानक नहीं।

हर method×bit पर failure counts/denominators, worst valid NLL degradation और seed range दें। छोटे repeats के कारण tail percentiles या precise failure probability के दावे न करें।

**Observed stabilization:** equivalence pass हो, rotated arm में numerical/severe failures शून्य हों, और baseline में failure हो; अथवा दोनों arms failure-free हों तथा rotated arm का worst degradation कम-से-कम 0.01 nats/token बेहतर और seed range अधिक न हो। GPTQ के लिए इसे हर matched calibration seed में जाँचें; pooled worst-case भी दें। RTN baseline deterministic है, इसलिए variance reduction का दावा नहीं होगा—केवल failure avoidance या तीनों rotations में robust worst-case improvement। Infrastructure-missing cells हों तो stabilization verdict incomplete रहेगा।

'Improve and stabilize' तभी लिखें जब संबंधित quality और stability दोनों rules pass हों। '2–4 bits में' तभी जब हर bit पर शर्तें पूरी हों; अन्यथा सफल/असफल bit-width और method अलग नाम से बताएँ। निष्कर्ष इसी model, coverage और tested seeds तक सीमित होंगे।

## 7. Feasibility और लागत-संवेदी execution proposal

यह 1.1B model, 1024 context, 128 calibration windows, दो calibration seeds और तीन rotations वाला **न्यूनतम प्राथमिक design** है। इसे sequentially चलाएँ; सभी quantized models एक साथ memory में न रखें। Batch size 1, layer-wise GPTQ और streaming evaluation अपनाएँ; full vocabulary logits disk पर जमा न करें। Seeds और bits के पार reuse योग्य tokenization तथा FP32 calibration-independent data cache करें, लेकिन अलग arms के Hessians reuse न करें।

आकार-आधारित, benchmark नहीं, indicative memory estimates:
- 1.1B FP32 parameters लगभग 4.4 GB; full second weight copy से लगभग उतनी ही अतिरिक्त memory लग सकती है। Layer-local rotations/copies बेहतर हैं।
- 5632×5632 FP32 Hessian लगभग 127 MB; Hessian, factorization और temporary copies मिलाकर कई सौ MB प्रति सक्रिय matrix लग सकते हैं।
- 128×1024×2048 FP32 hidden-state cache लगभग 1.07 GB; इसे host RAM/disk पर stream किया जा सकता है।
- इसके अलावा intermediate activations, FP32 KV, logits और allocator workspace चाहिए। **16–24 GB GPU एक planning target है, guarantee नहीं**; 32–64 GB host RAM तथा checkpoint/data/cache के लिए कई दसियों GB storage reserve करना उचित प्रारंभिक प्रस्ताव है। Actual peak memory implementation-dependent है।

Reference dequantized inference में low-bit storage का theoretical लाभ compute-memory savings नहीं माना जाएगा। Runtime या GPU-hours की पुष्टि उपलब्ध नहीं है। Current environment में GPU/datasets/dependencies नहीं हैं; इस design को वहाँ सफलतापूर्वक executable बताने का आधार नहीं है।

**Optional extensions, primary से अलग:**
- तीसरा calibration seed जोड़ने पर 48 quantized + 4 unquantized = **52 configurations**; seed-population uncertainty के गंभीर दावे के लिए और seeds चाहिए।
- `meta-llama/Llama-2-7b-hf` जैसा दूसरा, larger base model: access/license और memory की पुष्टि के बाद वही 40-cell design; 7B FP32 weights अकेले लगभग 28 GB, अतः offload या बड़े/multiple accelerators आवश्यक हो सकते हैं।
- Verified QuaRot code मिलने पर exact original rotation scope का अलग intervention, उसके अपने equivalence controls और explicit version audit के साथ। इसे इस local-rotation परिणाम में मिलाएँ नहीं।
- Group size, block size या damping sensitivity; activation/KV precision फिर भी unquantized रहे। अतिरिक्त settings को primary test देखकर चुनकर मूल confirmatory result न बनाएँ।

## 8. अपेक्षित handoff artifacts

एक configuration manifest; exact transform equations/sites; data split और sample hashes; four-control equivalence report; 40-cell results template; seed-level NLL/accuracy तथा failures की अलग categories; six paired primary contrasts; और architecture/coverage सीमाओं सहित निष्कर्ष template। इन artifacts में अभी outcomes खाली रहेंगे—यह प्रस्ताव है, executed experiment या सकारात्मक परिणाम का दावा नहीं।
````

**Stage**

````text
result
````

**Evidence**

````text
स्थानीय निरीक्षण में केवल task.json मिला। उसमें मूल वैज्ञानिक प्रश्न और design-only context है; documents में track.md का inline संदेश 'Design-only task; repositories and compute are not required.' था, अलग source/code file नहीं। Read-only find check ने केवल ./task.json की पुष्टि की। कोई model या dataset load नहीं किया गया। शोधकर्ता के अनुमोदन और स्रोत-स्पष्टीकरण से weight-only, bits {4,3,2}, calibration-free RTN तथा Hessian-approximation GPTQ निश्चित हैं; model/data/settings उनसे निर्धारित नहीं होते। Within-method paired controls transformation effect को quantizer-method effect से अलग करते हैं; unquantized transformed controls implementation drift जाँचते हैं। Local orthogonal identity xR(WR)ᵀ=xWᵀ exact scope को function-preserving बनाती है, और numerical gate finite-precision implementation की परीक्षा है। Listed memory estimates parameter/matrix element counts × FP32 bytes से बने planning estimates हैं, measured peaks नहीं।
````

**Assumptions**

````text
[
  "नामित TinyLlama checkpoint और datasets भविष्य में license/access सहित उपलब्ध कराए जा सकेंगे; execution से पहले revision और actual dimensions सत्यापित होंगे।",
  "Local signed block-Hadamard intervention वैज्ञानिक रूप से उपयोगी QuaRot-inspired ablation है, लेकिन verified QuaRot reproduction नहीं है।",
  "FP32 dequantized reference inference low-bit weight reconstruction की quality जाँचने के लिए उपयुक्त है; deployed packed kernels की performance इससे स्थापित नहीं होगी।",
  "0.01-nat practical improvement और ln(2)-nat severe-degradation thresholds इस design के पूर्वनिर्धारित operational choices हैं, स्रोत से निकली सीमाएँ नहीं।",
  "यदि execution किया जाए तो पर्याप्त accelerator/host memory और dependencies अलग से उपलब्ध कराई जाएँगी।"
]
````

**Uncertainties**

````text
[
  "वास्तविक quality improvement, stability, seed sensitivity और 2-bit feasibility अज्ञात हैं।",
  "एक छोटे model और सीमित seeds से अन्य architectures, sizes और व्यापक failure probabilities पर निष्कर्ष सीमित होंगे।",
  "Actual runtime, peak memory और exact checkpoint/data access अभी सत्यापित नहीं हैं।",
  "सत्यापित QuaRot implementation उपलब्ध न होने से इस ablation के निष्कर्ष पूर्ण QuaRot algorithm पर सीधे लागू नहीं होंगे।"
]
````

### Event 5 — Simulator

**Message**

````text
Design में controls, quantization settings और analysis पर्याप्त स्पष्ट हैं, लेकिन मुख्य प्रश्न से एक महत्वपूर्ण अंतर शेष है: primary intervention अब केवल local block-Hadamard है, जबकि QuaRot का परीक्षण optional हो गया है। कृपया अंतिम design में QuaRot weight-only rotation arm को मुख्य तुलना बनाएं: उसी RTN/GPTQ × {4,3,2} matrix में बिना rotation और QuaRot rotation की तुलना हो। Design-only कार्य होने से code अभी उपलब्ध होना आवश्यक नहीं है; exact QuaRot rotation scope/version का स्रोत-आधारित audit और equivalence gate भविष्य के execution की अनिवार्य prerequisites रखें, अनुपलब्ध विवरण को पुष्ट तथ्य न बनाएं। Local block-Hadamard को अलग mechanistic ablation या fallback रखें, जो अकेले QuaRot संबंधी प्रश्न का उत्तर नहीं देगा। बाकी matched settings और controls बनाए रखें तथा आवश्यक run counts संशोधित करें। Stability rule भी स्पष्ट करें: प्रत्येक fixed calibration seed में unrotated GPTQ का rotation-range शून्य है, इसलिए उसी seed में rotated range उससे अधिक न होने की शर्त लगभग असंभव है। Calibration sensitivity को प्रत्येक fixed rotation पर calibration seeds के बीच मापें, rotation sensitivity अलग report करें, और failure avoidance/worst-case improvement को स्वतंत्र operational endpoints रखें। संशोधित अंतिम design दें; किसी experiment execution की जरूरत नहीं है।
````

**Interaction**

````text
refine_analysis
````

**Phase**

````text
result_review
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
प्रस्तुत design weight-only 2–4-bit factorial comparisons, unquantized controls, numerical equivalence, paired uncertainty और feasibility देता है तथा execution का दावा नहीं करता। लेकिन इसमें स्वयं बताया गया है कि local rotation verified QuaRot नहीं है और QuaRot मुख्य अध्ययन से optional extension में चला गया है। Within-calibration seed range की stability शर्त भी rotation तथा calibration variation को अस्पष्ट रूप से मिलाती है।
````

**Objectives Open**

````text
[
  "QuaRot को मुख्य intervention बनाकर मूल प्रश्न से design का सीधा संबंध स्थापित करना",
  "Calibration और rotation variability के लिए संगत stability decision rules देना"
]
````

### Event 6 — Actor

**Answer**

````text
# संशोधित अंतिम experiment design

## 1. प्रश्न और निश्चित सीमाएँ

प्राथमिक प्रश्न: **क्या QuaRot की function-preserving rotations जोड़ने से RTN और GPTQ की weight-only quantization quality तथा stability, 4/3/2 bits पर, बेहतर होती है?** सुधार मानकर नहीं चलेंगे।

स्रोत-स्पष्टीकरण से निश्चित:
- setup_5 और setup_7: केवल weights quantize होंगे।
- setup_11: W bits ∈ {4, 3, 2}।
- setup_16: RTN calibration-free Round-to-Nearest है।
- setup_17: GPTQ Hessian approximation पर आधारित error-minimizing quantization है।

**नीचे model/data और numerical settings प्रस्तावित experimental choices हैं, स्रोत-पुष्ट setup नहीं। कोई प्रयोग नहीं चलाया गया है।**

Hypothesis: orthogonal Hadamard mixing weight outliers को coordinates में फैला सकती है और quantization error घटा सकती है। Activation geometry, grouping और error compensation के कारण यह task-quality लाभ की गारंटी नहीं है।

## 2. मुख्य intervention: QuaRot rotations, generic local rotation नहीं

प्राथमिक matrix में प्रत्येक method और bit पर **बिना rotation बनाम QuaRot rotation** होगा। Activation और KV-cache quantization बंद रहेगी; अन्य QuaRot optimizations को साथ बदलकर effect confound नहीं करेंगे। निष्कर्ष इस प्रकार चुनी गई QuaRot rotation pipeline के संयुक्त प्रभाव का होगा, किसी एक internal rotation का नहीं।

### भविष्य के execution से पहले अनिवार्य audit

QuaRot paper, उसके supplement और आधिकारिक implementation के आधार पर एक version-pinned rotation specification तैयार और स्वीकार किए बिना primary प्रयोग शुरू नहीं होगा। उसमें अनिवार्यतः दर्ज हों:
1. Paper/version, repository URL, commit, checkpoint compatibility और relevant code paths।
2. हर rotation का matrix, normalization, randomized/deterministic construction, scope और seed handling।
3. Offline weight reparameterization तथा आवश्यक online transforms; residual stream, normalization, attention/QKV/output, MLP, embeddings और LM head से संबंधित वास्तविक placement।
4. Norm folding, biases और tied weights के treatment तथा nonlinear operations के आर-पार function preservation का आधार।
5. Non-power-of-two dimensions के लिए **वास्तविक QuaRot implementation का** factorization/block/padding treatment और उसकी orthogonality/shape checks। अपनी local-block recipe को चुपचाप substitute नहीं करेंगे।
6. Weight-only path में activation/KV quantizers और असंबंधित numerical/kernel changes बंद होने की पुष्टि।

इनका exact विवरण अभी अज्ञात है; यह जानबूझकर **execution prerequisite** है, पूरा हो चुका audit नहीं। यदि चुना model समर्थित न हो, तो data देखने से पहले protocol amendment द्वारा compatible model चुनें। यदि audited QuaRot path fixed quantization settings से असंगत निकले, तो incompatibility और किसी आवश्यक amendment को evaluation से पहले घोषित करें।

### Function-preservation gate और controls

चार unquantized controls का प्रस्ताव: मूल FP32 model और तीन QuaRot-rotated FP32 models। Random seeds केवल audited implementation के वैध randomization पर लागू होंगे।

Quantization से पहले 16 fixed validation segments पर प्रत्येक rotated model की मूल model से तुलना:
- logits का relative RMS difference ≤ 10⁻⁴;
- mean NLL का absolute difference ≤ 10⁻⁴ nats/token।

इसके अतिरिक्त isolated transformations की shape, orthogonality और linear-identity tests हों। Tolerance FP32 computation के लिए पूर्वनिर्धारित है; gate fail होने पर diagnosis/amendment के बिना primary quality conclusions नहीं निकालेंगे। पूरे test set पर unquantized controls भी evaluate होंगे।

यदि audited rotation पूर्णतः deterministic हो, तो एक ही rotated control/arm रखें; नकली rotation repeats न बनाएँ। यदि exact scope audit उपलब्ध न हो, primary QuaRot प्रश्न **अनुत्तरित** रहेगा—local ablation उसका उत्तर नहीं बनेगी।

## 3. प्रस्तावित model, data और precision

**Model:** `TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T`, base checkpoint और उसी का tokenizer; exact revisions pin हों। Actual architecture और QuaRot support audit अनिवार्य है।

**Numerics:** unquantized parameters, activations, KV cache, online transforms, scales और dequantized matmuls FP32; dropout तथा TF32 बंद। Quantized weights integer codes में बनाकर FP32 में dequantize किए जाएँगे। यह weight-reconstruction quality का reference experiment है, low-bit kernel throughput benchmark नहीं।

**Primary dataset:** `Salesforce/wikitext`, `wikitext-2-raw-v1`।
- Train: केवल GPTQ calibration।
- Validation: fixed implementation/equivalence checks; hyperparameter search नहीं।
- Test: final NLL/perplexity।
- Top-level article headings से documents बनाएँ; automatic special tokens बंद, हर article के शुरू में एक BOS। प्रत्येक article को ≤1024-token nonoverlapping segments में काटें; दो से कम tokens वाले segments छोड़ें। First token के बाद के tokens score हों; cross-article context नहीं। सभी arms में समान segments/masks। Token-weighted NLL और exp(NLL) report करें। Parsing और token counts manifest में जमा हों।

**GPTQ calibration:** train articles को EOS से जोड़कर nonoverlapping 1024-token candidate windows बनाएँ। Seeds 101 और 202 में प्रत्येक के लिए बिना replacement 128 windows चुनें। दोनों seeds में overlap हो सकता है, जो दर्ज होगा। दोनों GPTQ arms में समान calibration seed का अर्थ exactly वही examples/order है।

**Secondary dataset:** `Rowan/hellaswag` validation से seed 303 द्वारा fixed 1,000 examples; zero-shot token-count-normalized conditional likelihood accuracy। Prompt/template freeze करें। Endings intact रखें और आवश्यकता पर prompt बाएँ से truncate करके context ≤1024 रखें।

## 4. Matched weight quantization

**Coverage:** सभी transformer blocks के Q/K/V/O तथा MLP gate/up/down dense matrices। Embeddings, LM head, normalization parameters और biases quantize नहीं होंगे। QuaRot function preservation के लिए इन excluded tensors को reparameterize करना आवश्यक हो तो वे बदल सकते हैं, लेकिन FP32 में ही रहेंगे; audit में यह स्पष्ट हो। Quantized parameter fraction report करें।

**सभी arms में प्रस्तावित grid:**
- Input axis पर contiguous group size 128, प्रति output row/group।
- Unsigned affine q ∈ {0,…,2ᵇ−1}; FP32 scale, integer zero-point।
- a=min(group minimum,0), c=max(group maximum,0), s=(c−a)/(2ᵇ−1), z=clip(round(−a/s),0,2ᵇ−1)।
- q=clip(round(w/s)+z); reconstruction=s(q−z)। All-zero groups सुरक्षित zero reconstruction दें। Ties-to-even rounding।
- कोई percentile clipping, scale optimization या learned tuning नहीं; grid saturation मात्र।
- Scales प्रत्येक arm के अपने weights से बनें और GPTQ updates से पहले freeze हों।

**RTN:** weight statistics के अतिरिक्त कोई calibration, Hessian या activation-based setting नहीं।

**GPTQ:** layer-sequential processing, H=XᵀX/N, FP32 statistics; damping 0.01×mean(diag(H)); Cholesky-based damped inverse treatment; natural column order; activation ordering बंद; processing block size 128; static groups/frozen scales। Previous layers quantized होने के बाद subsequent-layer inputs recompute हों। साझा inputs वाले projections का processing order pin हो।

दोनों GPTQ arms में examples समान होंगे, लेकिन **प्रत्येक arm अपना Hessian अपनी actual activations से बनाएगा**, जिसमें QuaRot transforms और earlier quantized layers के effects शामिल हों। Hessians arms के बीच reuse नहीं होंगे। Fixed damping पर factorization failure दर्ज होगा; silent retuning नहीं।

## 5. Primary configurations और counts

प्रस्तावित rotation seeds 11, 22, 33, यदि audited QuaRot implementation valid randomized rotations देता हो। वही rotation प्रत्येक bit, method और calibration seed में साझा हो।

| Arm | प्रति bit configurations |
|---|---:|
| RTN, बिना rotation | 1 |
| RTN + QuaRot | 3 rotations |
| GPTQ, बिना rotation | 2 calibration seeds |
| GPTQ + QuaRot | 3 rotations × 2 calibration seeds = 6 |

कुल **36 quantized + 4 unquantized = 40 primary configurations**। पिछली संख्या वही है, लेकिन अब सभी primary rotated cells QuaRot हैं, local blocks नहीं। सभी पर primary तथा secondary evaluation हो। RTN baseline एक ही deterministic result है, independent repeated baseline नहीं।

यदि QuaRot deterministic हुआ: प्रति bit 1+1+2+2=6; **18 quantized + 2 unquantized = 20 configurations**।

## 6. Quality analysis और निर्णय नियम

Primary contrast, प्रत्येक method×bit पर:

**ΔNLL = NLL(QuaRot) − NLL(no rotation)**; negative लाभ है। GPTQ में matched calibration seed के भीतर contrasts बनाएँ और rotation/calibration cells को equal weight दें। RTN rotations shared baseline से paired हों। मूल unquantized reference से degradation और perplexity ratio भी दें।

10,000 paired bootstrap replicates:
- Text के लिए article-cluster resampling, हर arm में वही sampled articles, token-weighted NLL फिर compute करें।
- HellaSwag में paired example resampling।
- छह primary contrasts के लिए Bonferroni-adjusted two-sided 99.167% intervals; secondary accuracy और method interaction के 95% intervals exploratory।

ये intervals **tested seeds पर conditional evaluation uncertainty** दर्शाएँगे। सभी seed cells और seed ranges अलग report हों; तीन rotations/दो calibrations से व्यापक seed-population inference नहीं करेंगे।

**Quality improvement:** संबंधित सभी runs valid हों, equivalence pass हो, mean ΔNLL ≤−0.01 nats/token और adjusted interval का upper bound <0। Mixed seed signs हों तो 'औसत सुधार, सभी tested seeds में robust नहीं' लिखें। Failures होने पर successful-only mean से improvement घोषित नहीं होगा। Downstream accuracy कम हो तो trade-off स्पष्ट दें।

Method interaction ΔGPTQ−ΔRTN और layer-wise outlier/reconstruction/output-error diagnostics secondary हैं; diagnostics task quality का substitute नहीं।

## 7. संशोधित stability analysis: अलग axes और स्वतंत्र endpoints

Infrastructure failures—OOM, missing data/access, interruption, storage—अलग category हैं। Same-config rerun स्वीकार्य; unresolved cells missing रहेंगे, quantization failure नहीं बनेंगे।

Quantization/numerical failure: nonfinite weights/scales/logits/loss, fixed-settings GPTQ numerical failure, या original unquantized NLL से degradation ≥ln(2), अर्थात perplexity ≥2×। यह प्रस्तावित severe-degradation threshold है।

### A. Calibration sensitivity: केवल GPTQ

प्रत्येक bit पर baseline के दोनों calibration seeds के बीच NLL range निकालें। हर **fixed QuaRot rotation r** के लिए उन्हीं calibration seeds के बीच range अलग निकालें:

S₀=max_c L₀,c−min_c L₀,c;
Sᵣ=max_c Lᵣ,c−min_c Lᵣ,c।

सभी runs valid होने पर, सभी Sᵣ≤S₀ और meanᵣ(Sᵣ)≤0.9S₀ होने को 'tested calibration sensitivity में कमी' कहें, बशर्ते S₀>0। S₀=0 होने पर कमी का दावा नहीं होगा। दो calibration seeds से यह केवल observed range है, variance का सटीक estimate नहीं।

### B. Rotation sensitivity

हर fixed calibration seed में QuaRot rotations की NLL range तथा सभी individual values दें। RTN में उसके तीन rotations की range दें। इन्हें किसी fixed unrotated seed के शून्य rotation-range से 'कम' होने की शर्त नहीं लगाएँ। Baseline में rotation factor है ही नहीं।

### C. Failure avoidance: स्वतंत्र endpoint

प्रत्येक method×bit पर baseline और QuaRot failure counts/denominators दें। Observed complete failure avoidance तब घोषित हो जब baseline में कम-से-कम एक quantization/severe failure हो और सभी QuaRot cells failure-free हों। GPTQ के हर calibration seed का matched status भी दिखाएँ। Baseline failure-free हो तो 'failure avoidance प्रदर्शित नहीं हुआ', भले QuaRot भी failure-free हो।

### D. Worst-case quality improvement: स्वतंत्र endpoint

सभी संबंधित cells valid हों तो, GPTQ में प्रत्येक calibration seed c के लिए `max_r Lᵣ,c ≤ L₀,c−0.01` और pooled QuaRot worst NLL भी baseline pooled worst से ≥0.01 बेहतर होना tested robust worst-case improvement होगा। RTN में सभी rotations का worst NLL baseline से ≥0.01 बेहतर हो। किसी baseline numerical failure से finite worst-case difference बनाकर न दिखाएँ; वह endpoint C में जाएगा।

Calibration sensitivity, rotation sensitivity, failure avoidance और worst-case improvement **अलग outcomes** होंगे। 'Stabilization' शब्द आए तो किस endpoint पर उसका आधार है, नाम दें; एक अस्पष्ट composite score नहीं। 'Improve and stabilize' के लिए quality rule तथा कम-से-कम एक stabilization endpoint pass होना जरूरी है, और बाकी endpoints में deterioration छिपाई नहीं जाएगी। '2–4 bits में' तभी कहें जब तीनों bits पर नियम पूरे हों; अन्यथा bit/method-specific निष्कर्ष दें।

## 8. Local Hadamard: वैकल्पिक mechanistic ablation/fallback

अलग labeled arm में हर dense linear के input पर R और weight पर WR लागू करें: row convention में `xR(WR)ᵀ=xWᵀ`। R contiguous 128-dimensional normalized signed Hadamard blocks हो; remainder को power-of-two blocks और singleton identity में विभाजित करें। Q/K/V और gate/up shared input transforms ले सकते हैं; अन्य sites अलग हों। Outputs मूल basis में रहें। तीन seeds और स्वतंत्र unquantized equivalence controls हों।

यह QuaRot के वास्तविक scope की जगह नहीं है। इसे चलाने पर primary unrotated baselines साझा किए जा सकते हैं; **27 अतिरिक्त quantized cells + 3 local-rotated unquantized controls = 30 अतिरिक्त configurations**, यानी randomized-primary design सहित कुल **70**।

यदि QuaRot audit/implementation उपलब्ध न हो तो local-only fallback में 40 configurations हो सकते हैं, लेकिन निष्कर्ष केवल local Hadamard पर होगा और मूल QuaRot प्रश्न pending रहेगा।

## 9. Feasibility और optional विस्तार

न्यूनतम प्राथमिक design एक 1.1B model, context 1024, 128 calibration windows, दो calibration seeds और तीन valid rotation seeds पर आधारित है। Batch size 1, sequential configurations, layer-wise GPTQ, streamed evaluation और host-side caches अपनाएँ। No GPU-hour या सफलता का अनुमान दावा नहीं है।

आकार-आधारित planning estimates, actual measurements नहीं:
- 1.1B FP32 parameters ≈4.4 GB; full copied weights अतिरिक्त ≈4.4 GB।
- अपेक्षित 5632×5632 FP32 Hessian ≈127 MB; factors और temporaries से कई सौ MB प्रति active matrix।
- 128×1024×2048 FP32 hidden cache ≈1.07 GB।
- Logits, KV, activations, audited QuaRot workspace और allocator overhead अतिरिक्त।

16–24 GB GPU और 32–64 GB host RAM एक प्रारंभिक planning target है, पर्याप्त होने की guarantee नहीं। Exact QuaRot audit और memory preflight के बाद आवश्यकता तय होगी। Storage के लिए checkpoints/datasets/caches हेतु कई दसियों GB reserve करने का विकल्प रखें। Current environment में GPU, datasets या project dependencies उपलब्ध नहीं हैं।

तीसरा calibration seed जोड़ने पर randomized QuaRot primary: **48 quantized + 4 controls = 52 configurations**। दूसरा larger model, जैसे access-conditional `meta-llama/Llama-2-7b-hf`, अलग 40-cell replication हो सकता है; FP32 weights अकेले लगभग 28 GB होंगे। Group-size/damping या individual-rotation ablations अलग exploratory studies रहें।

## 10. अंतिम artifacts और निष्कर्ष सीमा

Version-pinned QuaRot audit; configuration/data manifests; weight coverage; equivalence gate report; complete cell-level results और failure log; छह paired quality contrasts; calibration/rotation sensitivity की अलग tables; failure-avoidance तथा worst-case endpoints। अभी ये परिणाम-रहित templates हैं।

Primary study सफलतापूर्वक पूरी होने पर भी निष्कर्ष चुने model, coverage, QuaRot version और tested seeds तक सीमित होगा। QuaRot के लाभ, null effect और deterioration सभी वैध संभावित निष्कर्ष हैं।
````

**Stage**

````text
result
````

**Evidence**

````text
Workspace निरीक्षण में केवल task.json मिला; उसमें मूल प्रश्न और design-only context था, QuaRot implementation या source-topic पाठ नहीं। छोटे read-only find check ने अतिरिक्त local inputs न होने की पुष्टि की। शोधकर्ता ने weight-only, bits {4,3,2}, calibration-free RTN और Hessian-approximation GPTQ के स्रोत-समर्थित तथ्य स्पष्ट किए; शेष settings प्रस्तावित हैं। इस revision में QuaRot audit को primary execution prerequisite बनाया गया है, और सभी primary rotation cells QuaRot हैं। Local block-Hadamard अब अलग ablation/fallback है। Calibration sensitivity को fixed rotation पर calibration seeds के बीच मापने से पिछले zero-range comparison की समस्या हटती है; rotation sensitivity और failure/worst-case endpoints स्वतंत्र हैं। Counts: प्रति bit 1+3+2+6=12, तीन bits पर 36, चार unquantized controls सहित 40; local ablation अतिरिक्त 3×(3+6)+3=30। कोई model experiment नहीं चलाया गया।
````

**Assumptions**

````text
[
  "नामित model/data भविष्य में उपलब्ध और licensed होंगे; checkpoint dimensions तथा QuaRot compatibility audit में सत्यापित होंगी।",
  "तीन rotation seeds का primary count audited QuaRot implementation में वैध randomization होने पर लागू है; deterministic implementation के लिए 20-cell विकल्प दिया गया है।",
  "FP32 dequantized inference low-bit weight quality जाँचने के लिए प्रयोग होगा, deployment performance मापने के लिए नहीं।",
  "Numerical tolerances, clipping/grid policy, 0.01-nat improvement, ln(2)-nat failure और 10% calibration-range reduction प्रस्तावित operational choices हैं।"
]
````

**Uncertainties**

````text
[
  "Exact QuaRot rotation scope, official commit, supported dimensions और non-power-of-two handling अभी सत्यापित नहीं; audit पूर्ण हुए बिना primary experiment नहीं शुरू होगा।",
  "QuaRot से quality या stability में सुधार होगा या नहीं अज्ञात है।",
  "Memory peaks, runtime और hardware availability अज्ञात हैं; दिए estimates measurements नहीं।",
  "सीमित model और seed counts व्यापक architecture generalization या precise failure probabilities का आधार नहीं हैं।"
]
````

### Event 7 — Simulator

**Message**

````text
संशोधित अंतिम design स्वीकार है। इसमें QuaRot मुख्य intervention है, local Hadamard अलग ablation है, और calibration तथा rotation sensitivity अब सही अलग axes पर मापी जाती हैं। Rationale, matched controls, quality/failure analysis और feasibility design-only deliverable के लिए पर्याप्त हैं। Exact QuaRot version/scope audit और equivalence gate भविष्य के execution की अनिवार्य शर्तें रहेंगी; उन्हें पूरा हुआ या empirical लाभ सिद्ध हुआ न बताया जाए। आगे संशोधन या प्रयोग चलाना आवश्यक नहीं है।
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
प्रस्तुत revision में RTN/GPTQ × {4,3,2} की QuaRot/no-rotation तुलना, 40 प्रस्तावित configurations तथा deterministic विकल्प, unquantized controls, paired quality intervals, स्वतंत्र stability endpoints और संसाधन अनुमान शामिल हैं। पिछले दोनों पहचाने गए अंतर सुधारे गए हैं। परिणाम चलाए जाने का दावा नहीं है; स्रोत और implementation संबंधी अनिश्चितताएँ स्पष्ट prerequisites हैं।
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
  "event_log": "runs/openai-astra-top10-trial-1-batch-2/episodes/expbench_neurips2024_94328_4-72cdd1baa00a/candidate_001/attempt-1/output/neurips2024__94328__4/events.jsonl",
  "event_log_sha256": "5cec507532b055eb5e52d71da30ead82b76cc16b7010f0fdf59b9651274a427d",
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
