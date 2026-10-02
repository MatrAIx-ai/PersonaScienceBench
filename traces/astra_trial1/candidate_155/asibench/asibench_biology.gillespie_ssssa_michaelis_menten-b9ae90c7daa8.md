# candidate_155 · asibench · biology.gillespie_ssssa_michaelis_menten

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **scored**; normalized native score: **39.47/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
请先仅进行输入与仓库检查，暂不要实施完整求解或生成最终产物。请完整阅读 case_manifest.json、observation_spec.json、calibration_spec.json、candidate_reactions.json 和 mechanism_spec.json，并检查其余 CSV、NPY 输入及现有代码和运行环境。请报告：一、实际输入结构、状态空间与规模、各项输出的精确模式和覆盖要求；二、自适应动力学的守恒量、采样要求、求解器策略区间、阶段进入与重启规则、交接约定及验证规则；三、独立校准问题的参数化与目标，以及机制发现的候选反应、参数边界、support_limit、时间插值、部分观测、公开 BIC 和干预查询约定；四、拟采用的精确基线、自适应求解、CME 数值传播、校准与稀疏支持搜索方案，以及可复现性、数值误差和运行成本的检查计划。请明确区分规范明定事项与您的方法建议，列出会实质影响正确性的假设、歧义或环境限制。特别说明如何确保 selected_mechanism.csv 中的同一模型生成全部拟合及预测表，并正确处理所有单候选激活面板。最后核对提交所需的 19 个文件与规范是否一致；最终 artifacts 字典须使用原生相对路径，不增加未声明交付物。此次只提交检查结果和拟议方案，待确认后再开展主体工作。
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
当前仅有任务说明、输入路径和提交契约，尚无实际文件检查或运行证据；应先确认规范与可行方案。
````

**Objectives Open**

````text
[
  "完整检查输入、仓库和环境",
  "确认全部产物模式及科学与数值约束",
  "审阅拟议实现、优化与验证方案",
  "识别影响正确性的假设和不确定性"
]
````

### Event 12 — Actor

**Answer**

````text
## 结论与工作边界
已完整阅读五个 JSON（case_manifest、observation_spec、calibration_spec、candidate_reactions、mechanism_spec），并读取 task.json、全部 CSV 和两个 NPY。此次仅做结构、覆盖、守恒与环境检查，**没有进行参数拟合、支持搜索、动力学求解，也没有生成 analysis.py 或任何最终交付文件**。以下将“规范明定/实际检查”与“拟议方法/解释”分开；等待您批准后开展主体工作。

## 一、实际输入、规模与环境

### 1. 仓库与环境事实
- /workspace 目前只有 task.json 与 data/；没有已有求解代码、测试代码或参考输出。
- data/ 恰有公开列出的 11 个输入文件。
- Python 3.12.11、NumPy 2.4.4、SciPy 1.16.0，满足最低要求。numba、pandas、threadpoolctl 可被发现，但尚未测试其运行兼容性；拟不将这些可选包作为必需依赖。
- 系统报告 64 个逻辑 CPU，MemTotal 约 504 GiB；这不是作业实际资源配额承诺。本次未获得有效的 cgroup CPU/内存额度，未做速度基准测试。

### 2. 公共状态空间
四个 bundle case、校准与机制问题均使用 E+ES=4、S+ES+P=6。枚举 P=0,…,6，再枚举 ES=0,…,min(4,6-P)，重建 E=4-ES、S=6-P-ES，恰有 **25 个离散状态**。机制候选全部通过两个守恒量的化学计量检查；但机制库允许 P 下降，不能把 bundle 的单向周转阶段结构移用于机制发现。

Manifest 的物种名和反应 ID 是不透明别名，必须按反应拓扑识别 E、S、ES、P 及结合/解离/催化通道。由拓扑读得四个 case 的 (c1,c_minus1,kcat) 分别为：
- case 0：(0.8996,14.5412,0.0495)
- case 1：(0.4283,2.03,0.0513)
- case 2：(0.1197,5.1934,0.3292)
- case 3：(0.2135,0.457,0.2325)
均从 (4,6,0,0) 开始，时间范围 [0,24]。

### 3. 数组与表的实际规模
- sample_times.npy：float64，(21,)，从 0 到 24 的非均匀时点；不能替换成等距网格。
- snapshot_times.npy：float64，(4,)，[3.44800397,12.09167183,17.58970747,22.08]，与 manifest 完全一致；不是 sample_times 的子集。
- calibration_histograms.csv：400 行=2 case×8 时点×25 状态；ID 唯一；每 cohort 768 个样本，总计 12288；147 行计数为零。时点为 [0.25,0.7,1.5,2.8,4.5,7,11,18]。
- calibration_queries.csv：400 行=2×8×25；时点为 [0.4,1,2.2,3.5,5.5,9,14,22]。
- mechanism_histograms.csv：504 行=3 condition×8 时点×21 类别；每 cohort 1536，总计 **36864**；285 行计数为零。时点 [0.3,0.8,1.8,3.5,6.5,10,15,21]。每组完整包含 P=0,…,6 与 bound_class=0,1,2 的笛卡尔积，包括结构不可能类别。
- mechanism_queries.csv：**6125 行**，全部 ID 唯一；temporal 525 行，initial_condition 350 行，intervention 5250 行。35 个 condition 各 7 时点×25 状态。已检查所有校准与机制全状态组确实覆盖同一套 25 状态。
- temporal 时点：[0.55,1.25,2.7,5,12.5,18.5,22]；其余查询时点：[0.45,1.5,4.2,8.5,14,19.5,22]。

