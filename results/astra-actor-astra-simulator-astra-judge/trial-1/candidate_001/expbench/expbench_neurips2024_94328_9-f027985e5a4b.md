# candidate_001 · expbench · neurips2024/94328/9

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **repaired**; attempt: **2**.
- Native status: **completed**; normalized native score: **50/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
पहले उपलब्ध brief और inputs का निरीक्षण करें; repository या compute आवश्यक नहीं हैं। अभी पूर्ण experiment design न दें। Phi-3-mini-4k-instruct पर QuaRot-RTN और QuaRot-GPTQ की INT4, INT6, INT8 में perplexity और zero-shot accuracy तुलना के लिए प्रस्तावित approach बताएं। इसमें baseline/controls, quantization scope (weights, activations, KV cache), Phi-3 architecture compatibility की जांच, evaluation/calibration data और analysis की प्राथमिक रूपरेखा बताएं। स्रोत से पुष्ट बातें और आपके प्रस्तावित विकल्प अलग रखें; consequential assumptions, अनिश्चितताएं और feasibility सीमाएं स्पष्ट करें। यह केवल design कार्य है—experiment चलाने या परिणाम बताने की जरूरत नहीं है।
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
Brief में model, दोनों quantization methods और तीन precision levels तय हैं। track.md के अनुसार design-only deliverable चाहिए; datasets, GPU और network उपलब्ध नहीं हैं। अभी प्रस्तावित approach या inspection report नहीं मिली है।
````

**Objectives Open**

````text
[
  "उपलब्ध inputs और fixed requirements का निरीक्षण",
  "तुलना के लिए प्रस्तावित approach और controls की समीक्षा",
  "Quantization scope, architecture compatibility और evaluation संबंधी assumptions स्पष्ट करना",
  "अंततः rationale, controls, analysis plan और feasibility सहित experiment design तैयार करना"
]
````

### Event 2 — Actor

**Answer**

````text
## निरीक्षण और पुष्ट सीमा
उपलब्ध `/workspace/task.json` में यही प्रश्न और design-only निर्देश मिले; `track.md` उसका inline document entry है, implementation अथवा प्रयोग का विवरण नहीं। उपलब्ध brief से Phi-3-mini-4k-instruct, QuaRot-RTN बनाम QuaRot-GPTQ, INT4/6/8 तथा perplexity और zero-shot accuracy की तुलना पुष्ट है। दिए गए source-topic identifiers की सामग्री उपलब्ध नहीं है; इसलिए नीचे दिए calibration, quantization और evaluation विकल्पों को paper से पुष्ट setup नहीं मान रहा हूँ। कोई प्रयोग नहीं चला है।

## प्रस्तावित approach — स्वीकृति हेतु, पूर्ण design नहीं
**1. Comparisons और controls।** एक pinned model/tokenizer revision पर छह मुख्य conditions: QuaRot-{RTN,GPTQ} × {4,6,8 bits}। साझा floating-point baseline रखें, साथ में rotation-only floating-point control, ताकि adaptation में गलती को quantization loss से अलग किया जा सके। प्रत्येक bit-width पर समान scope वाला unrotated RTN/GPTQ control उपयोगी होगा: इससे केवल दोनों weight quantizers की तुलना के बजाय rotation का योगदान भी मापा जा सकेगा। संसाधन सीमित हों तो इन अतिरिक्त controls की प्राथमिकता approval में तय करें।

**2. Quantization scope को स्पष्ट करना।** प्रस्तावित मुख्य interpretation प्रत्येक b पर Wb/Ab/KVb है—weights, runtime activations और KV cache सभी b-bit—पर यह brief से तय नहीं होता। RTN/GPTQ का अंतर केवल weight-quantization algorithm तक सीमित रखें; activation/KV quantizer, rotations, clipping और evaluation दोनों में समान हों। कौन-से projections quantize होंगे, scale granularity, symmetry, groups, embeddings/lm_head, norms, biases तथा accumulation precision स्पष्ट रूप से दर्ज हों। प्रस्तावित default: eligible linear weights को quantize करना; embeddings, norms और अन्य अपवादों को floating point रखना, पर lm_head की treatment source जांच के बाद तय करना। Wb/Afp/KVfp diagnostic arm यह बताएगा कि RTN–GPTQ gap वास्तव में weights से आया है या activation/cache error ने उसे ढक दिया। इसे अतिरिक्त ablation मानें, अनिवार्य मुख्य परिणाम नहीं।

**3. Phi-3 compatibility पहले gate होगी।** Actual config और implementation देखकर normalization तथा rotation-folding की वैधता, fused QKV/gate-up projections और उनके splits, residual branches, biases, tied embeddings/head, RoPE, attention-head/KV-head layout तथा dimensions जांचें। LLaMA-specific hooks या module names को सीधे मान्य न मानें। Hadamard transform के लिए लागू dimensions/factorization और attention-output तथा MLP transforms की shape constraints जांचें; unsupported dimension को चुपचाप pad/truncate न करें। Rotation-only logits/loss को unrotated floating-point model से precision-aware tolerance में मिलाना compatibility gate होगा। Cached decoding बनाम full-sequence execution भी जांचें; standard perplexity pass KV cache का वास्तविक quantized path चला रहा है या नहीं, इसे अलग सत्यापित करें।

