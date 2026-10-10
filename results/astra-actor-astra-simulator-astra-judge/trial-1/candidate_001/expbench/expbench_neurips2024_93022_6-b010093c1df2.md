# candidate_001 · expbench · neurips2024/93022/6

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **17/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
पहले उपलब्ध इनपुट की समीक्षा करें और संक्षिप्त प्रस्तावित दृष्टिकोण दें; अभी पूर्ण प्रयोग-डिज़ाइन नहीं चाहिए। यह design-only कार्य है: repository, compute या प्रयोग चलाना आवश्यक नहीं है। तुलना के दो आधार हैं: मूल time attention वाला SiT (neurips2024/93022/6:setup_4) और non-causal Hyena वाला SiT (neurips2024/93022/6:setup_5)। बताएं कि केवल temporal operator बदलकर निष्पक्ष तुलना कैसे प्रस्तावित करेंगे, ‘extremely long’, consistency और multiple timescales को कैसे परिभाषित करेंगे, और किन controls तथा मापों पर विचार करेंगे। उपलब्ध स्रोत-तथ्यों को अपनी प्रस्तावित मान्यताओं से अलग रखें—विशेषकर SiT variant, trajectory domain/data, length extrapolation, non-causal operator की बनावट और संसाधन-बजट के बारे में। इन अनिश्चितताओं में से कौन-सी निष्कर्ष को सबसे अधिक प्रभावित करती हैं, यह भी बताएं।
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
Brief में केवल दो architecture conditions और design-only deliverable निश्चित हैं। कोई dataset, repository implementation या empirical परिणाम उपलब्ध नहीं है; इसलिए पहले प्रस्ताव और महत्वपूर्ण मान्यताओं की समीक्षा उचित है।
````

**Objectives Open**

````text
[
  "उपलब्ध setup और महत्वपूर्ण अनिश्चितताओं की समीक्षा",
  "निष्पक्ष तुलना तथा लंबी multi-timescale trajectories के मूल्यांकन का प्रस्ताव",
  "दृष्टिकोण की स्वीकृति के बाद rationale, controls, analysis plan और feasibility सहित अंतिम प्रयोग-डिज़ाइन"
]
````

### Event 2 — Actor

**Answer**

````text
**उपलब्ध तथ्य बनाम अनिश्चित विवरण**
आपके इनपुट के अनुसार तुलना setup_4 के मूल time-attention SiT और setup_5 के non-causal-Hyena SiT की है। स्थानीय इनपुट में केवल प्रश्न और design-only निर्देश मिले हैं; दोनों setups का मूल विवरण, कोड या डेटा उपलब्ध नहीं है। इसलिए SiT का पूरा नाम/variant, trajectory domain, training lengths, Hyena की वास्तविक बनावट और compute budget को अभी स्रोत-समर्थित तथ्य नहीं माना जा सकता। कोई प्रयोग नहीं चलाया गया है।

**संक्षिप्त प्रस्तावित दृष्टिकोण**
1. एक साझा SiT implementation/configuration में केवल temporal mixing operator बदलें। Spatial processing, depth/width, conditioning, trajectory representation, generative objective, noise schedule, sampler, training examples और validation protocol समान रखें। पहले सत्यापित करें कि setup_4 और setup_5 में अन्य अंतर तो नहीं हैं; हों तो मूल setups के परिणामों और operator-only तुलना को अलग रखें। कई paired seeds और समान hyperparameter-search अवसर प्रस्तावित हैं। मूल attention का causal/non-causal mask भी जाँचना होगा: भविष्य की जानकारी तक पहुँच अलग होने पर परिणाम केवल operator का प्रभाव नहीं होगा।
2. **‘Extremely long’** को परिणाम देखने से पहले दो स्तरों पर तय करें: training की अधिकतम लंबाई L_train के सापेक्ष token/step count, और domain की सबसे धीमी प्रासंगिक timescale के सापेक्ष वास्तविक अवधि। उदाहरणात्मक, अभी अनुमोदित नहीं: L_train, 2L_train, 4L_train, 8L_train पर परीक्षण और कई slow cycles को समेटती अंतिम अवधि। लंबे sequences पर प्रशिक्षण देकर लंबा generation और छोटे sequences से zero-shot length extrapolation अलग दावे हैं; दोनों को न मिलाएँ। Extrapolation तभी अर्थपूर्ण होगा जब दोनों operators/positional encodings के लिए पहले से तय वैध extension rule हो।
3. **Consistency** का अर्थ केवल smoothness नहीं: समय के साथ constraint/invariant violations, drift, state validity और स्थिर/उचित statistical behavior देखें। Domain के अनुसार long-lag correlations और transition statistics जोड़ें। Stochastic या chaotic trajectories में लंबी अवधि की pointwise MSE को मुख्य कसौटी न बनाएँ। Diversity और mode coverage भी जाँचें ताकि स्थिर या बार-बार दोहराई गई trajectory को सफलता न माना जाए।
4. **Multiple timescales** के लिए training/reference data और domain knowledge से fast/intermediate/slow bands पहले तय करें। Power spectra, lagged autocorrelation, coarse-grained statistics और जहाँ लागू हो dwell times/transition rates से जाँचें कि तेज़ स्थानीय dynamics तथा धीमे बदलाव दोनों सुरक्षित हैं। सबसे धीमी timescale का reference data में पर्याप्त coverage होना अनिवार्य होगा।
5. **Controls और माप:** समान data split/normalization, whole-trajectory आधारित leakage रोकथाम, conditioning और sampling steps; समान data exposure व update budget की मुख्य तुलना। Parameters, training/inference time, peak memory और लंबाई के साथ scaling रिपोर्ट करें। संसाधन अनुमति दें तो अलग compute-matched तुलना रखें—समान architecture, parameter count और compute को एक साथ बिल्कुल बराबर मानना सही नहीं होगा। दोनों के लिए व्यवहार्य लंबाइयों पर paired quality comparison करें; attention की memory failure को Hyena की बेहतर trajectory quality का प्रमाण न मानें। Uncertainty seeds और स्वतंत्र trajectories पर आँकें, correlated timesteps को स्वतंत्र नमूने न गिनें।

**निर्णय का प्रस्तावित आधार**
लंबाई बढ़ने पर consistency और प्रत्येक timescale की dynamics के पूर्वनिर्धारित quality criteria पूरे हों, और attention की तुलना में सुधार uncertainty सहित दिखे। केवल अधिक लंबाई पर generation संभव होना scalability का निष्कर्ष देगा, प्रश्न का पूरा सकारात्मक उत्तर नहीं। अंतिम thresholds domain और reference variability मिलने पर तय होंगे।