## 二、19 项输出的精确模式与覆盖
已用程序核对：observation_spec.required_outputs 与 task.json.submission.required_artifacts **顺序及内容完全一致，共 19 项**。下面列出的每个文件均必须存在；CSV 按规范列序写出，不增加列。

1. **analysis.py**：自包含程序，只读取公开输入，生成其余 18 个文件。
2–3. **exact_bundle_summary.csv / adaptive_bundle_summary.csv**：各 84 行，4 case×21 sample_times。列：`row_id,case_index,time,mean_S,mean_ES,mean_P,var_ES,var_P`。
4–5. **exact_bundle_turnover.csv / adaptive_bundle_turnover.csv**：各 8 行，4 case×turnover_targets=[1,2]。列：`row_id,case_index,turnover_index,completion_fraction,mean_fpt,var_fpt`。
6. **stage_memory_probe.csv**：24 行，逐一沿用规范 probe_id 和位置。列：`probe_id,case_index,stage_slow_total,lag_time,entry_es_a,entry_es_b,tv_distance_between_entries,mean_es_gap_between_entries,var_es_gap_between_entries,survival_prob_entry_a,survival_prob_entry_b`。
7. **stage_residual_time_probe.csv**：同样 24 个 probe。列：`probe_id,case_index,stage_slow_total,lag_time,entry_es_a,entry_es_b,mean_remaining_time_entry_a,mean_remaining_time_entry_b,var_remaining_time_entry_a,var_remaining_time_entry_b`。
8. **adaptive_stage_handoff.csv**：24 行，沿用 handoff_row_id 和 memory_probe_id。列：`handoff_row_id,case_index,stage_slow_total,memory_probe_id,p_entry_es_a,p_entry_es_b,mean_entry_es,var_entry_es,mean_pre_event_es,var_pre_event_es`。
9. **cme_transient_distribution.csv**：2100 行=4×21×25。列：`cme_row_id,case_index,time_index,time,E,S,ES,P,probability`。规范排序：case 升序、time_index 升序、P 升序、ES 升序；必须是 manifest 全三反应网络的精确瞬态 CME 分布。
10. **stage_exit_kernel.csv**：320 行；每 case 的 T=6,…,1，每 entry_es=0,…,min(4,T)，每 pre_event_es=1,…,min(4,T)。列：`kernel_row_id,case_index,stage_slow_total,entry_es,pre_event_es,exit_probability,conditional_mean_time,conditional_var_time`。排序 case 升、T 降、entry 升、pre_event 升；吸收概率≤1e-12 时两个条件时间矩写零。
11. **calibrated_rates.csv**：2 行。列：`calibration_case_id,c1_before,c_minus1_before,kcat_before,c1_after,c_minus1_after,kcat_after,negative_log_likelihood`。
12. **calibration_predictions.csv**：400 行，逐行覆盖输入查询。列：`calibration_query_id,calibration_case_id,time_index,time,E,S,ES,P,probability`。
13. **selected_mechanism.csv**：每个所选候选 4 行，共 4s 行，s≤6；不写未选候选。列：`candidate_id,knot_id,knot_time,rate`。每个所选 candidate 必须包含四个结点且 rate 在其候选边界内。
14. **mechanism_public_fit.csv**：504 行，包括零计数/不可能类别。列：`mechanism_hist_row_id,probability`。
15. **mechanism_predictions.csv**：6125 行，包含全部三类查询。列：`mechanism_query_id,probability`。
16. **bundle_snapshot_samples.npz**：仅六个规范键 `exact_s_samples,exact_es_samples,exact_p_samples,adaptive_s_samples,adaptive_es_samples,adaptive_p_samples`，每个形状 (16,96)。拟用整数数组、case-major/snapshot-time-minor 排列。
17. **stage_solver_policy.csv**：24 行，规范给定 ID 与位置。列：`policy_row_id,case_index,stage_slow_total,memory_probe_id,stage_solver_code`。
18. **conservation_report.json**。
19. **runtime_report.json**。

重要缺口：给出的规范**没有规定最后两个 JSON 的内部键/精确模式**，也没有明确 summary/turnover 的 row_id 起点、NPZ 的展平顺序、汇总是否必须来自同一批 96 条轨迹、FPT 截尾处理等细节。不能声称这些已有精确规定。拟采用第六节的明确约定并在程序/报告内记录。CME/kernel 规范给出排序但未写 ID 起点；拟一致使用从 0 开始的连续 ID。

最终 artifacts 字典将只含以上 19 个**原生相对路径键**，值为对应原生相对路径；不加 `analysis` 别名，不增加 README、日志、模型缓存或独立诊断文件。本轮不提交 artifacts，因为尚未生成交付物。

## 三、自适应动力学：规定、数学对象及方案