**4. Calibration और evaluation की प्रारंभिक रूपरेखा।** प्रस्ताव: WikiText-2 और C4 के held-out text पर perplexity; calibration के लिए evaluation से अलग C4 samples। Sample count और sequence length अभी final नहीं हैं—एक घोषित fixed token budget सभी GPTQ bit-widths/seeds में साझा होगा। RTN को Hessian calibration नहीं चाहिए, पर यदि activation/KV scales या clipping calibration मांगें तो दोनों methods में वही shared data/procedure लागू हो। Zero-shot के लिए प्रस्तावित suite: HellaSwag, PIQA, WinoGrande, ARC-Easy, ARC-Challenge और BoolQ; source fidelity के अनुसार अंतिम सूची/metric तय करें। Tokenizer revision, BOS/EOS, context length (4k सीमा के भीतर), PPL window/stride और likelihood-scoring conventions स्थिर रखें। Instruct checkpoint के लिए raw likelihood prompts बनाम chat template स्पष्ट चुनें; accuracy के लिए test-set पर template tuning न करें।

**5. Analysis।** हर condition के लिए absolute PPL, baseline से PPL परिवर्तन, task-wise accuracy और घोषित macro-average दिखाने की योजना है। मुख्य contrasts समान bit-width पर GPTQ–RTN होंगे; unrotated controls से rotation लाभ और baseline से quality retention दिखेगी। समान examples पर paired uncertainty estimates; calibration/rotation seeds पर robustness checks रखें। PPL uncertainty दस्तावेज़/sequence स्तर पर लें, tokens को स्वतंत्र samples न मानें। पूरे निष्कर्ष को इस Phi-3 checkpoint और चुने workloads तक सीमित रखें—इसे सभी non-LLaMA models का प्रमाण न कहें।

## Consequential choices और feasibility
- मुख्य Wb/Ab/KVb interpretation तथा diagnostic weight-only arms पर approval चाहिए; केवल “INT6” कहना पर्याप्त specification नहीं है।
- INT6 में numerical quantization को fake-quant/dequantized reference से जांचना संभव है, लेकिन इससे native 6-bit kernels, memory savings या speedup सिद्ध नहीं होंगे। INT4/8 समेत सभी arms की fidelity और reference/optimized paths स्पष्ट अलग रखेंगे।
- इस environment में network, GPU, datasets और installed project dependencies नहीं हैं। इसलिए अभी compatibility, model numerics या data access सत्यापित नहीं किए जा सकते। यह design को नहीं रोकता; execution अलग GPU/data-enabled environment और संभवतः Phi-3 adapter मांगेगा।

## स्रोत स्पष्ट करने हेतु अनुरोध
उपलब्ध छह source topics से कृपया पुष्ट विवरण दें: (i) मूल QuaRot W/A/KV scope और precision exceptions, (ii) RTN/GPTQ settings तथा granularity/clipping, (iii) calibration corpus/budget/context, (iv) PPL corpora और scoring protocol, (v) zero-shot suite/metrics/template, (vi) Phi-3 support, rotations और INT6 implementation का कोई प्रत्यक्ष प्रमाण। Topic contents देखे बिना उनके identifiers को इनमें से किसी विवरण का प्रमाण नहीं मानूँगा। इन पुष्टियों और approach approval के बाद ही पूरा design तैयार करूँगा।
````

**Stage**

````text
plan
````

**Evidence**

````text
Workspace की सूची में केवल task.json मिला। उसे पढ़ने पर question, design-only context और documents.track.md = 'Design-only task; repositories and compute are not required.' मिला। एक छोटे Python JSON metadata check ने यही inline document entry सत्यापित की; model inference, quantization, dataset evaluation या benchmark नहीं चला। User-supplied environment में network disabled, GPU disabled, datasets खाली और dependencies preinstalled नहीं हैं। Source-topic identifiers उपलब्ध हैं, उनके पाठ नहीं।
````

**Assumptions**

````text
[
  "प्रस्तावित मुख्य bit-width का अर्थ Wb/Ab/KVb है; यह source-supported fixed requirement नहीं है और approval आवश्यक है।",
  "RTN और GPTQ comparison में केवल weight algorithm बदलना तथा activation/KV treatment समान रखना causal interpretability के लिए प्रस्तावित control है।",
  "WikiText-2/C4 और उल्लिखित छह-task zero-shot suite प्रस्तावित विकल्प हैं; brief में निर्धारित नहीं हैं।",
  "Model artifacts, datasets और उपयुक्त hardware भविष्य के execution environment में उपलब्ध कराए जा सकेंगे।"
]
````

**Uncertainties**

