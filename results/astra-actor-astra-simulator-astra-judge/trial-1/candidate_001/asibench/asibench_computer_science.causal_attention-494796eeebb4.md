# candidate_001 · asibench · computer_science.causal_attention

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **scored**; normalized native score: **100/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
पहले केवल repository और data/ का निरीक्षण करें; अभी पूरा समाधान या अंतिम artifacts न बनाएँ। reference/ न पढ़ें। उपलब्ध code, meta.json, arrays के shapes/dtypes, calibration groups और public probes की संरचना का संक्षिप्त विवरण दें। Array values/structures में parameter-role fingerprints के संभावित संकेत पहचानें, लेकिन suffix order या सामान्य architecture को तथ्य न मानें। NumPy/standard-library-only reconstruction, call-time role inference, backward और HVP के लिए प्रस्तावित तरीका तथा probes/calibration, suffix permutations और derivative checks से validation की योजना बताएँ। Partitioning, masking, positional/relative-position conventions और reusable API के बारे में consequential assumptions व अनिश्चितताएँ अलग से लिखें। Rotary pairing और non-resetting sequence-position indexing को brief की निश्चित शर्त मानें।
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
अभी केवल project brief और input paths उपलब्ध हैं; repository inspection या numerical evidence रिपोर्ट नहीं हुआ है। मुख्य कार्य की अनुमति देने से पहले input structure और प्रस्तावित approach की समीक्षा आवश्यक है।
````

**Objectives Open**

````text
[
  "Repository/input inspection और calibration/probe structure का विवरण",
  "Value/structure-based role inference का प्रस्ताव",
  "Forward, full gradients और HVP हेतु NumPy-only approach तथा validation plan",
  "Consequential assumptions और unresolved conventions की पहचान"
]
````

### Event 8 — Actor

**Answer**

````text
## निरीक्षण: केवल सार्वजनिक inputs
`/workspace` में depth-2 inventory में `data/` और `task.json` मिले; कोई उपलब्ध implementation/code file नहीं मिली। `reference/` नहीं पढ़ा। कोई समाधान, script या अंतिम artifact नहीं बनाया और operator fitting/derivative computation अभी नहीं किया।

**मुख्य metadata:** `input_shape=[2,13,48]`, `leading_shape=[2]`, `length=13`, `width=48`, `parts_a=6`, `parts_b=2`, `part_width=8`, `aux_width=16`, `table_width=4`, `span=5`, `epsilon=1e-5`, `repeat_factor=3`। ये संख्याएँ देखी गई हैं; इन fields की operational semantics अभी सत्यापित नहीं हैं।

**Shapes/dtypes:**
- `x`, `sensitivity`: `(2,13,48)`; `segment_ids`: `(2,13)`।
- `matrix_0`, `matrix_2`: `(48,48)`; `matrix_1`, `matrix_3`, `matrix_4`: `(48,16)`।
- `vector_0..2`: `(48,)`; `vector_3`, `vector_4`, `vector_6`: `(16,)`; `vector_5`: `(6,)`।
- दोनों tables: `(13,2)`। प्रत्येक supplied direction का shape अपने मूल array के समान है।
- सभी numerical continuous arrays `float64`; segment arrays `int64`।
- चार public probes: `probe_x` और sensitivities `(4,2,13,48)`, segments `(4,2,13)`, targets `(4,)`। Layouts में अलग boundary locations और कुछ skipped label numbers हैं; सभी देखे हुए base/public layouts contiguous segment runs हैं।

**Calibration archive:** schema version 1, तीन अतिरिक्त cases। Case axis के बाद `x/sensitivity=(2,13,48)` तथा चार probes/case हैं; कुल 12 अतिरिक्त scalar targets। तीनों metadata records के dimensions और partition fields समान हैं—यह archive अपने आप different-shape validation नहीं देता। Groups हैं `square_matrices (3,2,48,48)`, `kv_matrices (3,3,48,16)`, `width_vectors (3,3,48)`, `kv_vectors (3,3,16)`, `head_vectors (3,1,6)`, `tables (3,2,13,2)`; हर group के साथ corresponding `*_names` arrays हैं। Group labels shape bookkeeping का प्रमाण हैं, exact operator roles का नहीं।