### 1. 规范明定
- 非负整数状态，严格满足 E+ES=4、S+ES+P=6；n_replicates=96、21 个汇总时点、4 个快照时点。
- 每 case 六个阶段 T=S+ES=6,…,1，P=6-T；终点 T=0 为吸收状态。
- 24 个 probe 的 lag、entry_es_a、entry_es_b 直接读规范，不从 case 次序推断，也不重算替代 lag。memory_probe_factor=0.01 存在，但实际 probe 行已经给定 lag。
- 策略严格为：TV>0.55 用 code 0；0.12<TV≤0.55 用 code 2；TV≤0.12 用 code 1。先算 submitted dynamics 的 TV，再决策，不能按 case 标签硬编码。
- code 0：真实跃迁后 ES 入场，全系统逐事件运行至下一催化事件。
- code 2：真实跃迁后 ES 入场，以入场条件 killed fast chain 传播到催化吸收。
- code 1：首阶段 ES=0；后续每一阶段从**上一阶段**的平稳催化退出分布抽 ES_pre，再设 ES_after=ES_pre−1。该退出分布为 cπ_previous(c)/Σj jπ_previous(j)，c>0。禁止用当前阶段平稳占据分布替代。
- handoff 不是 horizon=24 内已完成样本的经验统计，而是指定政策下**完整周转路径**上的确定性入场/退出分布摘要。p_entry_es_a/b 是给定两个状态的概率，并非二点混合权重，二者无需和为 1。

### 2. 拟议数学实现
固定 T，用 c=ES，m=min(4,T)，结合率 b_c=c1(4−c)(T−c)，解离率 d_c=c_minus1 c，催化杀死率 h_c=kcat c。采用行分布约定：fast generator F 包括结合/解离，K=F−diag(h)。
- survival：u=e_entry exp(K lag)，s=u·1。
- 拟将记忆统计定义为存活条件分布 u/s 的 TV、均值差和方差差；survival 另列，不用未归一化分布混合退出质量。
- 剩余时间：R=(−K)^−1，t=R1，二阶矩=2R²1；以 lag 时存活条件分布加权，方差由二阶矩减均值平方。
- exit kernel：B=R diag(h)，时间一阶未归一化矩 R²diag(h)，二阶未归一化矩 2R³diag(h)，再逐出口除 B。实现用线性方程求解，不显式做不稳定逆矩阵。
- fast stationary π 用 birth–death 详细平衡递推后归一化；stationary catalytic-exit law 仅用于规范要求的 code 1 重启。
- handoff：首入场 δ0；目标阶段 code 0/2 时，将前一阶段实际退出分布按 c→c−1 推送；目标阶段 code 1 时，用前一阶段 stationary catalytic-exit law 推送。再通过当前阶段 kernel 得到退出分布，计算全部确定性矩，不按有限时间截尾。

### 3. 精确与自适应随机模拟方案
- 精确基线：真正 Gillespie direct SSA，三条离散通道，按 sample/snapshot 时点合并采样网格报告右连续状态，记录前两次催化事件 FPT。
- 自适应 code 0 同样逐事件；code 2 拟用小维 killed-chain 半群和 phase-type 吸收采样，联合保证退出时间与退出 ES 的相关性。跨观察时刻先按存活概率决定是否有吸收；存活则抽条件 ES，吸收则用累计概率反演时间并按该时刻催化通量抽出口。不会把退出时间和出口独立抽样。
- code 1 拟使用相同 killed-chain 阶段传播，但施加规范的 stationary-exit 重启，保留首阶段 ES=0。这是对规范未明写的 code 1 阶段内时钟所作的解释，不擅自改为当前 stationary occupancy 或额外的指数平均 hazard 近似。
- 随机输出每 case、每 solver 96 条轨迹，汇总与快照来自同一组路径；矩用总体方差 ddof=0。另用确定性 CME 校验抽样误差，而不是把随机路径输出偷换成概率表。

## 四、独立校准与机制发现

### 1. 校准的规定与拟议求解
两个 calibration_case 独立于 manifest 四个 case；每个 case 六参数，共享于所有时点；t=3.5 切换一次，全状态 independent-cohort multinomial likelihood。初态 (4,6,0,0)。前后 c1∈[0.04,1.2]、c_minus1∈[0.2,18]、kcat∈[0.02,0.5]。
拟在 log 参数边界内用多起点 L-BFGS-B；25 状态生成元在切换前后分别矩阵指数传播，分布在 3.5 连续，绝不在切换时重新初始化。用灵敏度或矩阵指数 Frechet 导数减少有限差分成本，并以有限差分抽查梯度。报告 NLL 拟为 −Σ count·log(max(p,1e−300))，省略与模型无关的 multinomial 常数；预测只由最终六参数再传播。

### 2. 机制库完整内容与边界
规范质量作用倾向是 k×∏species binomial(n,ν)，不能用未经阶乘校正的 n^ν；催化旁观物即使净化学计量抵消，仍保留在 reactants 中计算 propensity。
库含 30 个候选：一分子 4 个、二分子 18 个、三分子 8 个。本实例同分子数候选边界相同：一分子 [0.002,0.8]，二分子 [0.0005,0.35]，三分子 [0.00005,0.08]；实现仍逐候选读 bounds，不把这一规律硬编码。