**सबसे consequential अनिश्चितताएँ एवं स्पष्टीकरण**
• सर्वोच्च प्राथमिकता: दोनों स्रोतों में SiT variant, trajectory domain/data और अन्य architectural differences क्या हैं? इन्हीं से operator-only attribution और consistency की परिभाषा तय होगी।
• इसी स्तर पर: दावा लंबे-context training का है या unseen lengths पर extrapolation का; training/evaluation lengths और physical timescales क्या हैं? इससे ‘extremely long’ का अर्थ बदल जाता है।
• अगली प्राथमिकता: setup_5 का non-causal Hyena kernel/filter, bidirectional support, gating/order, padding/boundaries और length-extension नियम क्या हैं; setup_4 का attention mask क्या है? Circular wraparound या अलग future access तुलना को प्रभावित कर सकते हैं।
• संसाधन बजट, precision, seeds और tuning allowance क्या अनुमत हैं? यह feasibility व निष्कर्ष की precision को प्रभावित करेगा, लेकिन पहले domain/length और operator confounds स्पष्ट होने चाहिए।

यह केवल प्रस्ताव है; इन स्रोत-विवरणों और आपकी स्पष्ट स्वीकृति के बाद ही पूर्ण डिजाइन विकसित किया जाएगा।
````

**Stage**

````text
plan
````

**Evidence**

````text
Workspace inspection और सीमित file-list check में केवल ./task.json मिला। उस फ़ाइल में सार्वजनिक प्रश्न, researcher से source-supported clarification लेने की सूचना, और documents.track.md में 'Design-only task; repositories and compute are not required.' दर्ज है; कोई वास्तविक track.md, setup_4/setup_5 दस्तावेज, implementation या dataset नहीं मिला। Setup identifiers और उनकी attention/Hyena पहचान उपयोगकर्ता के इनपुट से हैं, स्थानीय स्रोत से स्वतंत्र रूप से सत्यापित नहीं। केवल इनपुट निरीक्षण हुआ है, training/evaluation experiment नहीं।
````

**Assumptions**

````text
[
  "एक साझा SiT configuration में temporal operator को अलग से बदलना संभव होगा; स्रोत विवरण से पुष्टि आवश्यक है।",
  "L_train के multiples और fast/intermediate/slow bands प्रस्तावित operational definitions हैं, स्रोत के स्थापित settings नहीं।",
  "Domain-appropriate reference trajectories पर्याप्त लंबी और evaluation हेतु स्वतंत्र उपलब्ध कराई जा सकेंगी; अभी कोई dataset उपलब्ध नहीं है।",
  "Compute-matched supplementary runs तथा multiple seeds बजट मिलने पर प्रस्तावित हैं, निश्चित संसाधन आवश्यकता नहीं।"
]
````

**Uncertainties**

````text
[
  "SiT variant, trajectory domain/data और स्रोत setups के गैर-temporal अंतर अज्ञात हैं।",
  "Training/evaluation length, physical duration और length extrapolation का इच्छित दावा स्पष्ट नहीं है।",
  "Non-causal Hyena की filter construction, boundary handling तथा baseline attention visibility अज्ञात हैं।",
  "Training compute, memory budget, tuning allowance और व्यवहार्य seed count निर्दिष्ट नहीं हैं।"
]
````

### Event 3 — Simulator

**Message**

````text
प्रस्तावित दृष्टिकोण स्वीकृत है। अब rationale, controls, analysis plan और feasibility सहित अंतिम प्रयोग-डिज़ाइन तैयार करें; प्रयोग चलाना आवश्यक नहीं है। मूल attention SiT (neurips2024/93022/6:setup_4) और non-causal Hyena SiT (neurips2024/93022/6:setup_5) ही उपलब्ध स्थापित setup विवरण हैं। अतिरिक्त स्रोत-विवरण उपलब्ध नहीं हैं; उनके इंतज़ार में डिज़ाइन न रोकें। एक ठोस trajectory benchmark तथा आवश्यक SiT/operator configuration को स्पष्ट रूप से प्रस्तावित विकल्प मानकर चुनें, स्रोत का तथ्य नहीं।

Operator-only comparison, whole-trajectory split, समान data exposure, paired seeds और साझा feasible lengths पर quality comparison बनाए रखें। L_train, 2L_train, 4L_train, 8L_train की प्रस्तावित श्रृंखला उचित है, लेकिन ठोस sampling interval, absolute lengths और slow-timescale coverage भी दें। Long-context training और zero-shot extrapolation अलग परीक्षण रहें। Non-causal mixing में generated/noisy sequence का दोनों दिशाओं में उपयोग और भविष्य के ground truth की leakage का अंतर स्पष्ट करें; filter boundaries और length-extension rule भी निर्दिष्ट करें।

मुख्य metrics और reference-data से acceptance thresholds तय करने की पूर्वनिर्धारित प्रक्रिया दें; test results देखकर thresholds न चुनें। Seed/trajectory स्तर पर uncertainty, diversity, fast/slow dynamics, drift और failures शामिल करें। निष्कर्ष में तीन बातें अलग रखें: Hyena की लंबी सही trajectories बनाने की क्षमता, attention के मुकाबले गुणवत्ता में लाभ, और केवल संसाधन/scaling में लाभ। Attention से बेहतर होना क्षमता सिद्ध करने की अनिवार्य शर्त नहीं है; दोनों सफल हों तो वही निष्कर्ष होगा। बजट अज्ञात होने के कारण न्यूनतम व्यवहार्य अध्ययन और वैकल्पिक विस्तार दें, साथ ही प्रस्तावित sample/seed counts और अपर्याप्त slow-event coverage होने पर निष्कर्ष की सीमा बताएं। कोई अनुमानित empirical result प्रस्तुत न करें।
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
एजेंट के प्रस्ताव में उचित operator isolation, length तथा physical-timescale की अलग परिभाषाएँ, leakage नियंत्रण, diversity, correlated samples और memory failure की सही व्याख्या शामिल है। निरीक्षण के अनुसार अतिरिक्त implementation/data उपलब्ध नहीं हैं; इसलिए अज्ञात विवरणों को घोषित design assumptions के रूप में चुनकर अंतिम design तैयार करना उचित है।
````

**Objectives Open**

````text
[
  "ठोस benchmark, operator specification और length/time-scale protocol सहित अंतिम प्रयोग-डिज़ाइन",
  "पूर्वनिर्धारित quality criteria, controls और uncertainty analysis",
  "बजट-सचेत feasibility तथा संभावित निष्कर्षों की स्पष्ट व्याख्या"
]
````

### Event 4 — Actor

**Answer**

````text
# अंतिम प्रयोग-डिज़ाइन

## 1. स्थापित तथ्य और अध्ययन का दायरा
स्थापित setup विवरण केवल ये हैं: setup_4 मूल temporal-attention SiT है और setup_5 non-causal-Hyena SiT है। नीचे चुना गया benchmark, SiT configuration, Hyena realization, lengths और budgets **इस अध्ययन के प्रस्तावित विकल्प हैं, स्रोत का पुनर्निर्माण नहीं**। निष्कर्ष इसी नियंत्रित realization और benchmark तक सीमित होगा। कोई training या evaluation प्रयोग नहीं चलाया गया है।

तीन प्रश्नों के उत्तर अलग दें:
1. क्या Hyena निर्धारित अत्यंत लंबी अवधि पर सही, विविध और multiscale trajectories बना सकता है?
2. समान परिस्थितियों और साझा feasible lengths पर क्या उसकी गुणवत्ता attention से बेहतर, समान या खराब है?
3. क्या उसे केवल memory/runtime/scaling का लाभ है?