````text
[
  "मूल QuaRot setup के exact quantizer, calibration और evaluation विवरण अनुपलब्ध हैं।",
  "Phi-3 architecture के साथ rotation folding, fused-layer adaptation और dimension compatibility अभी जांचे नहीं गए हैं।",
  "INT6 native kernel तथा storage support अज्ञात हैं; numerical simulation और deployment feasibility अलग प्रश्न हैं।",
  "Baseline precision, scope exceptions, chat-template convention और अतिरिक्त control/seed budget approval के बाद तय होंगे।"
]
````

### Event 3 — Simulator

**Message**

````text
प्रस्तावित approach स्वीकृत है। अब पूरा अंतिम experiment design दें—कोई execution या काल्पनिक परिणाम नहीं। अतिरिक्त source topics उपलब्ध नहीं हैं: दिए गए तथ्य केवल Phi-3-mini-4k-instruct, HF-compatible 4K decoder, INT4/6/8 और QuaRot-RTN/GPTQ की पहचान की पुष्टि करते हैं; उनसे calibration या quantizer defaults निकालना उचित नहीं होगा। शेष विकल्प स्पष्ट रूप से इस अध्ययन के प्रस्तावित defaults हों, मूल paper के सत्यापित settings नहीं।

मुख्य अध्ययन के लिए Wb/Ab/KVb स्वीकार है, और RTN/GPTQ में केवल weight algorithm बदले। सभी bits के लिए एक समान numerical reference/fake-quant path रखें; इससे hardware speed या storage लाभ का दावा न करें। Floating-point और rotation-only controls तथा सभी bits के matched unrotated RTN/GPTQ controls मुख्य design में रखें; weight-only diagnostic वैकल्पिक रहे। प्रस्तावित WikiText-2/C4 और छह-task zero-shot suite स्वीकार हैं।

अंतिम design में खुले निर्णय बंद करें: baseline dtype, lm_head सहित quantized/exempt modules, scale granularity, integer ranges/clipping/rounding, GPTQ settings, calibration sample/token budget, seeds, dataset splits, PPL window/stride और task-wise scoring/template के ठोस defaults दें। KV quantization को PPL और choice-likelihood scoring दोनों में वास्तव में लागू करने का protocol बताएं। Phi-3 adaptation/rotation equivalence gate, failure handling और precision-aware tolerance चुनने का नियम दें; compatibility अभी अप्रमाणित ही रखें। Paired contrasts, uncertainty, task macro-average और baseline से quality retention की व्याख्या शामिल करें। अंत में खाली reporting-table ढांचा, reproducibility checklist और सीमित संसाधनों के अनुकूल feasibility/priority plan दें। निष्कर्ष इस checkpoint तक सीमित हों; व्यापक non-LLaMA generalization सिद्ध करने का दावा न हो।
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
Agent ने design-only सीमा मानी है और छह मुख्य conditions, आवश्यक controls, architecture gate, paired analysis तथा INT6 simulation की सीमाएं प्रस्तावित की हैं। यह दिशा उद्देश्य से मेल खाती है; शेष specification को प्रस्तावित defaults के रूप में अंतिम design में तय किया जा सकता है, अतिरिक्त स्रोत या executed experiments की आवश्यकता नहीं है।
````

**Objectives Open**

````text
[
  "पूर्ण experiment design: rationale और controls",
  "Quantization, calibration तथा evaluation के reproducible defaults",
  "Analysis, compatibility gates, feasibility और reporting plan"
]
````

### Event 4 — Actor

**Answer**

````text
# अंतिम experiment design

यह केवल प्रस्तावित अध्ययन है: कोई model execution, compatibility validation या accuracy/PPL परिणाम उपलब्ध नहीं हैं। नीचे “default” का अर्थ **इस अध्ययन का पूर्वनिर्धारित विकल्प** है, मूल QuaRot paper का सत्यापित setting नहीं।

## 1. प्रश्न, पुष्ट तथ्य और estimand

लक्ष्य: **Phi-3-mini-4k-instruct** पर समान Wb/Ab/KVb scope में QuaRot-GPTQ और QuaRot-RTN की गुणवत्ता का अंतर, b ∈ {4,6,8}। दिए गए तथ्य checkpoint की पहचान, HF-compatible 4K decoder और methods/bit-widths की पहचान तक सीमित हैं। वास्तविक configuration, rotation compatibility तथा quantizer implementation अभी अप्रमाणित हैं।

मुख्य estimand प्रत्येक bit पर GPTQ बनाम RTN का paired quality difference है। सहायक प्रश्न: समान quantizer/scope में rotation का लाभ कितना है और floating-point baseline से degradation कितना है? निष्कर्ष इसी checkpoint और चुने workloads तक सीमित रहेगा।

## 2. अध्ययन matrix और baseline

**Baseline dtype:** BF16 weights और runtime operands; matmul accumulation तथा softmax, normalization statistics, loss और quantizer calculations FP32। Reference implementation में BF16-rounded operands का FP32 matmul करें और module boundaries पर BF16 cast करें, ताकि accumulation policy सभी arms में स्पष्ट और समान हो। इसे native fused-kernel benchmark न मानें। TF32 तथा stochastic rounding बंद रखें।