以下每行 ID 后为规范反应；系数 2 是化学计量数：
```
rx_4530bd0fed78bd3d  ES+E -> 2E+P
rx_ed2cb08fb54f4bb4  E+P+ES -> 2ES
rx_8934291f2e85fc0a  E+P+S -> ES+S
rx_5ef968d97ce11fee  E+S -> E+P
rx_d5c41d44658e48ec  ES+P -> ES+S
rx_5856629a30e33502  ES -> E+P
rx_e89c8cfb84cb13e9  2P -> P+S
rx_84981f8dfb31fc77  ES+S -> ES+P
rx_423cb222804180a8  ES+P -> E+S+P
rx_7c8ce938265f0640  E+S+ES -> 2ES
rx_46ebbca2c1033c3a  2S -> S+P
rx_3eb6ad6599eb3bec  S+P -> 2S
rx_a5c4d1c9c156bb39  ES -> E+S
rx_342f6ef46accbc93  E+2S -> ES+S
rx_7be80fa7a39bc32c  2E+P -> E+ES
rx_10449ed42c323bf6  ES+E -> 2E+S
rx_aa1f54f3901f13f2  ES+P -> E+2P
rx_c93415ea34167a04  2E+S -> E+ES
rx_7043d9e61b14a8c6  E+P -> ES
rx_0c4cd15614e09d60  2ES -> E+S+ES
rx_1f54b855a3e2f17d  E+S+P -> ES+P
rx_12e3defc650f63fc  2ES -> E+ES+P
rx_8354892d05e14f86  E+S -> ES
rx_9dc2512c08a09736  ES+S -> E+2S
rx_82ba88bad17d4fad  S+P -> 2P
rx_4fdd4949e7e7d443  ES+S -> E+S+P
rx_d6127ccfae544747  E+P -> E+S
rx_957bdb1587e61f37  S -> P
rx_db9d192affd6d22e  E+2P -> ES+P
rx_5ec4a10950bb4b1e  P -> S
```

### 3. 参数、部分观测与目标：规范明定
- support_limit=6，support 为 selected_mechanism.csv 出现的不同 candidate_id 集合；未选候选的速率恒为零，不能以低于下界的正速率伪装删除。
- 结点 [0,2,8,22]；每个被选候选各自 log(rate) 分段线性，区间外常数。拟用 knot_id=0,1,2,3。
- 训练条件 train_a=(4,6,0,0)、train_b=(3,4,1,1)、train_c=(2,2,2,2)，顺序为 (E,S,ES,P)。
- 观测映射为 (P,bound_class)，class 0:ES=0，1:ES=1，2:ES≥2。必须先将 full-state CME 概率按类别求和再求 likelihood，不能把 ES≥2 当单一 ES=2 状态。
- 公共目标 BIC=2NLL+(4s)log(36864)。snapshot count 是 36864，不是 504 行数；不对各时点另拟参数。
- unseen initial conditions：(4,2,0,4)、(1,2,3,1)。
- 30 个 singleton panel 的 multiplier 字典确实与 30 个候选形成一一对应，每个显式因子均为 256；这些面板本身不提供 support 信息。

### 4. 拟议 CME 与稀疏支持搜索
- 预构建 30 个 25×25 单位生成元及 21×25 观测映射；Q(t)=Σselected k_r(t)Q_r。采用同一 orientation 全程一致。
- 时间变化传播不把 Q(t) 冻结为整段常数；按结点分段积分，常规先试 DOP853，256 倍激活可能刚性时用带解析 Jacobian 的 Radau/BDF。优化阶段可适度放宽容差，最终重新高精度传播并做容差收敛比较。
- 训练三个初态可批量传播；最多 24 个 log-rate 参数，优先前向灵敏度梯度，并检查有限差分一致性。
- 支持搜索不是穷举所有六候选组合。拟采用确定种子的多起点与小型 beam：从所有候选的公平初筛/可达性检查开始，交替 add、drop、swap，每个新支持做边界内联合四结点拟合，缓存支持与 warm start；对优胜及近优支持增加起点、检查单反应替换，再以精确复算的公开 BIC 选择。
- 筛选不会基于 ID、候选排列、singleton 面板是否存在，或套用 manifest 的三反应真模型；部分观测下可能有支持混淆，单纯训练拟合好不保证激活外推好。不承诺找到全局 BIC 最优，也不声称能在无干预标签情况下直接优化隐藏的 worst-panel Hellinger。

### 5. 确保“同一模型生成全部表”与全部单激活面板
最终选定支持与结点率后，先写 selected_mechanism.csv，再从该文件**重新读入**重建 Q(t)，只通过这一公共重建路径生成 504 行 fit 和 6125 行 predictions；不复用优化器里独立估计的概率，不按 query family 再拟合。
对每个 condition：从公开初态的 δ 分布开始，先插值所选候选 rate，再乘该 condition 的显式 multiplier；未列出的候选乘 1。若被激活候选不在 selected support，它仍然是零，不能临时加入，且该 panel 应等于 train_a 的未扰动模型在相同时点的分布。
所有 30 panel 各写齐 7×25=175 行；允许内部缓存至多 6 个真正改变 Q 的面板及共享基线，但不能因此省略任何输出行。最终逐 panel 检查概率和、非负性、查询 ID、与重建模型一致性；强激活率不受原始 knot-rate 上界二次裁剪，原始边界约束的是未扰动结点率。
规范的 robust intervention error 是 30 个 panel 各自跨时间的 full-state Hellinger 均值，再取最大，不是所有 query 混合平均；没有真实查询概率，当前无法报告该准确率。