क्षमता सिद्ध करने के लिए attention को हराना आवश्यक नहीं है। दोनों सफल हों तो दोनों की क्षमता समर्थित होगी।

## 2. ठोस benchmark: switching-driven stochastic oscillators
**चयन का rationale:** ज्ञात simulator से स्वतंत्र reference trajectories मिलेंगी; fast oscillations, slow oscillations और दुर्लभ regime changes को अलग-अलग मापा जा सकेगा। यह वास्तविक molecular/robotic trajectories का विकल्प नहीं, पहला नियंत्रित परीक्षण है।

Sampling interval Δt = 0.125 time units रखें। Hidden regime s_n ∈ {−1,+1} symmetric continuous-time two-state Markov process से sample करें, switching rate λ = 1/128। Sampled transition probability p = (1−exp(−2λΔt))/2 हो। औसत underlying dwell time 128 units है।

तीन 2D oscillator states z_j के periods P_j = 1, 8, 64 units और damping times τ_j = 2, 16, 128 units रखें। हर step:

z_(j,n+1) = a_j R(2πΔt/P_j) z_(j,n) + b_j(s_n) sqrt(1−a_j²) ε_(j,n),

a_j = exp(−Δt/τ_j), ε स्वतंत्र N(0,I₂), b_j(s)=1+0.25s। R standard 2D rotation है। सातवाँ observed coordinate:

x_(n+1) = c x_n + (1−c)s_n + 0.1 sqrt(1−c²) η_n,

c = exp(−Δt/8), η स्वतंत्र N(0,1)। Model को केवल सात observed coordinates (तीन oscillator pairs और x) दें; hidden s और simulator innovations नहीं। इससे slow regime oscillator amplitudes से जुड़ता है—सिर्फ तीन असंबद्ध frequencies उत्पन्न करना पर्याप्त नहीं होगा। यह sampled recurrence ही benchmark की परिभाषा है; किसी continuous oscillator equation के exact solver होने का दावा नहीं।

हर स्वतंत्र path से पहले 4096-unit burn-in हटाएँ। Burn-in adequacy reference-only calibration में अलग initializations से moments/regime occupancy की तुलना करके जाँचें; अपर्याप्त हो तो data generation से पहले बढ़ाकर स्थिर करें।

### लंबाई और ‘extremely long’
| स्थिति | steps | अवधि | slow P=64 cycles | expected hidden switches |
|---|---:|---:|---:|---:|
| L_train | 2048 | 256 | 4 | लगभग 2 |
| 2L_train | 4096 | 512 | 8 | लगभग 4 |
| 4L_train | 8192 | 1024 | 16 | लगभग 8 |
| 8L_train | 16384 | 2048 | 32 | लगभग 16 |

अंतिम पंक्ति इस benchmark में ‘extremely long’ की operational definition है: training length का आठ गुना, slow oscillation के 32 cycles और slow damping time का 16 गुना। यह सार्वभौमिक परिभाषा नहीं है; अपेक्षित switches वास्तविक observed event count का विकल्प नहीं हैं।

## 3. डेटा और leakage controls
अलग random streams से 2400 independent observed paths, प्रत्येक 16384 steps, प्रस्तावित हैं: 1200 train, 400 validation/calibration, 800 locked test। **Whole-path split पहले करें, crops बाद में।** कोई parent path एक से अधिक splits में नहीं जाएगा। Normalization केवल train statistics से, दोनों models के लिए समान होगी। Test trajectories और उनके latent labels fitting, tuning या threshold selection में उपयोग नहीं होंगे।

छोटे-context training में train parents से केवल 2048-step crops दिखाएँ। Crop start positions, sample order और diffusion noise/time draws paired runs में समान हों। Train parent लंबा होने का अर्थ model को उसका लंबा context दिखाना नहीं है। Calibration set को 200 tuning paths और 200 threshold-setting paths में अलग करें।

Generation unconditional होगा; प्रत्येक लंबाई की पूरी trajectory एक साथ generate करें। Ground-truth prefix, stitching और sliding-window rollout मुख्य परीक्षण में नहीं होंगे। इससे window-overlap heuristics operator प्रभाव में नहीं मिलेंगे।

## 4. प्रस्तावित SiT और operator-only intervention
प्रस्तावित backbone: सात coordinates को प्रति timepoint एक token में linear embed करें; width 128, चार pre-normalized residual blocks, expansion-4 pointwise MLP, समान diffusion-time adaptive conditioning और सात-channel output projection। सभी सात coordinates एक token में होने से इस benchmark में अलग spatial-attention module नहीं चाहिए। इसे प्रस्तावित compact SiT-style interpolant model के रूप में रिपोर्ट करें, मूल source configuration बताकर नहीं।

Generative training में linear stochastic interpolant X_t=(1−t)ε+tX, t~Uniform[0,1], ε~N(0,I), और velocity target X−ε का mean squared loss चुनें। दोनों में वही loss reduction और time sampling हो। Sampling के लिए 100-step Heun integration t=0 से 1 तक, वही initial Gaussian tensors, precision और solver settings रखें। Calibration पर 200 steps का sensitivity check करें ताकि sampler error को architecture failure न समझें; आवश्यक बदलाव दोनों पर लागू करके test से पहले lock करें।

**Attention arm:** चार heads, full bidirectional temporal self-attention, dropout 0।

**Hyena arm:** चार channel groups वाला order-2 gated long-convolution mixer। Tokenwise linear projection से g₁,g₂,v बनें; y₀=v और y_i=g_i ⊙ (h_i * y_(i−1)), i=1,2; अंतिम shared-width output projection residual में जाए। यह स्पष्ट proposed non-causal Hyena-style realization है, canonical source implementation होने का दावा नहीं।

हर group/stage के लिए positive और negative lag filters एक small implicit MLP से बनाएँ: signed lag feature sign(k)log(1+|k|), fixed sinusoidal lag features तथा envelope exp(−|k|/ρ); ρ values 8,64,512,2048 steps पर initialize करके positive learned values रखें। प्रत्येक lag पर kernel मूल्य length से स्वतंत्र होगा। Sequence N पर सभी valid signed lags −(N−1)…N−1 लें। Normalization या coordinates को N से rescale न करें। लंबाई बढ़ने पर यही function नए lags पर evaluate होगा, कोई fitting नहीं।

दोनों arms में identical fixed sinusoidal absolute-position embeddings हों, learned finite-length tables नहीं। नए positions पर वही analytic formula इस्तेमाल करें। Filter extrapolation और position extrapolation साथ रिपोर्ट हों; उनकी सफलता मानकर न चलें।

**Boundaries:** sequence के बाहर zero extension; circular convolution नहीं। FFT implementation में कम से कम 3N−2 support तक padding के बाद सही linear-convolution slice लें। छोटे N पर direct convolution से numerical agreement और impulse-response checks आवश्यक हैं। Edge तथा interior errors अलग रिपोर्ट करें।