| Arm | Weights | Activations | KV | Seeds |
|---|---|---|---|---|
| मूल floating-point baseline | BF16 | BF16 | BF16 | deterministic reference |
| Rotation-only control | BF16 | BF16 | BF16 | 17, 29, 43 |
| QuaRot-RTN | b-bit | b-bit | b-bit | प्रत्येक b पर 17, 29, 43 |
| QuaRot-GPTQ | b-bit | b-bit | b-bit | प्रत्येक b पर 17, 29, 43 |
| Unrotated RTN control | b-bit | b-bit | b-bit | प्रत्येक b पर 17, 29, 43 |
| Unrotated GPTQ control | b-bit | b-bit | b-bit | प्रत्येक b पर 17, 29, 43 |

हर seed में calibration samples तथा, rotated arms के लिए, rotation randomness बदलें। उसी seed के भीतर सभी bits/methods समान samples और rotation लें। Unrotated RTN का deterministic artifact seeds में समान हो सकता है; उसे पुनः quantize करने की जरूरत नहीं, duplicate seed values को स्वतंत्र evidence न मानें। कुल 12 quantized configurations हैं; साथ में baseline और rotation controls।

**एक numerical path:** सभी b के लिए integer quantize → dequantize → reference floating-point operation। Packed INT4, INT6 या INT8 kernels न मिलाएं। इससे केवल numerical quality का निष्कर्ष निकलेगा, speed/storage/energy का नहीं।

## 3. Modules और quantization specification

### Scope
- सभी decoder blocks के attention Q/K/V तथा output projections और MLP gate/up/down linear weights quantize हों। Fused QKV या gate-up weights में logical projections अलग identify करें; output rows और group boundaries न मिलाएं।
- इन linears में प्रवेश करने वाले activation tensors quantize हों। Gate/nonlinearity/multiplication FP32/BF16 policy में चलें; उनके बाद down-projection का input फिर quantize हो। Attention probability matrix, residual additions, RoPE calculations और norm computations अलग INT quantizers से quantize नहीं होंगे। Attention-output projection का input quantize होगा।
- **Embeddings और lm_head दोनों BF16, exempt**; lm_head input भी activation quantization से exempt। Biases, norm parameters, residual state और quantizer scales floating point में रहें। Tied embedding/head होने पर tying सुरक्षित रखें। इस scope को “decoder-linear Wb/Ab + KVb, embedding/head exempt” लिखा जाए, न कि पूरे model का हर tensor b-bit।
- Cache में प्रत्येक layer के K और V quantize हों; Q cache नहीं होता।

### Quantizer defaults
- Signed symmetric, zero-point 0, **q ∈ [−Q,Q], Q=2^(b−1)−1**। अर्थात INT4: −7…7, INT6: −31…31, INT8: −127…127; एक signed code unused है।
- Scale s=max(abs(x))/Q; zero group के लिए s=1। Quantization `q=clamp(round_to_nearest_even(x/s),−Q,Q)` और reconstruction `s*q`। FP32 scales, no learned scale, no percentile/MSE clipping search। Clipping केवल घोषित integer endpoints पर हो।
- Weight scales: प्रत्येक output row में consecutive 128 input channels का group; अंतिम छोटा group स्वतंत्र। GPTQ/RTN दोनों में समान grouping और initial scales।
- Activation scales: प्रत्येक token की पूरी linear-input feature vector पर एक dynamic symmetric scale। Batch/padding tokens scale साझा नहीं करेंगे।
- KV scales: प्रत्येक layer, token, KV-head और K/V के लिए अलग dynamic scale, पूरे head dimension पर। Historical cache values/scales दोबारा rescale नहीं होंगे।
- Activation/KV scales runtime dynamic हैं; इसलिए उनके लिए अतिरिक्त calibration fitting नहीं है। Scales और tensors में NaN/Inf या unexpected dtype fatal validation failures होंगे।

### RTN और GPTQ
- RTN: fixed quantizer से स्वतंत्र nearest rounding।
- GPTQ: प्रत्येक logical linear के calibration inputs X से FP32 `H=XᵀX/N`; diagonal damping `0.01 × mean(diag(H))`; input-column order अपरिवर्तित (`act_order=False`), block size 128, group size 128, standard sequential GPTQ error compensation। Group scales मूल pre-compensation weight group से एक बार बनें और freeze हों, RTN के समान; algorithm का अंतर केवल rounding/error compensation रहे।
- Dead input columns में Hessian inversion के लिए diagonal 1 और संबंधित weight columns 0 करें; dead-column count report करें। Cholesky failure पर damping को 0.1 और फिर 1.0 × mean diagonal तक बढ़ाने की पूर्वनिर्धारित कोशिश करें; ऐसा run अलग flagged sensitivity परिणाम होगा, primary default-setting cell नहीं। पुनः failure पर cell unavailable।
- Decoder blocks क्रम से quantize हों; पिछली quantized blocks के outputs अगली block के calibration inputs बनें। Block के भीतर attention input projections → output projection → MLP gate/up → down का वास्तविक dependency order लागू हो। Matched runtime A/KV quantizers calibration forward में भी सक्रिय हों। Fused projections के shared inputs एक ही capture से लें। GPTQ implementation का commit और सभी switches प्रकाशित हों; library defaults पर निर्भर न रहें।