## संभावित role fingerprints
Suffix को role मानने का आधार नहीं है; calibration में fingerprints का suffix बदलना प्रत्यक्ष दिखता है।
- Square matrices में scale separation: base standard deviations `0.0920` बनाम `0.1464`; calibration में लगभग `0.084–0.094` और `0.139–0.149`, और उनका suffix assignment बदलता है। ये अलग projection roles के candidates हैं, अभी query/output attribution सिद्ध नहीं।
- Rectangular matrices में एक बहुत छोटा scale (`std≈0.029–0.031`), शेष दो `≈0.137–0.154`। छोटा projection gate/auxiliary candidate है; बाकी दो के key/value roles केवल global std से विश्वसनीय नहीं अलग होते। इनके column/pair/block structure तथा correlations की आगे जाँच आवश्यक है।
- Width vectors में एक near-one (`mean≈0.98–1.01`), और दो near-zero मगर अलग scales (`std≈0.010–0.014`, `≈0.035–0.046`)। Gain तथा दो अलग biases संभावित roles हैं; normalization और bias placement probes से निर्धारित होंगे।
- Aux-width vectors में एक positive-offset (`mean≈0.55–0.57`), तथा दो near-zero scale groups (`std≈0.016–0.024`, `≈0.048–0.084`)। Gate offset और projection biases संभावित हैं।
- Six-element vector positive है: base range `0.0253–0.1513`; per-part relative-position slope इसका एक candidate है, तथ्य नहीं।
- Tables के शुरुआती rows स्पष्ट sine/cosine signature देते हैं: base `table_0[0]=[0,0]`, `table_1[0]=[1,1]`, अगले sine row `[sin(1),sin(.01)]`; pointwise squared sum का अधिकतम error `2.22e-16`। Calibration में sine/cosine suffix उलटता है। यह मजबूत structural fingerprint है; supplied table values को independent differentiable parameters की तरह उपयोग करना होगा, formula से regenerate नहीं करना।

## प्रस्तावित reconstruction और validation
1. NumPy/standard library में shape-group loader और value/structure diagnostics बनाऊँगा। Arrays से role assignment के candidates निकालकर सभी 16 public scalar responses के विरुद्ध conventions जाँचूँगा। Public fitting architecture पहचानने का साधन होगा, reusable API में suffix-map या disk/probe lookup का विकल्प नहीं। समान-scale projections के लिए टिकाऊ structural fingerprint मिलना आवश्यक होगा।
2. Candidate space में normalization (RMS/centered, affine placement), projection orientation, reduced-part expansion, gating/nonlinearity, residual/output placement, attention scaling, relative-distance term और mask semantics को evidence-driven ढंग से अलग करूँगा। सामान्य attention architecture को verified तथ्य नहीं मानूँगा। **Adjacent even/odd rotary pairing और हर leading batch element में non-resetting sequence index `t` brief की निश्चित शर्तें हैं**, इनका alternative search नहीं होगा।
3. Forward को arbitrary leading batch axes और supplied partition metadata के अनुसार लागू करूँगा। `return_cache=True` में intermediates और उस call का inferred role mapping रखूँगा; backward gradients को caller के original anonymous keys में लौटाएगा। HVP में `x` सहित सभी parameter directions शामिल होंगी। Role inference हर नए forward/HVP invocation के passed arrays पर होगा; numerical derivatives में inferred discrete assignment को locally fixed semantic choice माना जाएगा।
4. Backward के लिए NumPy में explicit reverse-mode primitives/chain rules; HVP के लिए उन्हीं forward और reverse equations का tangent propagation (forward-over-reverse) प्रस्तावित है। Broadcasting reductions, gather/scatter rotary gradients, masked softmax और head replication की adjoints स्पष्ट लिखूँगा। Finite differences केवल verification होंगे, production HVP नहीं।
5. Validation: सभी base/calibration scalar residuals; कुछ probes को hold-out रखकर candidate discrimination; same-shaped suffix permutations के साथ params और directions दोनों permute करके output invariance तथा gradient/HVP key-equivariance; per-parameter finite-difference scalar checks; joint-direction gradient dot product; analytic HVP बनाम centered finite differences of full gradients, कई step sizes पर; Hessian bilinear symmetry। Synthetic valid dimensions/partitions, extra leading axes, singleton segments, sequence ends तथा `span` boundary के आसपास metamorphic/derivative tests भी होंगे। Synthetic tests hidden ground-truth agreement का प्रमाण नहीं बताएँगे।