## 五、可复现、数值误差与成本计划（方法建议）
1. 固定 master SeedSequence，按模块/case/solver 派生 RNG；排序和 tie-break 固定；不以 wall-clock 截止决定最终支持，避免同一输入运行结果漂移。BLAS 线程数受控。
2. 输入验证：表头、唯一 ID、状态/类别全覆盖、总数、bounds、结点、初态、单激活字典；构建 Q 时验证非负 off-diagonal、行和为零、反应映射合法、两守恒量无漂移。
3. deterministic 结果验证：每组概率归一，kernel 各 entry 行和为 1，生存概率∈[0,1]，方差非负；均值/残余时间与线性方程及数值积分交叉检查。对概率的舍入负值只允许在已验证容差内清零，不用大幅裁剪/归一掩盖错误。
4. 时变最终积分拟起步 rtol≈1e-9、atol≈1e-12，再收紧一档，比较最大概率差、NLL/BIC 差与所有强激活 panel；误差阈值由实际收敛诊断确认。极小概率的 1e-300 floor 仅用于 log-likelihood，不给结构不可能类别强塞质量。
5. SSA 与 CME 的均值/方差及快照分布按 Monte Carlo 标准误校验，不把 96 样本偏差误判为确定性算法错误；随机路径所有事件及重启后均检查整数非负与守恒。
6. 优化检查：多起点一致性、梯度抽查、边界活跃情况、近优支持/BIC 差、重拟与删/换候选改善。最优点再用严格容差重算，报告实际搜索范围，不声称穷举证明。
7. 成本：CME 仅 25 维，阶段矩阵至多 5 维；基本模拟与线性代数预期成本较低，机制离散搜索会占主导。先测单次 likelihood/梯度与短拟合成本，再固定可复现的搜索轮次、beam 大小、起点数和迭代上限；不在当前未测试情况下承诺总分钟数。
8. conservation_report 拟记录 checked_state_count、样本形状、最大守恒偏差、负值/非整数数量、概率质量误差等；runtime_report 拟记录种子、版本、线程、各模块耗时、优化次数、BIC/NLL、容差/收敛诊断与采用的歧义约定。全部诊断装入这两个已声明 JSON，不另加交付物。
9. 最后从空输出状态完整运行 analysis.py，核对 19 文件集合、列序/行数/ID、NPZ 键/形状及 selected-model 重建一致性；再复跑检查科学数值可复现。runtime 的实测耗时自然不要求字节相同。

## 六、会实质影响正确性的解释、假设与限制
以下是实际规范缺省，不作为已明定事实：
- **code 1 的阶段内等待时间律**：规范给定重启法但未明确要求均值 hazard 指数时钟。拟采用 killed-chain 传播+规定重启，避免额外未经授权近似；若研究者掌握更细的公开约定，应在实施前调整。
- **memory/residual probe 的精确定义**：规范列名与 killed-chain 契约支持“lag 时条件于未催化的分布”解释，但未写完整公式。拟按第三节实现；mean/var gap 拟取绝对差，TV 用 1/2 L1。绝对差与有符号差是需记录的解释。
- **turnover 汇总**：规范未明说 mean_fpt/var_fpt 是否只对 horizon 内完成者。拟 completion_fraction=24 前完成比例，FPT 矩对这些完成者计算（零完成者写 0 并记录）；不把未完成者当作 24 的 FPT。此约定可在批准时直接修改，不需另开探索轮。
- **样本方差与行序**：拟总体方差 ddof=0、96 条路径、case-major 的连续 row_id/NPZ 排列；这些细节不能伪称是文件中已有逐项规定。
- **NLL 常数**：拟报告通常用于拟合的 −Σn log p，不含 multinomial 组合常数。该常数不影响同一数据集上的最优率、支持排序或 BIC 差，但会改变绝对 NLL。
- **JSON 内部模式**：公开未给出；拟用透明诊断键，不凭空猜测隐藏 evaluator 键名。没有本地 evaluator，因此当前只能保证公开约束及自建校验。
- **可识别性/成本**：partial observation、30 候选与强激活外推使 support 错选的风险高；无隐藏真值、无干预计数，不能承诺 robust Hellinger 最优。资源配额与长运行稳定性尚未实测。

请批准上述总体方案及显式约定，或直接指定需改变的约定；在批准前我不会实施主体求解或生成最终文件。
````

**Stage**

````text
plan
````

**Evidence**

````text
检查命令实际读取了全部五份JSON且工具输出未截断；CSV/NPY用Python解析而非仅看文件名。已验证：状态数25；calibration_histograms/calibration_queries各400行且各组完整25态；mechanism_histograms 504行、24个cohort、总样本36864、每组21类别；mechanism_queries 6125行=525 temporal+350 initial_condition+5250 intervention，各组完整25态；30个候选均守恒，分子数分布4/18/8；30个singleton与候选ID一一对应且因子均256；两处required_artifacts列表完全相同、长度19。Python 3.12.11、NumPy 2.4.4、SciPy 1.16.0。工作目录结束时仍仅task.json与data，无新产物。
````

**Assumptions**

````text
[
  "拟将memory probe解释为killed-chain在lag时存活条件分布，gap采用绝对差；残余时间亦条件于存活。",
  "拟将code1实现为规定的stationary catalytic-exit重启加killed-chain阶段传播，而不额外假定指数平均hazard时钟。",
  "拟以96条同组轨迹生成各solver汇总和快照，方差ddof=0；FPT矩限于24内完成者，未完成不伪造FPT。",
  "拟用从0开始连续输出ID与case-major快照行序；NLL省略模型无关multinomial常数。",
  "最终只使用19个原生相对路径作为artifacts键和值，不添加未声明交付物。"
]
````