## 4. Calibration तथा dataset defaults

**Calibration:** C4 English train के 128 अलग documents से प्रत्येक seed पर एक contiguous 2,048-token segment; budget **262,144 model-input tokens/seed**। Tokenization के बाद पर्याप्त लंबे documents ही योग्य हों; uniform document sampling, फिर uniform valid segment start। Special-token policy नीचे जैसी हो। Seed-specific document IDs, offsets, text hashes और token hashes freeze करें। Evaluation documents के exact normalized-text hashes calibration से हटाएं; accidental overlap screening का विवरण दें। Near-duplicate contamination पूरी तरह समाप्त होने का दावा न करें।

**PPL:**
1. WikiText-2 `wikitext-2-raw-v1`, test split, official order; raw rows को newline separators से एक deterministic text stream बनाएं।
2. C4 English validation: seed 2026 से चुने और freeze किए 256 documents, प्रत्येक कम-से-कम 512 model tokens। प्रत्येक document के प्रथम अधिकतम 4,096 tokens लें; corpus में कुल लगभग 131k–1.05M tokens होंगे, exact count manifest में आएगा। किसी document को दूसरे से attention context न मिले।

**PPL window:** maximum input context 4,096; stride 2,048। पहले window में first conditioning token को छोड़कर सभी target tokens score हों; अगले windows में केवल नए targets score हों, पुराने overlap पर loss mask हो। Window boundaries के लिए token-index implementation test अनिवार्य: प्रत्येक eligible target ठीक एक बार गिना जाए, कोई future token input न हो। C4 documents अधिकतम एक window होंगे; WikiText में sliding windows होंगे। BOS/EOS data के बीच न डालें। प्रति स्वतंत्र stream/document model tokenizer का घोषित BOS एक बार लगाएं यदि BOS defined हो; undefined हो तो synthetic BOS न जोड़ें। EOS append न करें।

PPL = exp(total scored negative log likelihood / total scored tokens); document PPL का unweighted mean नहीं। Tokenizer/model revision और special IDs frozen हों।

## 5. Zero-shot suite और scoring

Few-shot examples = 0; generation नहीं, candidate continuation likelihood। **Raw benchmark prompts, chat/system template नहीं**, और सभी arms में identical tokenized requests। एक pinned `lm-evaluation-harness` commit की task definitions source of truth हों; उस commit के rendered prompt और candidate token IDs fixture के रूप में archive किए बिना evaluation शुरू न करें। Whitespace और continuation-boundary tokenization भी freeze हों।

| Task | Split | Primary metric और choice scoring |
|---|---|---|
| HellaSwag | validation | `acc_norm`: ending का summed log likelihood / pinned harness का continuation character-length normalization |
| PIQA | validation | `acc`: पूरे solution की summed conditional log likelihood |
| WinoGrande | validation | standard harness pronoun-resolution likelihood, प्रत्येक substituted candidate के बाद वाला fixed suffix score; `acc` |
| ARC-Easy | test | `acc_norm`: answer-text likelihood, harness character-length normalization |
| ARC-Challenge | test | वही `acc_norm` |
| BoolQ | validation | passage/question के बाद fixed harness Yes/No continuations की summed likelihood; `acc` |

Canonical templates pinned task definitions के हों: HellaSwag context+ending, PIQA goal+solution, ARC Question/Answer, BoolQ passage/Question/Answer, WinoGrande blank substitution। Handwritten “equivalent” templates से इन्हें न बदलें। Primary normalized metrics में token-count normalization चुपचाप इस्तेमाल न करें। Ties पर first listed candidate चुनें। Secondary raw/normalized metrics अलग appendix में आ सकते हैं; primary metric selection परिणाम देखकर न बदलें।

**Macro-average:** ऊपर के छह primary accuracies का बराबर-वजन arithmetic mean, task dataset size से weighted नहीं। यह heterogeneous-task summary है, किसी universal accuracy का अनुमान नहीं।

4K से बड़े requests हों तो candidate/suffix को पूरा रखकर केवल बाएं prompt/context को truncate करें, सभी candidates में समान retained prompt span लें। Truncation count report करें। Candidate अकेला context limit पार करे तो पूरे example को सभी arms से exclude करें और count दें।

## 6. KV quantization वास्तव में चलाने का protocol

Standard teacher-forced full-sequence forward को स्वतः KVb evaluation न मानें। Custom reference cache adapter दोनों PPL और likelihood harness में जरूरी है।