**Non-causal ≠ ground-truth leakage:** training में दोनों operators current interpolated/noisy sequence के past और future positions देखेंगे; sampling में दोनों current generated/noisy sequence के दोनों दिशाओं के positions देखेंगे। किसी held-out clean future trajectory या hidden regime को input नहीं दिया जाएगा। Generation noise से शुरू होती है, test trajectory से नहीं।

बाकी backbone समान रखें, parameters की संख्या रिपोर्ट करें। Hyena और attention के operator parameters बिल्कुल बराबर नहीं होंगे; मुख्य अध्ययन backbone-matched है। Optional parameter-matched sensitivity analysis को अलग रखें, ताकि उसे operator-only तुलना के साथ न मिलाया जाए।

## 5. Training controls और अलग length tests
मुख्य प्रस्ताव: तीन paired training seeds, AdamW, learning rate 2×10⁻⁴, weight decay 0.01, gradient clipping 1, 500-step warm-up और cosine decay, effective batch आठ crops, 10,000 updates। Final EMA checkpoint, decay 0.999, evaluate करें। ये budget choices हैं, convergence का दावा नहीं। Shared parameters की initialization और data/noise schedule pair करें; operator-specific parameters के distributions दस्तावेज करें। Seeds के भीतर pairing, seeds के बीच independence रखें।

Loss normalization, precision, optimizer, data exposure, tokens/update और update count समान हों; जरूरत हो तो attention microbatch छोटा करके accumulation करें। Fixed-budget result को fully optimized architecture ranking न कहें। Calibration learning curves convergence न दिखाएँ तो दोनों के लिए पहले से घोषित समान extension या ‘undertrained’ limitation रखें; केवल एक arm को अतिरिक्त updates न दें।

**A. Zero-shot extrapolation, मुख्य अध्ययन:** केवल L_train=2048 पर train करें, frozen models को चारों evaluation lengths पर जाँचें। लंबी samples देखकर tuning नहीं।

**B. Long-context training, अलग प्रयोग:** नए models को N=16384 पर train करके N=16384 पर evaluate करें। दोनों arms के लिए effective batch एक और वही 10,000 updates देने से A के बराबर total training tokens होंगे, किंतु context/batch structure बदलेगा; इसलिए A बनाम B को pure operator effect नहीं कहेंगे। यह budget अनुमति पर extension है। इसे zero-shot extrapolation के प्रमाण में शामिल नहीं करें। यदि attention इस length पर train नहीं हो सकता, तो Hyena-only capacity result और attention resource limitation रिपोर्ट हों, paired quality superiority नहीं।

## 6. Metrics और thresholds की पूर्वनिर्धारित प्रक्रिया
हर seed/operator/length पर 128 independent trajectories प्रस्तावित हैं। Matching random tensors variance घटाने के लिए हैं; exact trajectory matching अपेक्षित नहीं। Pointwise long-horizon MSE मुख्य metric नहीं होगा।

**Primary metric families, lower discrepancy बेहतर:**
1. **Fast और slow dynamics:** per-channel spectra और autocorrelation। Periods 1,8,64 के आसपास पूर्वनिर्धारित frequency bands [0.75/P,1.25/P] में power तथा peak position; complementary bands में power भी, ताकि गलत अतिरिक्त modes छिपें नहीं। ACF lags 0.125,1,8,32,64,128 और 256 units जहाँ valid हों।
2. **Regime dynamics और cross-timescale coupling:** x की hysteresis labels—x>0.5 पर positive, x<−0.5 पर negative, बीच में previous state—से observed dwell distributions, switch rate, occupancy और regime-conditional oscillator energy। यही detector generated और reference data दोनों पर लगेगा; hidden labels केवल simulator/detector sanity check में। Censored start/end dwells को survival analysis में समुचित treatment दें।
3. **Consistency/drift:** trajectory quarters में mean, variance, oscillator energy, occupancy; normalized end-to-start changes और slopes की distributions। Boundary और interior discrepancies अलग। Stationary truth में भी random drift होगा; शून्य drift नहीं, reference distribution लक्ष्य है।
4. **Diversity/coverage:** train-calibrated summary vectors—energies, bandpowers, x quantiles, switching rate—की multivariate distribution पर standardized energy distance; reference bins की occupancy और near-duplicate trajectory rate सहायक checks। केवल marginal variance को diversity न मानें।
5. **Failures:** NaN/Inf, sampling failure, OOM/timeout और finite-but-pathological excursions अलग counts। Excursion cutoff reference calibration की maxima distribution से तय हो; oscillator Gaussian tails के कारण arbitrary hard physical bound नहीं लगाएँ। किसी failed sample को चुपचाप हटाएँ नहीं।

**Threshold-setting procedure:** model test outputs देखने से पहले threshold-only reference paths से, प्रत्येक N और m=128 के लिए, disjoint parent groups की repeated random partitions बनाएँ। समान size के दो real groups के बीच वही discrepancies निकालें। Spectral bins, lags और drift summaries को उनके reference-reference 95th-percentile discrepancy से scale करें; near-zero scales के लिए numerical floor पहले लिखें। Families तथा lengths पर maximum standardized discrepancy की reference-only 95th percentile को simultaneous acceptance envelope बनाएँ। Random partition repetitions नई independent data नहीं हैं; envelope की uncertainty parent-path bootstrap से रिपोर्ट करें।

इसी प्रक्रिया से drift, diversity और finite-excursion rate की tolerances तय हों। NaN/Inf तथा sampler failure के लिए अलग preregistered engineering tolerance 1% और one-sided 95% binomial upper bound का नियम रखें। यह 1% reference का तथ्य नहीं, प्रस्तावित स्वीकार्यता है। यदि reference pool/sampling error से tolerances बहुत चौड़ी हों, अधिक reference paths बनाएँ या claim को coarse-resolution तक सीमित रखें; test देखकर tolerances न फैलाएँ।

**Capacity pass:** 8L पर सभी primary families की discrepancy के upper uncertainty bounds frozen acceptance envelope के अंदर हों और failure criterion पूरा हो। अन्य lengths की profile भी दें। यदि bounds threshold पार करते हों तो ‘not established’; स्पष्ट exceedance पर metric-specific failure। Reference-equivalence की यह finite-sample operational कसौटी है, distribution की mathematical identity नहीं।

## 7. Statistical analysis और interpretation
Seed को मुख्य training-replicate unit मानें। हर seed का result और paired operator difference दें। Within-seed uncertainty independent generated/reference parent trajectories bootstrap करके; overall uncertainty hierarchical bootstrap से—पहले paired seeds, फिर trajectories। Timesteps, overlapping crops और FFT bins को स्वतंत्र replicates न गिनें। तीन seeds की between-training uncertainty कमजोर होगी; इस सीमा को स्पष्ट रखें।

Attention quality comparison केवल उन lengths पर करें जहाँ दोनों preregistered evaluation पूरा कर सकें। Primary composite frozen scaled discrepancies का maximum हो, लेकिन हर family अलग भी दिखे। Paired difference और 95% interval रिपोर्ट करें; superiority के लिए difference Hyena के पक्ष में हो और किसी primary family में reference-derived tolerance से बड़ी deterioration न हो। Family-wise inferential comparisons के लिए Holm correction रखें। अस्पष्ट interval को equivalence का प्रमाण न कहें।