## Consequential assumptions और अनिश्चितताएँ
- **Partitioning:** observed equalities `48=6×8`, `16=2×8`, `6=2×3` grouped partitioning सुझाती हैं। Repeat-vs-tile head mapping, channel order तथा gate-sharing अभी अज्ञात हैं। Hidden shapes में accidental shape collisions संभव हों तो roles सिर्फ shape से नहीं चुनने चाहिए।
- **Masking:** causal diagonal inclusion, `span` का अर्थ और off-by-one, segment equality बनाम contiguous-run semantics, तथा fully masked rows का व्यवहार अभी स्थापित नहीं। देखे गए contiguous labels equality और run interpretation में भेद नहीं करते।
- **Position/relative position:** rotary pairing और non-reset indexing निश्चित हैं; tables का `(13,2)` और `table_width=4` partial rotary का संकेत है, पर कौन-से channels/प्रोजेक्शन rotate होते हैं, rotation sign, relative-distance sign/clipping तथा scale अभी जाँचना है।
- **Reusable API:** brief के तीन exact function signatures बनाए रखूँगा; forward की cache-return tuple और full gradient/HVP dictionaries के लिए स्वाभाविक convention क्रमशः `(output, cache)` और `x` सहित original-key dictionaries है। बिना cache वाले forward का return output होगा। Call-time role inference parameter values पर निर्भर होगा, filenames के suffix पर नहीं।
- **Identifiability:** 16 scalar probes सीमित evidence हैं; समान-scale matrices के role fingerprints अभी unresolved हैं। यदि कई convention candidates बराबर fit हों, उन्हें स्पष्ट limitation बताऊँगा, architecture assumptions से चुपचाप नहीं भरूँगा।

अनुमोदन मिलने पर ही implementation/main analysis और अंत में केवल निर्धारित तीन `.npy` outputs तथा `analysis.py` तैयार करूँगा।
````

**Stage**

````text
plan
````

**Evidence**

````text
Executed read-only inventory and two NumPy inspection passes over data/. Found 5 matrices, 7 vectors, 2 tables, matching directions, 4 base probes, and 3 calibration cases with 4 probes each. All three calibration meta_json records share the base dimensions. Observed square-matrix scale fingerprints and width/aux-vector fingerprints switch suffix assignments across cases; sine/cosine tables also swap suffixes. Table unit-circle residual is 2.22e-16. No reference content was read; no files were written; no reconstruction was executed.
````

**Assumptions**

````text
[
  "Forward return_cache=True will conventionally return (output, cache); gradient and HVP dictionaries will include x plus all original parameter keys.",
  "Fingerprint-based role assignment is a discrete semantic decoding step held locally fixed during differentiation.",
  "Grouped attention, gain/bias placement, gating and relative-position slopes are hypotheses to test, not established architecture."
]
````

**Uncertainties**

````text
[
  "The two similarly scaled rectangular projection matrices still need discriminative structural role fingerprints.",
  "Partition expansion order, normalization, gating, residual structure, relative-position formula and precise causal/window mask remain unverified.",
  "Visible calibration cases do not vary dimensions or metadata partitions, and visible contiguous segment layouts cannot alone distinguish equality masking from run-based masking."
]
````

### Event 9 — Simulator

**Message**