**Uncertainties**

````text
[
  "规范未明确code1阶段内时钟、probe差值符号、FPT截尾矩、summary/NPZ部分排列细节，计划中已显式给出解释。",
  "conservation_report.json与runtime_report.json没有公开内部键模式；无本地评分器。",
  "时变机制支持搜索不能保证全局BIC最优；公开干预查询没有标签，无法直接验证robust Hellinger准确率。",
  "实际CPU/内存配额和优化运行成本尚未实测；可选包仅检查可发现性，未验证兼容性。"
]
````

### Event 13 — Simulator

**Message**

````text
批准开展主体实现、执行与验证。您提出的精确 SSA、阶段 killed-chain 传播、联合吸收时间与出口采样、独立分段校准，以及公开 BIC 驱动的稀疏机制搜索方案可以采用。请以公开规范为最高依据；对您报告未明定的事项，暂采用所列约定：存活条件 memory/residual probe、绝对矩差、code 1 的指定 stationary catalytic-exit 重启加 killed-chain 阶段传播、同组 96 条轨迹、ddof=0、期限内完成者的 FPT 矩、零起点 ID 与 case-major 快照顺序。这是明确的方法选择，并非对未知源意图的确认；请在已声明 JSON 中记录。

实施时特别注意：code 1 重启后须由当前 T 和新 ES 重建其余物种，保证每次重启也满足离散守恒；code 2 跨采样时刻的存活条件更新必须保持同一条轨迹的联合分布。未选候选的激活面板只有在初态及其余条件相同的情况下才能复用基线分布，缓存键应包括完整条件，不能仅凭候选未入选判定。

按拟议计划先做短成本测量，再固定可复现的搜索预算；不要根据运行时长改变最终支持。报告实际搜索范围、最优及近优支持的 BIC 差、多起点和删除/替换检查、参数边界与优化收敛情况，不作全局最优或隐藏干预准确率承诺。最终表必须从序列化后的 selected_mechanism.csv 重建同一模型生成，覆盖全部查询。

完成后请提交完整候选：answer 描述已完成工作与实际证据，artifacts 以全部 19 个精确原生相对路径为键。请同时报告实际行数与 ID 覆盖、NPZ 形状、策略代码及阈值一致性、守恒与概率误差、积分容差收紧比较、梯度抽查、SSA/CME 抽样误差诊断、模型重建一致性、运行成本和干净运行及复跑结果。所有持久诊断仅放入已声明文件，不增加交付物。若执行中遇到实质阻碍或发现规范与上述解释冲突，请如实指出并提供已完成证据。
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
代理报告已完整检查输入和规范，列出了19项交付模式、25态状态空间、部分观测与全部30个激活面板的处理，并明确区分规范与解释。所提数学传播、联合采样和模型一致性路线符合项目目标；当前尚无执行产物或数值验证结果，适宜授权主体工作。
````

**Objectives Open**

````text
[
  "实现并执行自包含 analysis.py，生成全部19项交付物",
  "验证随机动力学、阶段策略与交接、离散守恒及数值精度",
  "完成独立校准与受限稀疏机制搜索，并以同一模型生成全部拟合和预测",
  "报告真实执行诊断、可复现性及最终 artifacts"
]
````

### Event 42 — Actor

**Answer**

````text
## 完成情况
已实现并实际执行自包含的 `analysis.py`，生成全部 **19 个规定文件**。最终交付目录没有新增未声明文件；所有持久诊断均在 `conservation_report.json` 和 `runtime_report.json` 中。

实施遵循批准的解释：存活条件 memory/residual probe、绝对矩差、code 1 的指定 stationary catalytic-exit 重启加 killed-chain 阶段传播、每 case/solver 同组 96 条轨迹、ddof=0、期限内完成者 FPT 矩、零起点 ID 与 case-major 快照。上述约定已写入 runtime_report，而非宣称为未明定的规范原意。

## 1. 动力学与校准结果
- 实现了真正逐事件 Gillespie SSA；自适应 code 0 同样逐事件，code 1/2 使用 killed-chain 联合时间/出口采样，并在观察时刻按存活条件更新同一条轨迹。
- code 1 每次重启后由当前 T 和新 ES 重建 E、S、P；没有用当前阶段 stationary occupancy 替代规定的上一阶段 catalytic-exit law。
- 完成 25 状态全 CME、24 个 memory/residual probe、24 个确定性完整周转 handoff、320 行退出核。

**策略与阈值一致性：**

| code | 阶段数 | 实际 TV 范围 |
|---|---:|---:|
| 0 | 8 | 0.56450591–0.94680876 |
| 1 | 6 | 9.2195×10⁻⁹–0.00502253 |
| 2 | 10 | 0.12262283–0.51699106 |

全部严格满足 >0.55→0、(0.12,0.55]→2、≤0.12→1。code 1 实际发生 104 次 stationary 重启。

**校准：**两个独立六参数模型均使用 t=3.5 连续分布交接，而非重新初始化。最佳 NLL 分别为 **12228.5576178044** 和 **13500.4472863923**，均报告优化收敛；每 case 进行了四起点拟合。第二个 case 有两个起点停在稍高目标值，已如实记录，不声称各起点均到同一解。