Slow-event adequacy: हर length/reference और हर seed/model में observed complete dwells और independent paths की संख्या रिपोर्ट करें। प्रस्तावित न्यूनतम: 200 complete detected dwells, कम से कम 50 event-containing paths, और switch-rate interval की relative half-width ≤25%। अपर्याप्त coverage पर long-dwell/slow-transition fidelity का सकारात्मक दावा रोकें। Slow spectral dynamics और event dynamics को अलग रिपोर्ट करें। यदि generated event shortage reference से स्पष्ट असंगत है तो वह model failure हो सकता है, केवल sample-size समस्या नहीं।

अंतिम outcome table में तीन स्वतंत्र columns हों: ‘Hyena capacity established?’, ‘paired quality advantage?’, ‘resource advantage?’। दोनों operators pass करें तो दोनों सफल; Hyena pass और attention OOM हो तो Hyena capacity + feasibility advantage, quality superiority नहीं; Hyena तेज़ हो पर dynamics criteria fail हों तो केवल scaling लाभ।

## 8. Feasibility, resource reporting और extensions
अभी GPU, dataset या installed project stack उपलब्ध नहीं है; यह तत्काल executable study का दावा नहीं। Reference simulator और dataset हल्के हैं: 2400×16384×7 float32 values लगभग 1.1 GB हैं, overhead अलग। Training/generation GPU मांगेंगे। Hardware अज्ञात होने से GPU-hours का अनुमान तथ्य की तरह नहीं देंगे।

Training से पहले छोटे forward/backward smoke checks: shapes/gradients, bidirectional influence, attention mask, direct-vs-FFT convolution, no wraparound, finite sampling, और shared-weight/config diff। फिर प्रत्येक length पर maximum feasible microbatch तथा peak memory/time मापें। Exact memory-efficient attention इस्तेमाल किया जा सकता है; approximation/subquadratic replacement नहीं। N=16384 पर dense attention की naive score matrices बहुत बड़ी होंगी; optimized attention से memory घट सकती है, quadratic arithmetic नहीं।

Resource metrics: parameter count, train tokens, accelerator-hours, peak allocated memory, batch-one generation latency, per-generated-token time, और failure/OOM boundary। Same hardware/precision/sampler और warm-up policy रखें; operator microbenchmark तथा end-to-end generation दोनों दें। Abort/timeout ceiling hardware allocation के बाद, model-quality outcomes देखने से पहले तय करें।

**न्यूनतम व्यवहार्य अध्ययन:** मुख्य A के दो operators × तीन seeds; चार requested lengths पर Hyena, दोनों की feasible shared lengths पर paired quality; 128 samples/seed/length; frozen calibration और उपर्युक्त checks। Upper lengths infeasible हों तो उन्हें अनमापा बताएँ—छोटे-length सफलता से 8L सफलता अनुमानित न करें।

**वैकल्पिक विस्तार:** पाँच या अधिक seeds; 256–512 evaluation samples; B का long-context training; बराबर search allowance वाला छोटा learning-rate sweep; compute-matched और parameter-matched secondary studies; अलग boundary/envelope choices; फिर वास्तविक scientific trajectory dataset। ये primary operator-only result से अलग रिपोर्ट हों।

मुख्य सीमाएँ: प्रस्तावित synthetic benchmark की external validity, केवल एक स्पष्ट Hyena realization, तीन seeds, budget-dependent optimization और slow-tail estimation। इन सीमाओं को अतिरिक्त स्रोत-विवरण के इंतज़ार का कारण नहीं, निष्कर्ष के दायरे के रूप में दर्ज करें।
````

**Stage**

````text
result
````

**Evidence**

````text
पूर्व निरीक्षण में workspace में केवल ./task.json मिला; उसमें सार्वजनिक प्रश्न और design-only सूचना थी। कोई setup implementation, dataset या विस्तृत source document उपलब्ध नहीं था। उपयोगकर्ता ने पुष्टि की है कि setup_4=मूल attention SiT और setup_5=non-causal Hyena SiT ही स्थापित setup विवरण हैं, और अतिरिक्त विवरण की प्रतीक्षा किए बिना प्रस्तावित configuration चुनना है। इसलिए benchmark समीकरण, SiT-style interpolant configuration, explicit gated signed-lag filters और सभी counts इस डिजाइन के चयन हैं। Sampling interval और lengths से durations सीधे निकलती हैं: 2048×0.125=256 तथा 16384×0.125=2048; अंतिम अवधि में 64-unit slow oscillation के 32 periods और rate 1/128 पर 16 expected hidden switches हैं। Data storage estimate केवल scalar-count arithmetic है, empirical profiling नहीं। कोई training, quality measurement, compute benchmark या empirical result प्रस्तुत नहीं किया गया है।
````

**Assumptions**

````text
[
  "प्रस्तावित compact SiT-style interpolant backbone task के नियंत्रित operator comparison हेतु स्वीकार्य है; यह स्रोत के अज्ञात SiT variant की पुष्टि नहीं करता।",
  "प्रस्तावित switching-driven oscillator benchmark पर सफलता वास्तविक trajectory domains तक स्वतः सामान्यीकृत नहीं होगी।",
  "भविष्य के execution चरण में उपयुक्त GPU तथा सामान्य tensor/FFT/attention software उपलब्ध कराया जाएगा; अभी hardware budget निर्धारित नहीं है।",
  "प्रस्तावित sample counts, update budget, 1% engineering-failure tolerance और slow-event sufficiency criteria अध्ययन के preregistered विकल्प हैं, उपलब्ध स्रोतों के तथ्य नहीं।"
]
````

**Uncertainties**

````text
[
  "मूल source architectures से proposed realization का संबंध सीमित है; निष्कर्ष exact source reproduction का नहीं होगा।",
  "Implicit Hyena filter तथा sinusoidal positions का unseen lags/positions पर व्यवहार empirical प्रश्न है; extension rule परिभाषित होना सफलता की गारंटी नहीं।",
  "सबसे लंबे attention runs की feasibility और दोनों models का convergence hardware budget पर निर्भर है।",
  "तीन seeds और rare-event tails की सीमित coverage से superiority तथा slow-event fidelity के confidence intervals चौड़े हो सकते हैं।"
]
````

### Event 5 — Simulator

**Message**