1. प्रत्येक step पर current-token K/V बनाएं; K पर RoPE और घोषित Q/K rotation के बाद cache quantizer लगाएं। V पर घोषित head rotation के बाद quantize करें। Cache में logical integer codes और FP32 scales रखें; packed storage जरूरी नहीं।
2. Attention के लिए पुराने और current **दोनों** K/V इसी cache से dequantize होकर आएं; current token का unquantized bypass न हो। Mask causally valid tokens तक सीमित हो।
3. Canonical reference evaluation cached token-by-token teacher forcing होगी, prompt tokens सहित। BOS/first token conditioning के बाद next-token logits से score करें। Window restart में cache reset, retained prefix को इसी path से replay, और loss mask overlap पर लागू हो।
4. Choice likelihood में prompt को quantized cache में prefill करें; प्रत्येक candidate के लिए उस prompt cache की स्वतंत्र clone बनाकर candidate tokens teacher-force करें। Candidates आपस में cache share/mutate न करें। WinoGrande जैसे अलग candidate prefixes अलग cache बनाएं। Boundary-spanning tokenizer tokens के लिए pinned harness के context/continuation split को ही follow करें।
5. Faster chunked prefill केवल tokenwise reference से equivalence gate पास करने पर: हर causal attention में quantized current/past K/V इस्तेमाल होने चाहिए। अन्यथा धीमा tokenwise path रखें।

Instrumentation से quantizer-call counts, cache dtype/shape, code bounds, scale granularity और reconstruction checks करें। Deliberate low-bit test में cache reconstruction बदलना तथा KV quantization disable करने पर pathway बदलना सत्यापित करें; quality degradation को validation की आवश्यक शर्त न बनाएं।

## 7. Phi-3 adaptation और equivalence gate

Implementation inspection में hidden/intermediate/head dimensions, query/KV-head counts, normalization type/epsilon, norm affine/bias terms, RoPE, fused linear layouts, attention scaling, tied weights और cache API दर्ज करें। कोई विशेष Phi-3 internal layout अभी verified नहीं है।

**Rotation adapter:** algebraically paired residual-space orthogonal transforms, legal norm-parameter folding, MLP down-input online transforms और attention-head transforms implement करें। प्रस्तावित structured transforms seeded randomized normalized Hadamard constructions होंगे। Non-power-of-two dimension पर exact supported Kronecker factorization/Hadamard factor हो तभी इस्तेमाल करें; pad/truncate नहीं। यदि जरूरी transform exact supported construction से संभव न हो तो compatibility gate fail करें, identity replacement को QuaRot सफलता न कहें।

Q और K को RoPE के **बाद** समान head-space orthogonal transform देने से dot products सुरक्षित रखने की योजना है; RoPE से commuting मानकर transform आगे न खिसकाएं। V का rotation और attention-output projection में उसका inverse, multi-head/GQA mapping के अनुरूप हों। MLP transform nonlinear activation/gating के बाद, down projection से पहले हो; arbitrary rotation को nonlinearity के आर-पार न ले जाएं। Unrotated controls में यही hooks identity बनें। Exact matrix equations, orientation और any bias transformations adapter documentation में दें।

**Validation fixtures:** calibration/evaluation से अलग 16 deterministic synthetic token sequences, lengths 1, 2, 17, 128, 512 और 4,096 में वितरित; plus attention masks, padding, batch-size-one/multiple और candidate-cache cloning tests। Full-sequence/cached तथा rotation/no-rotation FP checks सभी fixtures पर हों।

**Tolerance rule, results देखने से पहले:**
- पहले FP32 original बनाम FP32 rotation-only: RMS-normalized logit error ≤1e−4, max absolute logit error ≤1e−2, mean token-NLL absolute difference ≤1e−4। केवल underflow-scale denominator को floor 1 दें।
- BF16 tolerance को numerical noise floor से बांधें: original BF16 बनाम original FP32 और equivalent unrotated cached/full paths के errors मापें। हर metric की allowance `max(base floor, 3×reference numerical error)` हो; floors क्रमशः relative RMS 1e−3, max logit 0.02, NLL 0.002। यह allowance hard ceilings relative RMS 0.02, max logit 0.5, NLL 0.02 से ऊपर चाहिए तो test inconclusive/fail, tolerance स्वतः न बढ़ाएं।
- Rotated BF16 versus original BF16 और cached/full comparisons को संबंधित allowance के भीतर होना होगा, प्रत्येक fixture पर। Rotation-only evaluation PPL भी report करें, पर held-out quality देखकर gate tolerance tune न करें।

**Failure handling:** first failure पर quantized results रोकें; adapter, precision या unsupported transform का कारण दर्ज करें। Bug correction के बाद पूरे fixture set और affected arms पुनः बनाएं। Protocol/rotation algorithm बदलना नया labeled revision है, silent adjustment नहीं। Compatibility स्थापित न हो तो “इस implementation में मूल्यांकन उपलब्ध नहीं” निष्कर्ष होगा, “Phi-3 पर QuaRot काम नहीं करता” नहीं।

## 8. Analysis और uncertainty