## 2. 稀疏机制与同模型预测
最终选择 **5 个反应、20 个结点参数**，满足 support_limit=6：

| candidate_id | 反应 |
|---|---|
| rx_46ebbca2c1033c3a | 2S → S+P |
| rx_0c4cd15614e09d60 | 2ES → E+S+ES |
| rx_1f54b855a3e2f17d | E+S+P → ES+P |
| rx_12e3defc650f63fc | 2ES → E+ES+P |
| rx_4fdd4949e7e7d443 | ES+S → E+S+P |

每个反应均写齐 [0,2,8,22] 四个 knot；全部速率在逐候选公开边界内，没有参数落在边界判定容差内。propensity 使用 binomial 约定，旁观反应物仍计入 propensity。

- 最终公开 NLL：**50783.5472175291**。
- 最终公开 BIC：**101777.3942499393**，参数罚项使用 20×log(36864)。
- 搜索中检查的最近替代支持为上述五反应加 `rx_7c8ce938265f0640`，BIC=101788.7075355748，**ΔBIC=11.31328564**。
- 最接近的四反应删除模型 ΔBIC=107.96709280；所有五个单反应删除均已重新拟合检查。

**模型一致性：**程序先写出 `selected_mechanism.csv`，再读回该文件重建时变生成元，生成全部 fit/prediction 表；没有独立拟合概率表。序列化前后 log-rate 最大差为 0；从提交模型重新传播所得 public NLL 与搜索阶段严格传播值相差 1.09×10⁻¹⁰。

**干预：**完整覆盖全部 30 个 singleton panels，每个 175 行。先进行 log-rate 插值，再应用显式 256 倍 multiplier，不裁剪受干预速率到原始 knot bounds。未选候选仍为零。缓存键包含初态、支持及速率、有效 multiplier、完整时点集合；不是仅按“候选未选中”复用基线。全部查询共 35 个 condition，实际有 11 个不同传播缓存条目。

## 3. 实际输出覆盖
CSV 表头均按规范逐列校验；显式 ID 唯一且完整，与所有输入查询 ID 集合一致。

| 文件或文件组 | 实际行数/形状 |
|---|---:|
| exact/adaptive_bundle_summary.csv | 各 84 行 |
| exact/adaptive_bundle_turnover.csv | 各 8 行 |
| stage_memory_probe.csv | 24 行 |
| stage_residual_time_probe.csv | 24 行 |
| adaptive_stage_handoff.csv | 24 行 |
| stage_solver_policy.csv | 24 行 |
| cme_transient_distribution.csv | 2100 行 |
| stage_exit_kernel.csv | 320 行 |
| calibrated_rates.csv | 2 行 |
| calibration_predictions.csv | 400 行 |
| selected_mechanism.csv | 20 行 |
| mechanism_public_fit.csv | 504 行 |
| mechanism_predictions.csv | 6125 行 |
| bundle_snapshot_samples.npz | 规范六个键，各 (16,96)，整数 |

机制查询覆盖为 temporal **525**、unseen-initial-condition **350**、singleton intervention **5250** 行；没有省略零概率行、不可能观测类别或未改变模型的激活面板。加上 analysis.py 及两个 JSON，恰为所需 19 项。

## 4. 数值与随机校验实测
- 快照非负整数违规：**0**；两守恒量最大误差：**0**；检查的催化事件/重启违规：**0**。
- 全 CME 最大概率质量误差：**1.0725×10⁻¹³**。
- stage exit kernel 最大行和误差：**1.0125×10⁻¹³**。
- killed-chain 特征分解半群与直接 expm 最大差：**4.44×10⁻¹⁵**。
- residual 线性方程最大残差：**3.7570×10⁻¹³**；退出时间矩恒等式最大误差：**5.3930×10⁻¹²**。
- 校准预测最大质量误差：**3.77×10⁻¹⁵**。
- 机制所有 condition 最大概率质量误差：**2.00×10⁻¹⁵**；最小原始概率为 −5.20×10⁻¹²⁹，仅将这种舍入量清零，不作大幅修正。
- 机制积分从 rtol=10⁻⁹ 收紧到 10⁻¹⁰，全部 condition 的最大概率差：**9.55×10⁻¹¹**。最终表使用 rtol=10⁻¹⁰、atol=10⁻¹³。
- 提交模型再次用 rtol=2×10⁻¹¹ 传播，最大概率差：**1.33×10⁻¹¹**。
- 最终 RK4 搜索目标与严格时变 ODE NLL 相差 **2.62×10⁻⁷**。
- 机制最终 8 个参数伴随梯度抽查，有限差分最大绝对误差 **2.53×10⁻⁶**；校准梯度抽查最大误差 **4.44×10⁻⁷**。
- 精确 SSA 均值相对 CME 的 Monte Carlo 标准误诊断：四 case 最大 |z| 分别 **2.241、2.855、2.729、1.992**；RMS z 为 **0.829、1.040、0.832、0.724**。这些是相关时点的抽样诊断，不作为独立多重检验或隐藏准确率保证。

## 5. 搜索范围、成本与复跑
短测完整 30 候选 likelihood/gradient 约 0.031 秒后固定预算：两次 dense relaxed 初始化、逐级删除、两轮 add/drop/swap 筛选及精拟合、四起点最终拟合、全部最终删除检查。dense relaxed 阶段仅用于初始化；最终所选模型严格使用公开 bounds。