````text
अंतिम डिज़ाइन में rationale, controls और निष्कर्षों का पृथक्करण पर्याप्त स्पष्ट है। केवल दो sample-count असंगतियाँ ठीक करके संशोधित अंतिम डिज़ाइन दें; प्रयोग न चलाएँ। (1) Threshold-only pool में 200 paths हैं, लेकिन calibration में 128-128 के दो disjoint parent groups चाहिए—इसके लिए कम से कम 256 स्वतंत्र paths चाहिए। Pool और कुल dataset/storage counts बढ़ाएँ, या समान sample-size calibration की कोई स्पष्ट वैध योजना दें। (2) प्रति seed 128 samples पर शून्य failures होने पर भी one-sided 95% binomial upper bound लगभग 2.31% है; इसलिए 1% failure criterion प्रति seed पूरा नहीं हो सकता। स्पष्ट करें कि criterion किस स्तर पर लागू होगा और sample count उसके अनुरूप करें—उदाहरणतः प्रति seed/length कम से कम 299 samples पर शून्य failures इस सीमा के अनुकूल हैं। अलग trained seeds के outputs को बिना औचित्य एक समान failure probability वाले independent trials न मानें। इन परिवर्तनों के साथ calibration group sizes, evaluation counts और feasibility budget को परस्पर संगत रखें। शेष डिज़ाइन को बदलना आवश्यक नहीं है।
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
प्रस्तुत design-only deliverable मूल प्रश्न और सहमत तुलना को संबोधित करता है तथा कोई executed result नहीं बताता। किन्तु 200 calibration paths से दो disjoint 128-path groups नहीं बन सकते, और n=128 पर zero-failure one-sided 95% upper bound 1−0.05^(1/128)≈2.31% है; ये दोनों प्रस्तावित acceptance procedure के लागू होने में ठोस बाधाएँ हैं।
````

**Objectives Open**

````text
[
  "Calibration pool और disjoint group sizes में संगति",
  "Failure acceptance criterion के स्तर और sample size में संगति",
  "इन सुधारों सहित अंतिम design-only deliverable"
]
````

### Event 6 — Actor

**Answer**

````text
# संशोधित अंतिम प्रयोग-डिज़ाइन

दोनों sample-count असंगतियाँ ठीक की गई हैं: **threshold-only pool अब 600 independent paths**, और **evaluation अब प्रति trained seed, operator और length पर 300 independent generation attempts** होगा। Calibration में 300–300 के disjoint groups होंगे। 1% numerical/sampling-failure criterion प्रत्येक trained seed और length पर अलग लागू होगा। शेष वैज्ञानिक तुलना और controls अपरिवर्तित हैं। कोई प्रयोग नहीं चलाया गया है।

## 1. तथ्य, प्रस्ताव और प्रश्न
स्थापित स्रोत-विवरण केवल setup_4 का मूल attention SiT और setup_5 का non-causal Hyena SiT होना है। नीचे का benchmark, backbone, operator realization और budget प्रस्तावित विकल्प हैं, मूल source configurations के सत्यापित विवरण नहीं।

निष्कर्ष तीन अलग प्रश्नों पर दें:
- **क्षमता:** क्या Hyena अत्यंत लंबी, consistent, multiscale trajectories बनाता है?
- **तुलनात्मक गुणवत्ता:** साझा feasible lengths पर क्या attention से बेहतर गुणवत्ता है?
- **संसाधन:** क्या memory, runtime या attainable length में लाभ है?

Attention को हराना क्षमता सिद्ध करने की शर्त नहीं; दोनों सफल हो सकते हैं। Attention का OOM Hyena की quality superiority सिद्ध नहीं करता।

## 2. Benchmark और लंबाइयाँ
प्रस्तावित benchmark सात observed coordinates वाला switching-driven stochastic oscillator है। Sampling interval Δt=0.125 time units। Hidden regime s∈{−1,+1} symmetric continuous-time Markov process है, switch rate λ=1/128; sampled switch probability (1−exp(−2λΔt))/2 होगी।

तीन 2D oscillators के periods P=(1,8,64), damping times τ=(2,16,128) हों:

z_(j,n+1)=a_j R(2πΔt/P_j)z_(j,n)+(1+0.25s_n)√(1−a_j²)ε_(j,n),

जहाँ a_j=exp(−Δt/τ_j), ε स्वतंत्र N(0,I₂)। सातवाँ coordinate:

x_(n+1)=c x_n+(1−c)s_n+0.1√(1−c²)η_n,

जहाँ c=exp(−Δt/8), η स्वतंत्र N(0,1)। Model को hidden regime या innovations नहीं मिलेंगे। यही discrete recurrence benchmark की परिभाषा है। Slow regime और oscillator amplitudes का coupling multiscale coherence की परीक्षा देता है।

प्रत्येक स्वतंत्र path से पहले 4096-unit burn-in हटाएँ। Reference-only checks में initial-condition sensitivity मिले तो dataset lock करने से पहले burn-in बढ़ाएँ।

| Evaluation length | Steps | अवधि | P=64 cycles | Expected hidden switches/path |
|---|---:|---:|---:|---:|
| L_train | 2048 | 256 | 4 | 2 |
| 2L_train | 4096 | 512 | 8 | 4 |
| 4L_train | 8192 | 1024 | 16 | 8 |
| 8L_train | 16384 | 2048 | 32 | 16 |

अंतिम पंक्ति इस benchmark की ‘extremely long’ परिभाषा है: आठ गुना training context, 32 slow cycles और 16 slow damping times। Expected events को observed event coverage न मानें।

## 3. संशोधित dataset और calibration counts
प्रत्येक retained parent path 16384 steps का होगा। कुल **2800 स्वतंत्र paths**:

| Partition | Independent parent paths | उपयोग |
|---|---:|---|
| Train | 1200 | normalization और training crops |
| Tuning | 200 | optimization/sampler checks |
| Threshold-only calibration | 600 | reference-reference acceptance envelopes |
| Locked test | 800 | अंतिम independent reference comparisons |
| **कुल** | **2800** | |

Whole-trajectory split cropping से पहले होगा। कोई parent एक से अधिक partitions में नहीं जाएगा। Calibration और test से normalization या training नहीं होगी। छोटे-context training में केवल 2048-step crops दिखेंगी।

हर calibration replicate में 600 threshold-only parents को **दो disjoint groups, 300+300**, में partition करें। प्रत्येक parent से उस length का एक निर्धारित crop लें। इस प्रकार generated sample size 300 और reference-reference calibration sample size 300 समान होंगे। अलग lengths में वही parents इस्तेमाल हो सकते हैं; उनकी dependence simultaneous calibration में संरक्षित होगी। Repeated partitions को अतिरिक्त स्वतंत्र data न गिनें। Envelope uncertainty parent-level bootstrap से बताएँ।

Test comparisons के लिए प्रत्येक length पर 800 locked parents से outcomes देखने से पहले निर्धारित 300-parent reference group लें; reference-selection uncertainty को parent resampling से आँकें। सभी operators/seeds के लिए समान reference selection रखें। पूरे 800-path pool के descriptive summaries सहायक रूप में दें, पर उन्हें 300-sample calibrated acceptance test के साथ न मिलाएँ।

Observed float32 storage: 2800×16384×7×4 = **1,284,505,600 bytes**, लगभग **1.285 GB decimal या 1.196 GiB**, metadata/hidden labels अलग।

## 4. Operator-only configuration और leakage नियंत्रण
प्रस्तावित compact SiT-style backbone: प्रति timepoint सात coordinates का एक token, width 128, चार pre-normalized residual blocks, expansion-4 pointwise MLP, diffusion-time adaptive conditioning और seven-channel output। दोनों arms में identical fixed sinusoidal absolute-position embeddings हों; unseen positions पर उसी analytic formula का उपयोग हो।