````text
प्रस्तावित तरीका स्वीकृत है; अब reconstruction, implementation और validation पूरा करें। Call-time structural/value fingerprints से roles चुनें; विशेषकर समान-scale rectangular matrices का भेद सभी calibration cases पर स्थापित करें, suffix या public-data lookup से नहीं। NumPy/standard library में analytic backward और tangent-over-reverse HVP तथा बताए गए API return conventions उचित हैं। Rotary tables को वास्तविक differentiable inputs रखें और सभी parameter directions के cross-effects HVP में शामिल करें। सभी 16 probes के residuals, full-dictionary gradient/HVP numerical checks और suffix-permutation equivariance के वास्तविक diagnostics रिपोर्ट करें। अलग shapes/partition तथा leading-axis tests उपयोगी हैं, लेकिन उन्हें target correctness का स्वतंत्र प्रमाण न कहें। Visible layouts से equality बनाम run masking अलग न हो पाए तो चुनी convention और शेष अनिश्चितता स्पष्ट रखें; अज्ञात source intent को तथ्य न बनाएँ। अंत में analysis.py तथा केवल results/output.npy, results/input_gradient.npy, results/input_hvp.npy numerical outputs बनाएँ। अंतिम उत्तर में किए गए काम, पहचाने गए operator/role नियम, diagnostics और शेष सीमाएँ दें; artifacts dictionary में चारों exact relative paths को keys रखें।
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
निरीक्षण रिपोर्ट में array shapes, 16 public scalar probes और तीन समान-shape calibration cases उपलब्ध हैं। Suffix बदलने वाले scale/vector/table fingerprints रिपोर्ट हुए हैं, जबकि rectangular role distinction और operator conventions अभी hypotheses हैं। प्रस्तावित probe-based identification, call-time decoding तथा analytic derivative validation brief के अनुरूप हैं; अभी execution evidence उपलब्ध नहीं है।
````

**Objectives Open**

````text
[
  "Public probes और calibration से operator conventions तथा transferable role fingerprints पहचानना",
  "तीनों exact reusable APIs में forward, सभी gradients और joint-direction HVP लागू करना",
  "Probe residuals, derivative diagnostics, permutation equivariance और shape robustness रिपोर्ट करना",
  "चार आवश्यक artifacts exact paths पर प्रस्तुत करना"
]
````

### Event 36 — Actor

**Answer**

````text
## कार्य पूरा हुआ
`analysis.py` में तीनों आवश्यक reusable APIs लागू और execute किए गए हैं। Implementation केवल NumPy/standard library उपयोग करता है। Forward के साथ `(output, cache)`, backward में `x` सहित पूरे original-key gradient dictionary, और HVP में उसी key-space का पूरा dictionary मिलता है। Role inference प्रत्येक forward/HVP call के supplied arrays से होता है; APIs कोई public-data/probe lookup नहीं करते। `reference/` नहीं पढ़ा गया।

### पहचाना गया operator
1. `z = x / sqrt(mean(x², channels) + epsilon) * gain`।
2. `z` से affine query, key, value और gate projections।
3. Query/key के पहले `table_width` channels पर adjacent even/odd rotary pairs। Supplied sine/cosine tables वास्तविक differentiable inputs हैं; token `t` हमेशा row `t` उपयोग करता है, segment boundaries पर reset नहीं।
4. Reduced key/value heads को contiguous groups में `repeat_factor` बार expand करना। Attention से **पहले** value को `sigmoid(gate)` से गुणा करना।
5. Score: `q·k / sqrt(part_width) − slope[head] * (t−s)`। चुना mask: समान segment label तथा `0 ≤ t−s < span`; diagonal शामिल है।
6. Masked softmax, weighted values, merged heads, output projection और output bias। **Residual addition नहीं है।**

### Call-time role fingerprints
- Gate projection सबसे छोटे scale वाला; output projection square projections में छोटे scale वाला; सामान्य grouped shapes में शेष width-wide projection query है।
- **Key/value distinction global standard deviation से नहीं किया गया।** Query columns को `(parts_b, repeat_factor, part_width)` groups में reshape करके repeat axis पर average करने पर key से प्रबल correlation मिलता है, value से नहीं:

| Array set | Key correlation | Value correlation |
|---|---:|---:|
| Base | 0.947661 | −0.016330 |
| Calibration 1 | 0.957078 | −0.002246 |
| Calibration 2 | 0.946886 | −0.016554 |
| Calibration 3 | 0.950006 | 0.085204 |

Calibration 1 में key `matrix_1` और value `matrix_3` निकले; अन्य तीन sets में इनके roles उलटे हैं। प्रारंभिक scale-only hypothesis इस case पर विफल हुई थी; final structural rule सभी cases पर सफल है।
- Gain near-one, gate bias positive-offset, और बाकी biases अपनी shape तथा relative scale से चुने जाते हैं। Per-head slope shape/positive-mean signature से; sine/cosine initial-row signatures से। कोई suffix map hard-code नहीं है।

### Analytic derivatives
Backward NumPy reverse-mode primitives से है। HVP उन्हीं forward/reverse equations में dual-number tangents propagate करता है—production finite differences नहीं। `x`, पाँच matrices, सात vectors और दोनों tables के simultaneous directions तथा उनके cross-effects शामिल हैं।

## वास्तविक validation
**सभी 16 probe residuals**, prediction minus supplied target:

| Array set | Probe 1 | Probe 2 | Probe 3 | Probe 4 |
|---|---:|---:|---:|---:|
| Base | 0 | 2.665e−15 | −1.776e−15 | −1.776e−15 |
| Calibration 1 | 0 | 0 | 0 | 4.441e−16 |
| Calibration 2 | 2.665e−15 | −2.665e−15 | −8.882e−16 | 0 |
| Calibration 3 | −2.665e−15 | 0 | −8.882e−16 | 4.441e−16 |

- **Full coordinate gradient check:** base case में सभी **8,410 scalar coordinates**, सभी 15 dictionary entries सहित, centered finite differences (`h=1e−5`) से जाँचे। अधिकतम absolute error **3.570e−10**; worst per-entry relative L2 error **6.652e−10**।
- **Full-dictionary HVP check:** supplied joint direction में सभी coordinates को perturbed full gradients के centered differences से जाँचा। `h=1e−5` पर अधिकतम absolute error **1.379e−10**, worst per-entry relative L2 error **9.420e−11**। Step sweep `1e−3, 1e−4, 1e−5, 1e−6` में अपेक्षित truncation/roundoff behavior मिला; पहले दो steps पर global max errors क्रमशः `6.073e−7`, `6.074e−9` थे।
- तीन calibration cases में भी हर dictionary block का gradient directional check और हर coordinate का HVP check हुआ। चारों sets में worst block-gradient scaled error **7.260e−9**, worst HVP absolute error **2.037e−10**।
- Hessian symmetry: `uᵀHv` और `vᵀHu` का अंतर **2.998e−15**।
- **48 suffix-permutation trials:** चारों sets पर 12-12 independent same-shaped permutations; params और directions दोनों permute किए। Forward invariance तथा full gradient/HVP key-equivariance errors सभी **ठीक 0**।
- Batch splitting, additional leading axis, injective segment relabeling और final-token perturbation का earlier outputs पर प्रभाव: अपेक्षित comparison errors **0**।
- तीन synthetic configurations: `(H,K,d,rotary_width,span)=(4,2,6,4,3)`, `(6,3,4,2,2)`, `(3,1,8,6,1)`; zero, two और three leading axes, तथा singleton sequence शामिल। Gradient directional errors ≤`2.572e−11`, full HVP errors ≤`1.765e−10`। ये implementation consistency tests हैं, target correctness का स्वतंत्र प्रमाण नहीं।

## निर्मित outputs
`results/` में केवल निर्धारित तीन numerical files हैं। तीनों `(2,13,48)`, `float64`, पूरी तरह finite हैं।

- Target scalar: **−5.836680389460258**
- Output L2 norm: `22.390865683421225`
- Input-gradient L2 norm: `11.733445979130012`
- Input-HVP L2 norm: `6.541953757064611`