实际完成 **442 次优化、358 个不同支持、16844 次目标/梯度评估**；两轮邻域分别筛选 150 与 155 个模型。113 次优化满足相对目标变化收敛条件；329 次主要为预算内短筛选，达到预设迭代上限。最终模型报告相对目标变化收敛，不把该标志解释为全局最优证明。最终同支持四起点的 BIC 约为 101777.3943373、101777.3943588、101777.3942808、101777.3942603。

两次成功完整运行：
- 第一次程序内部总耗时 **337.02 秒**；机制搜索 278.43 秒。
- 第二次删除全部生成文件后重跑，总耗时 **217.26 秒**；机制搜索 197.19 秒。
- 两次 BIC 完全一致。**17 个生成的科学文件（包括 conservation_report.json，排除含耗时的 runtime_report.json）逐字节完全一致**，NPZ 也一致。
- 两次合并调用曾触及工具 600 秒上限；随后改用独立调用成功完成，不调整搜索预算、不依运行时长选择支持。此环境约束已在复跑诊断中注明。

复现命令为 `python analysis.py`；已有完整产物时可用 `python analysis.py --verify-existing` 执行清空产物后的复跑验证。

## 限制
这是公开 BIC 驱动的启发式支持搜索，不是所有支持的穷举或全局最优证书。部分观测可能存在机制混淆；没有提供真实 full-state query 概率，因此不能报告隐藏干预 Hellinger、worst-panel 准确率或其最优性。无本地评分器；已完成公开模式、自建数值检查、同模型重建与可复现性验证。可选 numba 在当前环境实际用于加速；脚本提供无 numba 回退，但未测其完整运行成本。

现提交完整候选及证据，供研究者最终审核。
````

**Stage**

````text
result
````

**Evidence**

````text
两次成功执行分别以exit_code=0结束；最后一次执行python analysis.py --verify-existing先删除所有18个生成文件，再完整拟合与生成，记录17个科学文件的SHA256逐字节一致。最终目录仅task.json、data/与声明19文件。runtime_report记录442次优化、358个不同support、16844次目标评估，BIC=101777.3942499393；conservation_report记录完整行数、ID与表头检查、六个(16,96)整数快照数组、零守恒违规。所有35个条件均从序列化所选模型生成并做积分收紧比较；6125个机制query ID覆盖完整。具体数值与限制见answer及两个声明JSON。
````

**Assumptions**

````text
[
  "采用研究者批准的probe、code1阶段律、采样、方差、FPT截尾矩和行序解释，已写入runtime_report.assumptions。",
  "NLL省略模型无关的multinomial组合常数，按规范使用1e-300对数概率floor。",
  "原始候选边界约束未扰动knot rates；256倍干预后的有效速率不再次裁剪。",
  "可选numba加速已实际使用；无numba路径存在但未做完整成本测量。"
]
````

**Uncertainties**

````text
[
  "启发式有限预算支持搜索无全局最优证明；329次短优化达到预设迭代上限，最终候选满足优化器相对目标变化收敛条件。",
  "没有隐藏query真值，不能衡量或保证worst-panel full-state Hellinger准确率。",
  "没有本地评分器；两个报告JSON的内部模式由程序透明定义，因为公开规范没有规定其键。",
  "运行耗时随环境负载变化；合并两次运行曾超过工具600秒上限，拆成独立调用后两次均成功。"
]
````

### Event 43 — Simulator

**Message**

````text
本轮审阅结束，无需追加修订。所提交候选已包含全部 19 个必需文件，artifacts 使用精确原生相对路径；据您的执行报告，已完成精确与自适应随机动力学、独立校准、受支持数限制的时变机制选择，以及从序列化同一模型生成的完整拟合和查询预测。已报告的守恒、概率质量、积分收敛、梯度、策略阈值、模型重建及干净复跑诊断，足以支持本次交付。请保留现有文件及报告中的解释与限制，不将有限支持搜索称为全局最优，也不将数值一致性称为隐藏干预预测准确率的验证。
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
最终候选列齐19个规定路径，并报告实际成功执行和干净复跑；17个非运行耗时生成文件逐字节一致。机制支持大小为5，每候选4个结点，覆盖504个拟合行、6125个查询行及30个单激活面板。报告守恒违规为0，策略代码与TV区间一致，积分收紧最大概率差约9.55e-11，提交模型再传播差约1.33e-11。公开BIC为101777.3942499393，搜索范围及非全局最优限制已披露。这些是代理提交的执行证据，并非本轮独立重跑所得；可见交付未显示需要修订的具体偏差。
````

**Objectives Open**

````text
[]
````

## Provenance

````text
{
  "source_run": "runs/openai-astra-top2-first-pass",
  "repair_run": "runs/repair-1-openai-astra-top2-first-pass",
  "event_log": "runs/openai-astra-top2-first-pass/episodes/asibench_biology.gillespie_ssssa_michaelis_menten-b9ae90c7daa8/candidate_155/attempt-1/output/asibench_biology.gillespie_ssssa_michaelis_menten-b9ae90c7daa8/controller/events.jsonl",
  "event_log_sha256": "3fe099903f6a8ebfd349bc875e2bd16e279102ccfe48705605b6530311e8ae59",
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