Training objective: X_t=(1−t)ε+tX, t uniform और ε Gaussian; target velocity X−ε, समान MSE reduction। Sampling unconditional Gaussian से पूरे sequence पर 100-step Heun solver से हो। Calibration पर 200-step sensitivity check करें; जरूरत का बदलाव दोनों arms में test से पहले lock हो।

- **Attention:** चार heads, full bidirectional temporal attention, dropout zero।
- **Hyena:** चार channel groups, order-2 gated long convolutions। Tokenwise projection से g₁,g₂,v; y₀=v और y_i=g_i⊙(h_i*y_(i−1)), i=1,2; फिर output projection। Signed-lag implicit MLP filters में sign(k)log(1+|k|), fixed sinusoidal features और exp(−|k|/ρ) envelope हो। Positive learned ρ को 8,64,512,2048 steps पर initialize करें।

Length N पर signed lags −(N−1)…N−1 के लिए वही filter function evaluate करें। Kernel को N से rescale या refit न करें। Outside-sequence zero extension, circular convolution नहीं; FFT padding कम से कम 3N−2 और सही linear-convolution slice। छोटे inputs पर direct convolution और impulse-response tests हों।

बाकी backbone, conditioning, objective, sampler और precision समान रहें। Operator parameter counts अलग हो सकते हैं—उन्हें रिपोर्ट करें; मुख्य अध्ययन backbone-matched है। Optional parameter-matched comparison अलग होगा।

**Non-causal mixing leakage नहीं है:** training में दोनों arms current interpolated/noisy sequence के दोनों दिशाओं के positions देखते हैं; generation में current generated/noisy sequence देखते हैं। Held-out clean future, hidden regime या ground-truth prefix input नहीं है। Stitching और rolling windows मुख्य परीक्षण का भाग नहीं हैं।

## 5. Training और अलग length experiments
तीन paired training seeds; AdamW, learning rate 2×10⁻⁴, weight decay 0.01, clipping 1, 500-step warm-up, cosine decay, effective batch आठ crops, 10,000 updates और final EMA checkpoint, decay 0.999। Shared weights की initialization, crop order और training noise/time draws pair करें। Microbatch/accumulation बदल सकती है, effective exposure नहीं। दोनों arms को समान tuning अवसर मिलें।

यह fixed-budget study है, convergence का दावा नहीं। Calibration learning curves undertraining दर्शाएँ तो दोनों के लिए पहले से घोषित समान extension करें या limitation बताएँ।

**A—मुख्य zero-shot extrapolation:** train केवल 2048 पर; frozen models को 2048,4096,8192,16384 पर evaluate करें। Long-length outcomes देखकर retuning नहीं।

**B—वैकल्पिक long-context training:** नए models को 16384 पर effective batch एक और 10,000 updates से train करें। Total training tokens A के बराबर होंगे, batch/context structure नहीं; A बनाम B को pure operator contrast न कहें। दोनों arms के बीच B में controls समान रहें। Hyena-only feasible B run क्षमता दिखा सकता है, attention पर quality superiority नहीं।

## 6. Evaluation और acceptance thresholds
**हर operator × trained seed × length पर 300 independent generation attempts।** Generation randomness conditional on fixed trained weights स्वतंत्र होगी; paired operator runs में matching Gaussian tensors हो सकते हैं। तीन training seeds को एक समान failure probability वाले pooled Bernoulli trials नहीं मानेंगे।

Primary metric families:
1. **Fast/slow dynamics:** spectra, P=1,8,64 के आसपास [0.75/P,1.25/P] bands की power/peak position, complementary-band power; ACF lags 0.125,1,8,32,64,128,256 जहाँ valid हों।
2. **Regime dynamics/coupling:** x>0.5 तथा x<−0.5 hysteresis detector से observed dwell survival, switch rate, occupancy और regime-conditional oscillator energy। समान detector reference और generated paths पर; endpoint censoring का treatment हो।
3. **Consistency/drift:** trajectory quarters में mean, variance, energy, occupancy; slope और end-to-start change distributions। Edge/interior discrepancies अलग। Stationary reference के stochastic drift से तुलना हो, zero drift की माँग नहीं।
4. **Diversity:** standardized summary vectors की energy distance, reference-bin coverage, near duplicates। स्थिर या repeated outputs की smoothness सफलता नहीं है।
5. **Failures:** numerical/sampling failures, pathological finite excursions, तथा resource failures अलग। Failed attempts न हटाएँ और न replacement से छिपाएँ।

Threshold-only pool के 300-vs-300 partitions पर यही discrepancy metrics निकालें। प्रत्येक discrepancy को उसके reference-reference 95th-percentile scale से normalize करें; numerical floor पहले तय हो। Families और lengths के maximum standardized discrepancy की reference-only 95th percentile simultaneous acceptance envelope बने। यह प्रक्रिया model test results से पहले पूरी और frozen होगी। Drift, diversity और finite-excursion tolerance इसी reference-only आधार से तय हों।

**संशोधित numerical/sampling-failure criterion:** हर fixed trained model और length के 300 attempts पर failure probability का exact one-sided 95% Clopper–Pearson upper bound ≤1% होना चाहिए। शून्य failures पर bound:

1−0.05^(1/300) ≈ **0.009936 = 0.994%**,

इसलिए sample count अब criterion के अनुरूप है। 300 attempts में nonzero failures होने पर इस नियम के तहत criterion पूरा नहीं होगा। Criterion seed-wise है; तीन seeds के failures pool करके pass नहीं दिया जाएगा। इन individual 95% bounds को simultaneous 95% confidence statement भी नहीं कहेंगे।

OOM/timeout को इस Bernoulli numerical-failure criterion में न मिलाएँ: वह अलग execution-feasibility failure है। पूरा 300-attempt evaluation न हो पाए तो उस cell की क्षमता स्थापित नहीं होगी। Numerical failures हों तो primary pass नहीं; surviving trajectories के quality metrics केवल explicitly conditional diagnostics होंगे, 300-sample calibrated unconditional pass नहीं।

**Capacity decision:** 8L पर प्रत्येक seed में complete evaluation, failure criterion और सभी primary families के discrepancy upper uncertainty bounds का frozen envelope के भीतर होना आवश्यक होगा। तीन seeds के outcomes अलग दिखाएँ। Partial success को seed-dependent कहें। Envelope पार करती uncertainty होने पर ‘not established’; स्पष्ट exceedance पर संबंधित quality failure बताएँ। यह finite-sample operational fidelity है, distributional identity का प्रमाण नहीं।

## 7. Analysis और निष्कर्ष
Within-seed uncertainty independent generated/reference parents पर bootstrap से; cross-seed analysis paired-seed hierarchy से हो। Timesteps या overlapping crops को independent samples न मानें। तीन seeds की training-variability inference सीमित होगी।