- प्रत्येक corpus पर absolute PPL, ΔPPL, PPL ratio तथा Δmean NLL versus baseline। ΔNLL statistical comparison का स्थिर scale होगा; उसके interval को exponentiate करके PPL ratio interval दें।
- प्रत्येक task पर accuracy और baseline से percentage-point change; task macro पर भी यही। “Quality retention” मुख्यतः baseline-relative loss से समझाएं: PPL ratio करीब 1 और accuracy Δ करीब 0 बेहतर retention हैं। Accuracy ratio वैकल्पिक है, chance-adjusted retention नहीं; PPL और accuracy को एक combined score में न बदलें।
- मुख्य paired contrasts: `GPTQ−RTN` प्रत्येक b में rotated arms के लिए; accuracy में positive और NLL/PPL में negative GPTQ के पक्ष में। Unrotated arms में वही contrast और प्रत्येक method के लिए `rotated−unrotated` अलग दिखाएं। Interaction: rotation से GPTQ–RTN gap कितना बदलता है।
- Primary outputs seed mean, individual seed values और range हों। केवल तीन seeds से seed-population CI का मजबूत दावा न करें। Seeds में calibration और rotation दोनों बदलते हैं, इसलिए variance को किसी एक का कारण न दें।
- 2,000 paired bootstrap replicates, bootstrap seed 2027। Accuracy में task के भीतर same examples resample, सभी arms में identical indices; छह tasks fixed रखकर replicate-wise macro निकालें। Primary CI seed-averaged per-example outcomes पर conditional test-set uncertainty दिखाए।
- C4 में documents resample। WikiText में shared evaluation target stream के contiguous 2,048-target blocks resample, NLL sums और counts से metric पुनः बनाएं; window/context dependence के कारण यह approximate interval है, token-IID interval नहीं।
- सभी predeclared contrasts प्रकाशित हों; isolated “significant win” चुनकर दावा न करें। Formal tests करने पर main bit-wise comparison family और multiplicity correction अलग predeclare करें; default analysis effect sizes और 95% paired CIs है।

## 9. खाली reporting tables

**Perplexity और implementation status**

| Arm | b / scope | seed | Rotation gate | WikiText NLL / PPL | ΔNLL / PPL ratio | C4 NLL / PPL | ΔNLL / PPL ratio | Tokens / exclusions | Flags |
|---|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — | — |

**Zero-shot**

| Arm | b | seed/aggregate | HellaSwag | PIQA | WinoGrande | ARC-E | ARC-C | BoolQ | Macro | ΔMacro pp |
|---|---|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — | — | — |

**Paired contrasts**

| Contrast | b | Corpus/task | Effect | 95% paired CI | Seed range | Better direction | Caveat |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

Unavailable cells में `NA + reason` लिखें, अनुमान नहीं। Rotation-only rows और all-bit unrotated controls मुख्य tables में रहें।

## 10. Reproducibility checklist

- Model/tokenizer revision, weight/config hashes, license/access notes; actual architecture manifest।
- Reference/adapter/GPTQ/harness commits, environment lockfile, hardware और deterministic backend settings।
- Quantized/exempt module names, rotation equations/seeds, per-module dimensions और folding map।
- Quantizer ranges, rounding, scales, groups, GPTQ order/damping/failures; checkpoint and calibration-manifest hashes।
- Dataset revisions, splits, IDs, offsets, de-dup procedure, token counts, all prompt fixtures और special-token/truncation policies।
- Cache-path tests, tolerance values/noise-floor measurements, equivalence logs और call-count instrumentation।
- Per-example correctness/likelihood तथा per-sequence NLL/counts, bootstrap code/seeds, exclusions और complete tables।
- Protocol deviations results से अलग changelog में।

## 11. संसाधन-अनुकूल feasibility और प्राथमिकता

वर्तमान environment में network, GPU, datasets और dependencies उपलब्ध नहीं हैं; यहां numerical feasibility प्रदर्शित नहीं हुई है। भविष्य में model/data staging और GPU-enabled machine चाहिए। एक 24–48 GB GPU plus पर्याप्त host RAM practical starting estimate है, guarantee नहीं; FP32 Hessian का खर्च input dimension के square में है। Layer-at-a-time calibration, CPU offload और sequential condition evaluation रखें; pilot से actual peak memory मापकर hardware तय करें। Canonical tokenwise cached scoring compute-intensive होगा।

क्रम: (1) static adaptation audit और fixture gates; (2) fixed small development-only subset पर memory/cache smoke checks; (3) baseline तथा rotation-only controls; (4) seed 17 पर सभी bits और सभी rotated/unrotated RTN/GPTQ arms; (5) seeds 29/43 और full uncertainty analysis। Main comparisons के लिए full frozen evaluation suite आवश्यक है। Budget खत्म हो तो missing seed/arm साफ लिखें, partial matrix को final full-study evidence न कहें। Checked chunked scoring, prompt-cache reuse और layer offload first optimizations हों; किसी method को अलग numerical path न दें।