## शेष सीमाएँ
- Visible contiguous segment layouts equality masking और contiguous-run masking में अंतर नहीं स्थापित करते। Implementation ने **label equality** चुनी है; repeated noncontiguous labels पर source intent का दावा नहीं है।
- Public calibration में dimensions/partition metadata समान हैं। अन्य grouped shapes के synthetic tests independent target evidence नहीं हैं। विशेषकर `parts_a == parts_b` होने पर projection shapes collide कर सकती हैं; इसके लिए code में value-based fallback है, लेकिन उस degenerate decoding को public target data स्वतंत्र रूप से validate नहीं करता।
- Role decoding discrete और locally constant है; fingerprints की decision boundaries के पार derivatives का दावा नहीं है। Supplied arrays तथा numerical perturbations में ऐसा crossing नहीं देखा गया।

Detailed reproducible checks `validate.py` और उनका log `diagnostics.txt` में उपलब्ध हैं; submission artifacts नीचे केवल चार native required paths हैं।
````

**Stage**

````text
result
````

**Evidence**

````text
Executed `analysis.py` successfully and generated all three required outputs. Executed `validate.py`: 16/16 scalar probes matched within 2.665e-15; exhaustive 8,410-coordinate gradient comparison had max absolute error 3.570e-10; full-dictionary base HVP comparison had max absolute error 1.379e-10 at step 1e-5; calibration HVP comparisons stayed below 2.037e-10; 48 same-shape suffix-permutation trials had exactly zero output/gradient/HVP equivariance errors; Hessian symmetry error 2.998e-15. Final file checks verified shape (2,13,48), dtype float64, all finite, and exactly three files in results/. `analysis.py` is a nonempty executed standalone implementation (12,738 bytes). No reference files were read.
````

**Assumptions**

````text
[
  "Segment masking uses label equality, not an independently inferred contiguous-run identity.",
  "The inferred discrete parameter-role map is held locally fixed when taking derivatives.",
  "Backward cache is paired with the same unmodified parameters and metadata used for its forward call."
]
````

**Uncertainties**

````text
[
  "Public layouts do not distinguish equality masking from run-based masking for noncontiguous repeated labels.",
  "Public target arrays do not validate equal-width query/key projection shape collisions; the implementation's value-based fallback for that degeneracy remains heuristic.",
  "Alternative-shape synthetic tests validate implementation and derivative consistency, not agreement with unseen target outputs."
]
````

### Event 37 — Simulator

**Message**

````text
कार्य पर्याप्त रूप से पूरा और रिपोर्ट किया गया है। प्रस्तुत चारों artifacts के exact relative-path keys submission contract से मेल खाते हैं। रिपोर्ट किए गए probe fits, पूरे gradient/HVP checks और suffix-permutation tests agreed approach का समर्थन करते हैं। Equality masking तथा equal-width projection fallback की सीमाएँ अंतिम उत्तर में स्पष्ट रखें; इन्हें स्वतंत्र रूप से सत्यापित source conventions न कहें। अतिरिक्त संशोधन आवश्यक नहीं है।
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
Agent ने NumPy/standard-library implementation और चारों आवश्यक artifacts रिपोर्ट किए हैं। 16 probes का अधिकतम residual 2.665e-15, 8,410-coordinate gradient check का अधिकतम absolute error 3.570e-10, base full-dictionary HVP error 1.379e-10 तथा 48 permutation trials में शून्य equivariance error रिपोर्ट हुआ। परिणाम arrays के shapes, dtype और finiteness भी रिपोर्ट किए गए हैं। ये agent द्वारा प्रस्तुत diagnostics हैं, स्वतंत्र निरीक्षण नहीं; शेष identifiability सीमाएँ स्पष्ट बताई गई हैं।
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
  "event_log": "runs/openai-astra-top10-trial-1-batch-2/episodes/asibench_computer_science.causal_attention-494796eeebb4/candidate_001/attempt-1/output/asibench_computer_science.causal_attention-494796eeebb4/controller/events.jsonl",
  "event_log_sha256": "5b4545857f02278c224f63ed4508e1232de9983839bc76e20bf40b530b0ed880",
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