साझा feasible lengths पर paired quality differences, per-family estimates और 95% intervals दें। Frozen maximum standardized discrepancy composite रखें। Superiority के लिए composite difference Hyena के पक्ष में हो और किसी primary family में reference-derived tolerance से बड़ी deterioration न हो। Multiple family comparisons पर Holm correction; nonsignificance को equivalence न कहें।

Slow-event adequacy प्रति seed/model/length और reference के लिए बताएँ: कम से कम 200 complete detected dwells, कम से कम 50 event-containing paths और switch-rate interval की relative half-width ≤25% प्रस्तावित gate है। अपर्याप्त coverage पर slow-event fidelity का सकारात्मक दावा रोकें। Reference में पर्याप्त पर generated data में कम events हों तो इसे संभावित dynamics failure मानें, केवल sampling limitation नहीं। Slow spectra और transition tails के निष्कर्ष अलग हों।

Outcome table में स्वतंत्र columns:
- Hyena long-trajectory capacity;
- attention के मुकाबले quality advantage;
- memory/runtime/attainable-length advantage।

दोनों pass हों तो दोनों की क्षमता; attention OOM और Hyena pass हो तो Hyena क्षमता और feasibility लाभ; Hyena तेज़ पर quality fail हो तो केवल resource लाभ।

## 8. संशोधित feasibility budget
**न्यूनतम अध्ययन:** दो operators × तीन seeds की छह trainings। सभी चार lengths feasible होने पर 2×3×4×300 = **7200 generation attempts**। प्रति operator/seed चार lengths में कुल 9,216,000 generated timepoints; पूरे मुख्य अध्ययन में **55,296,000 timepoints**। यह पिछले 128-sample प्रस्ताव की evaluation workload का **2.34375 गुना** है; training budget अपरिवर्तित है। 100-step Heun sampling की वास्तविक लागत इससे अलग profiler द्वारा मापी जाएगी, GPU-hour अनुमान नहीं गढ़ेंगे।

Output metrics batchwise निकालें; सभी samples memory में रखना जरूरी नहीं। Fixed hardware पर memory-efficient exact attention, microbatching और gradient accumulation अनुमत हैं; approximate attention replacement नहीं। 16384-length dense attention विशेष रूप से महँगा हो सकता है। Quality outcomes से पहले resource timeout/abort ceilings तय करें।

Preflight checks: configuration diff, attention mask, future-position influence, gradients, direct-vs-FFT convolution, no wraparound, sampler finiteness और peak-memory probes। Same hardware/precision पर parameters, tokens, accelerator-hours, peak memory, warm-start latency, per-token time और OOM boundary रिपोर्ट करें।

Budget 300 attempts/cell तक न पहुँचे तो count चुपचाप घटाकर वही 1% दावा न करें: अध्ययन को feasibility pilot या incomplete capacity evaluation कहें। Long-context experiment B, अधिक seeds, अधिक samples, compute/parameter-matched comparisons और वास्तविक-domain dataset वैकल्पिक extensions हैं। B करने पर भी वही 300-attempt per-seed/length failure policy लागू होगी।

मुख्य सीमाएँ यथावत: synthetic-domain external validity, proposed rather than source-verified SiT/Hyena realization, unknown hardware feasibility, optimization adequacy, तीन training seeds और slow-tail uncertainty।
````

**Stage**

````text
result
````

**Evidence**

````text
स्थानीय निरीक्षण में केवल task.json उपलब्ध था; source implementations या datasets नहीं थे। Setup_4/5 की पहचान उपयोगकर्ता द्वारा स्थापित है। कोई नया प्रयोग या profiling नहीं हुआ। संशोधित counts arithmetic के अनुसार संगत हैं: calibration pool 600=300+300 disjoint independent parents; dataset total 1200+200+600+800=2800; observed float32 storage 2800×16384×7×4=1,284,505,600 bytes। Fixed-model independent trials में zero failures का exact one-sided 95% binomial upper bound 1−0.05^(1/n) है: n=300 पर लगभग 0.994%, इसलिए 1% seed-wise criterion संभव है, जबकि n=128 पर नहीं था। Main evaluation में अधिकतम 7200 attempts और 55,296,000 generated timepoints हैं; ये planned workload counts हैं, executed outcomes नहीं।
````

**Assumptions**

````text
[
  "Benchmark, architecture, training budget और tolerances प्रस्तावित अध्ययन विकल्प हैं, मूल sources के अतिरिक्त तथ्य नहीं।",
  "हर fixed trained model/length के generation attempts स्वतंत्र random streams से होंगे; अलग training seeds की failure probabilities समान नहीं मानी जाएँगी।",
  "उपयुक्त भविष्य के execution resources उपलब्ध होने पर minimum evaluation में 300 attempts/cell पूरे किए जाएँगे; अधूरा evaluation capacity pass नहीं देगा।",
  "1% numerical/sampling-failure tolerance एक engineering choice है; individual per-cell confidence bounds simultaneous coverage का दावा नहीं करते।"
]
````

**Uncertainties**

````text
[
  "16384-step attention तथा 7200-attempt evaluation की hardware feasibility अभी अज्ञात है।",
  "तीन seeds training variability को सीमित precision से आँकेंगे; अतिरिक्त generated samples इस कमी का विकल्प नहीं हैं।",
  "Reference partitions की repetitions स्वतंत्र reference-data वृद्धि नहीं हैं; calibration-envelope uncertainty अलग रिपोर्ट करनी होगी।",
  "Slow-event tails और proposed operator की unseen-length fidelity empirical प्रश्न हैं; कोई परिणाम अनुमानित नहीं किया गया है।"
]
````

### Event 7 — Simulator

**Message**

````text
संशोधित अंतिम प्रयोग-डिज़ाइन स्वीकार है। दोनों sample-count असंगतियाँ दूर हुई हैं: 600 calibration paths से 300–300 के disjoint groups बनेंगे, और प्रति seed/length 300 attempts पर शून्य failures का 95% upper bound 1% से नीचे है। डिज़ाइन में rationale, निष्पक्ष operator comparison, leakage controls, multiscale fidelity और diversity metrics, uncertainty analysis तथा feasibility शामिल हैं। इसे design-only अंतिम deliverable रखें; इससे empirical सफलता या मूल source configuration के पुनरुत्पादन का दावा नहीं होता। अतिरिक्त संशोधन या प्रयोग चलाना आवश्यक नहीं है।
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
अंतिम रिपोर्ट में calibration और evaluation sample sizes संगत हैं, failure criterion seed-wise स्पष्ट है, और workload/storage counts संशोधित हैं। क्षमता, attention के मुकाबले गुणवत्ता और संसाधन लाभ अलग निष्कर्ष हैं। प्रस्तावित configuration तथा अज्ञात empirical outcomes स्पष्ट रूप से अलग रखे गए हैं; कोई निष्पादन दावा नहीं है।
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
  "event_log": "runs/openai-astra-top10-trial-1-batch-2/episodes/expbench_neurips2024_93022_6-b010093c1df2/candidate_001/attempt-1/output/neurips2024__93022__6/events.jsonl",
  "event_log_sha256": "d75cf8026f8fe921defecf188587a06bd981b4710b86549ec0e6cbe412679877",
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