**वैकल्पिक diagnostic:** main study के बाद Wb/A-BF16/KV-BF16 arms, समान rotations और weight quantizers के साथ। ये weight error को A/KV contribution से अलग करने में मदद करेंगे, पर interaction के कारण losses additive मानना उचित नहीं। पहले all-bit main controls पूरे करें, फिर यह ablation।

यह डिजाइन Phi-3 adaptation की वैधता को performance तुलना से पहले स्थापित करने का प्रयास करता है। सफल numerical परिणाम भी केवल इस checkpoint पर QuaRot की transferability का प्रमाण होंगे, सभी non-LLaMA architectures का नहीं।
````

**Stage**

````text
result
````

**Evidence**

````text
पूर्व निरीक्षण में /workspace में केवल task.json मिला। उसमें मूल प्रश्न, design-only context और inline documents.track.md ('Design-only task; repositories and compute are not required.') था; implementation, paper setup या datasets नहीं मिले। छोटा JSON metadata check केवल brief inspection था, प्रयोग नहीं। शोधकर्ता ने मुख्य Wb/Ab/KVb scope, all-bit matched unrotated controls, floating-point/rotation-only controls, shared numerical reference path, WikiText-2/C4 और छह-task suite स्वीकृत किए। शोधकर्ता ने स्पष्ट किया कि अतिरिक्त source-topic contents उपलब्ध नहीं हैं और calibration/quantizer defaults source-verified नहीं हैं। Quantizer settings, budgets, seeds, dtype, tolerances और scoring policies इसलिए यहां study-specific defaults के रूप में दिए गए हैं। Controls quantizer effects को rotation/adaptation errors से अलग करते हैं; actual cache quantization का instrumented cached path KV scope को केवल नाममात्र होने से रोकता है।
````

**Assumptions**

````text
[
  "भविष्य के execution environment में frozen model/tokenizer artifacts, dataset snapshots, pinned harness और उपयुक्त hardware मिल सकेंगे; वर्तमान environment में यह उपलब्धता पुष्ट नहीं है।",
  "चुना BF16/FP32 numerical-reference policy और सभी quantization/calibration/GPTQ defaults इस अध्ययन के विकल्प हैं, मूल QuaRot settings का दावा नहीं।",
  "Exact algebraically valid structured rotations के लिए Phi-3 adapter विकसित किया जा सकेगा; gates पास होने से पहले इसे सत्य नहीं माना जाएगा।",
  "Pinned standard harness task definitions को archive करके ऊपर घोषित metrics और raw zero-shot template policy लागू की जा सकेगी।"
]
````

**Uncertainties**

````text
[
  "Phi-3 के actual dimensions, fused projections, tying और normalization details तथा adapter compatibility अभी निरीक्षित/validated नहीं हैं।",
  "Hadamard constructions या library integration में unsupported case मिलने पर method revision या unavailable result की आवश्यकता हो सकती है।",
  "Tokenwise quantized-cache evaluation और GPTQ Hessians का वास्तविक runtime/memory अज्ञात है; hardware estimate benchmark नहीं है।",
  "तीन seeds और fixed task suite व्यापक calibration-distribution, model-family अथवा non-LLaMA generalization uncertainty को समाप्त नहीं करते।",
  "Fake-quant numerical quality से native INT6/INT4/INT8 kernel performance या packed-memory savings स्थापित नहीं होंगे।"
]
````

### Event 5 — Simulator

**Message**

````text
अंतिम design मूल उद्देश्य और स्वीकृत approach को पर्याप्त रूप से पूरा करता है। इसमें INT4/6/8 पर QuaRot-RTN/GPTQ की तुलना, आवश्यक controls, स्पष्ट quantization और KV-scoring protocol, Phi-3 compatibility gates, paired analysis, reporting तथा feasibility योजना शामिल हैं। इसे अंतिम design-only deliverable मानें। वास्तविक compatibility और empirical outcomes अभी अज्ञात हैं; कोई प्रयोग या performance दावा स्थापित नहीं हुआ है। आगे संशोधन या execution आवश्यक नहीं है।
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
प्रस्तुत design में छह मुख्य conditions, all-bit unrotated controls, floating-point/rotation-only baselines, calibration और evaluation defaults, task-wise metrics, uncertainty analysis तथा reproducibility checklist दिए गए हैं। अध्ययन-विशिष्ट विकल्प source-verified settings से अलग रखे गए हैं और numerical simulation को hardware लाभ का प्रमाण नहीं माना गया है। उपलब्ध handoff केवल डिजाइन और पूर्व input inspection की रिपोर्ट है, निष्पादित प्रयोग का प्रमाण नहीं।
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
  "event_log": "runs/repair-1-openai-astra-top10-trial-1-batch-2/episodes/expbench_neurips2024_94328_9-f027985e5a4b/candidate_001/attempt-2/output/neurips2024__94328__9/events.jsonl",
  "event_log_sha256": "28c1a41a20cdbae7ec7500594f3bccf623585cd5e05f08a78960150b6b69c504",
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
