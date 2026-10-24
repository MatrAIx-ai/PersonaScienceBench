#!/usr/bin/env python3
"""Offline metadata audit and 40-per-source sampling feasibility experiment.

No model calls or benchmark outcomes are used. The optimized sample is a
feasibility witness, NOT a probability sample or a launch-ready task manifest.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import random
import re
import shutil
import subprocess

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['discoverybench', 'bixbench', 'expbench', 'sciconvbench', 'asibench']
FAMILIES = ['life', 'physical_engineering', 'math_cs', 'social_humanities']
SEED = 20260929
VISUAL = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.gif', '.svg', '.mp4'}


def digest(text):
    return hashlib.sha256(re.sub(r'\s+', ' ', text.strip().lower()).encode()).hexdigest()


def record(source, tid, family, subfield, question, study, basis, **kwargs):
    return dict(source=source, task_id=tid, family=family, subfield=subfield,
                question=question, study_id=study, classification_basis=basis,
                task_family_id=source + ':' + digest(question),
                exclusion_reasons=[], figure_output=False, **kwargs)


def inventory():
    rows = []
    base = ROOT / 'external/sources'
    # Native source-domain mapping; software requirements is computing, not physics.
    mapping = {'biology': 'life', 'engineering': 'math_cs', 'humanities': 'social_humanities',
               'sociology': 'social_humanities', 'economics': 'social_humanities',
               'meta science': 'social_humanities'}
    for p in sorted((base / 'discoverybench/discoverybench/real').glob('*/*/metadata_*.json')):
        meta = json.loads(p.read_text())
        split, study, filename = p.parts[-3:]
        for group, queries in enumerate(meta['queries']):
            for q in queries:
                # Collapse raw/processed copies and study-directory suffix variants
                # for clustering; question text independently deduplicates tasks.
                study_group = re.sub(r'_(raw|processed)$', '', study)
                if study.startswith('nls_'):
                    study_group = 'nls'
                r = record('discoverybench', f'{split}/{study}/{filename}/{group}/{q["qid"]}',
                           mapping[meta['domain']], meta['domain'], q['question'], study_group,
                           'Native metadata domain; engineering source is software requirements.')
                if any(not (p.parent / x['name']).is_file() for x in meta['datasets']):
                    r['exclusion_reasons'].append('missing_declared_data')
                rows.append(r)

    # This reads archive membership only, never executes notebooks or graders.
    from personasciencebench.adapters.bixbench import BixBenchAdapter
    import zipfile
    bx = base / '_assets/bixbench'
    capsule_meta = {}
    for row in map(json.loads, (bx / 'BixBench.jsonl').read_text().splitlines()):
        capsule = row['capsule_uuid']
        if capsule not in capsule_meta:
            archive = bx / f'CapsuleFolder-{capsule}.zip'
            issues = []
            if not archive.is_file():
                issues.append('missing_capsule')
            else:
                prefix = f'CapsuleData-{capsule}/'
                with zipfile.ZipFile(archive) as z:
                    members = [n[len(prefix):] for n in z.namelist()
                               if n.startswith(prefix) and not n.endswith('/')]
                allowed = [n for n in members if BixBenchAdapter._permitted_input(n)]
                unknown = [n for n in members if not BixBenchAdapter._permitted_input(n)
                           and Path(n).suffix != '.ipynb'
                           and not re.search(r'(?:^|[_/-])(solution|answer|gold)(?:$|[_/.-])', n, re.I)]
                if unknown:
                    issues.append('unresolved_input_roles')
                if not allowed or any(not (bx / 'prepared' / capsule / n).is_file() for n in allowed):
                    issues.append('missing_prepared_inputs')
                if any(Path(n).suffix.lower() in VISUAL for n in allowed):
                    issues.append('visual_input_file')
            capsule_meta[capsule] = issues
        r = record('bixbench', row['question_id'], 'life', str(row['categories']),
                   row['question'], capsule, 'Biological question and native category annotations.')
        r['exclusion_reasons'].extend(capsule_meta[capsule])
        if 'imaging' in str(row['categories']).lower():
            r['exclusion_reasons'].append('imaging_category')
        rows.append(r)

    # Explicit paper-level screening with exceptions for mixed-modality papers.
    visual_papers = {'95262', '94155', '95333', '95818', '96893', '97674', '94065',
                     '93219', '97514', '19610', '18318', '19044', '17666', '18889',
                     '19269', '19128', '18447'}
    physical_papers = {'97882', '93022', '97791', '97609', '95974', '18865', '19281'}
    path = ROOT / 'data/exp_bench/tasks.jsonl'
    if not path.exists():
        subprocess.run([str(ROOT / '.venv/bin/python'), str(ROOT / 'scripts/expbench/examine_exp_bench.py')],
                       check=True, stdout=subprocess.DEVNULL)
    for row in map(json.loads, path.read_text().splitlines()):
        pid = row['paper_id']
        r = record('expbench', row['task_id'], 'physical_engineering' if pid in physical_papers else 'math_cs',
                   row['paper_title'], row['question'], row['conference'] + '/' + pid,
                   'Paper title/objective plus public question; molecular chemistry is physical; PsychoBench studies LLMs, so CS.')
        if not row['reference_design_schema_valid'] or row['question_match'] not in {'exact', 'unicode_or_whitespace', 'markdown_formatting'}:
            r['exclusion_reasons'].append('invalid_reference_or_question_alignment')
        if pid in visual_papers:
            r['exclusion_reasons'].append('image_or_perception_centric_paper')
        if pid == '97791' and row['task_index'] not in {2, 5, 6, 7}:
            r['exclusion_reasons'].append('image_based_astronomy_question')
        if pid == '97609' and row['task_index'] == 0:
            r['exclusion_reasons'].append('point_cloud_perception')
        if pid == '95974':
            r['exclusion_reasons'].append('mixed_driving_perception_scope_not_reviewed')
        if pid == '19292':
            r['exclusion_reasons'].append('audio_task_outside_text_numeric_scope')
        r['figure_output'] = pid == '97791' and row['task_index'] == 5
        rows.append(r)

    domains = ['fluids', 'foam', 'pde', 'matSci', 'matToolUse', 'solMech', 'solToolUse']
    for domain in domains:
        for mode in ['disambiguation', 'inconsistency']:
            p = base / 'sciconvbench' / domain / f'{mode}_{domain}.json'
            for row in json.loads(p.read_text()):
                q = row.get('incomplete_user_req' if mode == 'disambiguation' else 'inconsistent_prompt', '')
                intended = row.get('complete_user_req' if mode == 'disambiguation' else 'correct_prompt', '')
                r = record('sciconvbench', f'{domain}/{mode}/{row["id"]}',
                           'math_cs' if domain == 'pde' else 'physical_engineering', domain,
                           q, domain + ':' + digest(intended),
                           'Native domain; numerical PDE specification classified as applied mathematics (sensitivity checked).')
                match = re.search(r'Task ID:\s*(\S+)', intended)
                family = domain + ':' + (match.group(1) if match else digest(intended))
                r['study_id'] = family
                r['task_family_id'] = 'sciconvbench:' + family
                if not q.strip() or not intended.strip() or not row.get('missing_entities' if mode == 'disambiguation' else 'inconsistencies') or len(q) > 20000:
                    r['exclusion_reasons'].append('native_conversion_exclusion')
                # The task is specification dialogue: described solver plots are
                # not rendered or visually judged by this benchmark's evaluator.
                rows.append(r)

    ids = json.loads((base / 'asibench/config/public_scorers.json').read_text())['formal_tasks']
    excluded = {'math.nnls_modulus_deblur': 'image_reconstruction',
                'robotics.multiregime_icp_degeneracy': 'point_cloud_perception',
                'robotics.occupancy_grid_mapping_correlated_clutter': 'spatial_mapping_scope_ambiguous'}
    for tid in ids:
        meta = yaml.safe_load((base / 'asibench/tasks' / tid.replace('.', '/') / 'task_meta.yaml').read_text())
        domain = meta['domain']
        family = 'life' if domain in {'biology', 'biostat'} else 'math_cs' if domain in {'math', 'computer_science'} else 'physical_engineering'
        instance = base / '_assets/asibench/instances' / (tid + '__seed31415')
        q = (instance / 'prompt_b3.md').read_text() if (instance / 'prompt_b3.md').exists() else meta['name']
        r = record('asibench', tid, family, domain, q, tid, 'Native domain and task objective; Earth-science domain retained.')
        r['figure_output'] = any(x.get('type') in {'image', 'figure', 'video'} or Path(x['name']).suffix.lower() in VISUAL
                                 for x in meta.get('output', {}).get('files', []))
        if tid in excluded:
            r['exclusion_reasons'].append(excluded[tid])
        if not (instance / 'data').is_dir() or not (instance / 'reference').is_dir() or not (instance / 'prompt_b3.md').is_file():
            r['exclusion_reasons'].append('missing_adapter_required_assets')
        if tid == 'electrical_engineering.cmos_opamp_design' and not shutil.which('ngspice'):
            r['exclusion_reasons'].append('missing_ngspice')
        rows.append(r)
    return rows


def frame(rows, strict=False, pde_physical=False):
    groups = defaultdict(list)
    for row in rows:
        if row['exclusion_reasons'] or (strict and row['figure_output']):
            continue
        r = dict(row)
        if pde_physical and r['source'] == 'sciconvbench' and r['subfield'] == 'pde':
            r['family'] = 'physical_engineering'
        groups[r['task_family_id']].append(r)
    # Deterministic pseudorandom representative among equivalent variants.
    return [min(group, key=lambda r: digest(str(SEED) + r['task_id']))
            for _, group in sorted(groups.items())]


def matrix(rows):
    return {s: {f: sum(r['source'] == s and r['family'] == f for r in rows) for f in FAMILIES} for s in SOURCES}


def random_samples(rows, quota, simulations):
    pools = {s: [r for r in rows if r['source'] == s] for s in SOURCES}
    rng = random.Random(SEED)
    draws = []
    sample = None
    for i in range(simulations):
        selected = [r for s in SOURCES for r in rng.sample(pools[s], quota)]
        if i == 0:
            sample = selected
        counts = Counter(r['family'] for r in selected)
        draws.append([counts[f] for f in FAMILIES])
    a = np.array(draws)
    return sample, {'simulations': simulations, 'all_four_fraction': float(np.mean((a > 0).all(axis=1))),
                    'family_counts': {f: {'mean': float(a[:, i].mean()),
                                         'p05': float(np.quantile(a[:, i], .05)),
                                         'p95': float(np.quantile(a[:, i], .95))} for i, f in enumerate(FAMILIES)}}


def balanced_sample(rows, quota):
    """Lexicographic squared family imbalance, study diversity, seeded tie break."""
    n = len(rows)
    total = quota * len(SOURCES)
    groups = sorted({(r['source'], r['study_id']) for r in rows})
    group_index = {g: i for i, g in enumerate(groups)}
    y_start = n
    z_start = n + len(FAMILIES) * (total + 1)
    width = z_start + len(groups)
    constraints, lo, hi = [], [], []

    def add(items, lower, upper):
        constraints.append(items); lo.append(lower); hi.append(upper)

    for s in SOURCES:
        add({i: 1 for i, r in enumerate(rows) if r['source'] == s}, quota, quota)
    for j, f in enumerate(FAMILIES):
        offset = y_start + j * (total + 1)
        add({offset + k: 1 for k in range(total + 1)}, 1, 1)
        items = {i: 1 for i, r in enumerate(rows) if r['family'] == f}
        items.update({offset + k: -k for k in range(total + 1)})
        add(items, 0, 0)
    for group, gi in group_index.items():
        items = {i: -1 for i, r in enumerate(rows) if (r['source'], r['study_id']) == group}
        items[z_start + gi] = 1
        add(items, -np.inf, 0)
    a = lil_matrix((len(constraints), width))
    for i, items in enumerate(constraints):
        for j, v in items.items(): a[i, j] = v
    c = np.zeros(width)
    # Under integer count changes, a unit of imbalance costs more than all
    # possible diversity/tie-break improvements. A study outweighs all random terms.
    rng = random.Random(SEED)
    c[:n] = [rng.random() / (10 * total) for _ in rows]
    for j in range(len(FAMILIES)):
        c[y_start + j * (total + 1):y_start + (j + 1) * (total + 1)] = [
            (k - total / len(FAMILIES)) ** 2 * (total + 1) for k in range(total + 1)]
    c[z_start:] = -1
    result = milp(c, integrality=np.ones(width), bounds=Bounds(0, 1),
                  constraints=LinearConstraint(a.tocsr(), lo, hi),
                  options={'time_limit': 120, 'mip_rel_gap': 0})
    if not result.success:
        raise RuntimeError(f'Allocation not certified optimal: {result.message}')
    selected = [r for i, r in enumerate(rows) if result.x[i] > .5]
    counts = Counter(r['family'] for r in selected)
    return selected, {'optimal': True, 'squared_family_deviation': sum((counts[f] - total / 4)**2 for f in FAMILIES),
                      'distinct_study_groups': len({(r['source'], r['study_id']) for r in selected}),
                      'objective': 'Minimize squared deviation from equal family counts, then maximize study-group coverage; seeded random tie-break.'}


def write_report(summary, rows, output):
    def table(values):
        lines = ['| Source | Life sciences | Physical / engineering | Mathematics / CS | Social / humanities | Total |',
                 '|---|---:|---:|---:|---:|---:|']
        for source in SOURCES:
            numbers = [values[source][f] for f in FAMILIES]
            lines.append('| ' + source + ' | ' + ' | '.join(map(str, numbers + [sum(numbers)])) + ' |')
        totals = [sum(values[s][f] for s in SOURCES) for f in FAMILIES]
        lines.append('| **Total** | ' + ' | '.join(map(str, totals + [sum(totals)])) + ' |')
        return '\n'.join(lines)

    main = summary['scenarios']['diagnostic_plots_allowed']
    strict = summary['scenarios']['no_figure_outputs']
    lines = ['# Empirical superfamily sampling audit', '',
             f'Seed: **{SEED}**. Audited **{len(rows)} source question records**. No model calls or benchmark executions.', '',
             'This tests whether the **four proposed reporting superfamilies** are represented when sampling an equal number of questions from each benchmark. It does not discover a unique scientific taxonomy.', '',
             '## Classification and eligibility', '',
             '- **Life:** biology and biostatistics; all Bix questions retain their biological application label.',
             '- **Physical / engineering:** physics, chemistry, astronomy, materials, Earth science, electrical engineering, robotics, fluids and mechanics. Molecular-design EXP papers are classified as chemistry.',
             '- **Mathematics / CS:** mathematics, CS, software requirements, and numerical PDE specifications. PsychoBench evaluates LLMs and is classified as CS; that boundary is contestable.',
             '- **Social / humanities:** sociology, economics, archaeology/humanities and meta-science. Native Discovery domain labels are retained, including its health/social survey questions.', '',
             'The main scenario allows diagnostic plots produced by numerical code, but excludes image-centric tasks, conservative unresolved modality cases, missing declared assets and unresolved Bix input roles. EXP uses explicit paper-objective exclusions plus question-level exceptions for mixed astronomy and aerodynamic datasets. Audio-centric design tasks are outside this text/numerical screen.', '',
             '**Screened does not mean runtime-certified.** All 200 native evaluators have not been executed. Further scientific-objective review, external-tool checks and resource limits can shrink this frame. Counts must not be described as a finalized runnable panel.', '',
             'Discovery duplicates are normalized question-text matches. SciConv also groups identical intended specifications or matching explicit native Task IDs across modes. This does not detect every semantic near-duplicate or parameterized variant. Group counts are clustering proxies, not a claim that all groups are independent studies.', '',
             '## Screened candidate capacities', '', table(main['eligible_distinct_task_families']), '',
             'Machine-readable decisions, public questions, classification basis, grouping keys and exclusions: [inventory.jsonl](inventory.jsonl).', '']
    if main['feasible']:
        lines += ['## Actual source-stratified random sample', '',
                  f'Uniformly selected {summary["quota_per_source"]} candidate task families without replacement from each source. Equivalent variants use a frozen seeded representative.', '',
                  table(main['random_sample_counts']), '',
                  '[Actual sampled task IDs](diagnostic_plots_allowed.random_sample.csv). This is a source-stratified random sample; study sizes are not equalized.', '',
                  '## Repeated sampling experiment', '',
                  'These are repeated offline draws of task IDs, **not model episodes**. The intervals below describe composition across draws, not performance confidence intervals.', '',
                  '| Family | Mean number of questions | 5th–95th percentile across draws |', '|---|---:|---:|']
        simulation = main['random_sampling_simulation']
        for family, stats in simulation['family_counts'].items():
            lines.append(f'| {family} | {stats["mean"]:.3f} | {stats["p05"]:.0f}–{stats["p95"]:.0f} |')
        lines += ['', f'All four families appeared in **{simulation["all_four_fraction"]:.1%} of {simulation["simulations"]} draws**. This observed frequency is not a guarantee for every possible draw.', '',
                  '## Optimized family-balance feasibility witness', '',
                  'Integer optimization fixes the same source quotas, minimizes the sum of squared deviations from equal family totals, then maximizes study-group coverage. A seeded random objective breaks remaining ties. There are no hand-entered source–family quotas.', '',
                  table(main['balanced_sample_counts']), '',
                  '[Optimized task IDs](diagnostic_plots_allowed.balanced_sample.csv). **This optimizer-selected set is a feasibility witness, not a probability sample.** Its inclusion probabilities are not known.', '',
                  f'Certified optimum squared deviation: **{main["optimization"]["squared_family_deviation"]}**; represented study-group proxies: **{main["optimization"]["distinct_study_groups"]}**.', '',
                  'Exact equality is impossible under this mapping: social/humanities is available only through Discovery, whose source quota limits it to 40. The optimized solution uses all Discovery slots for that family and loses Discovery biology/computing coverage. This exposes a tradeoff between balanced margins and within-source breadth; it is not a recommendation to discard that breadth silently.', '']
        with (output / 'diagnostic_plots_allowed.random_sample.csv').open() as f:
            sampled = list(csv.DictReader(f))
        lines += ['## Native subfield coverage in the random sample', '',
                  'Superfamily totals do not imply adequate subfield sample sizes. These are native domain labels, not a completed cross-source subfield taxonomy. Bix has overlapping category lists and EXP has paper titles; neither is counted as a mutually exclusive subfield taxonomy here.', '',
                  '| Source | Native domain | Questions |', '|---|---|---:|']
        for source in ['discoverybench', 'sciconvbench', 'asibench']:
            for domain, count in sorted(Counter(r['subfield'] for r in sampled if r['source'] == source).items()):
                lines.append(f'| {source} | {domain} | {count} |')
        lines += ['', '| Superfamily | Questions | Source-study group proxies |', '|---|---:|---:|']
        for family in FAMILIES:
            part = [r for r in sampled if r['family'] == family]
            lines.append(f'| {family} | {len(part)} | {len({(r["source"], r["study_id"]) for r in part})} |')
        lines += ['', 'Native subfields with only one or two sampled questions support examples or exploratory descriptions, not precise standalone comparisons. Question counts also overstate independent evidence when several questions share a study.', '']
    strict_asi = sum(strict['eligible_distinct_task_families']['asibench'].values())
    lines += ['## Sensitivity and limitations', '',
              f'- Excluding declared figure outputs leaves **{strict_asi} ASI candidates** after the other screening rules. Forty per benchmark is then infeasible. The initial 26 no-figure ASI records additionally lose two missing-data cases and two perception/spatial-mapping exclusions.',
              '- Moving all SciConv PDE tasks into physical/engineering still represents all four families. The alternate allocations and simulations are in [summary.json](summary.json).',
              '- Purely metadata-driven domain assignments are transparent but are not an independent two-reviewer field audit. Molecular biology/chemistry, LLM psychology, Earth ecology and applied PDEs have plausible alternative labels.',
              '- Acquisition readiness is distinct from scientific or runtime validity. R-based Bix analyses, expensive ASI computations, unresolved source-group dependence and mixed-modality EXP tasks still warrant task-level review.',
              '- The historical pilot outcomes were not read or used to select tasks. The sample can overlap historical tasks by chance; this audit does not implement a holdout split.', '',
              '## Reproduce', '',
              'From the repository root, with the downloaded sources and local environments:', '',
              '```bash', '.venv/bin/python scripts/audit_superfamily_sampling.py', '```', '',
              'The script uses only local source data, verifies checkout revisions and records inventory/script hashes. It does not load credentials, call models, alter historical experiment configurations or launch episodes. The frozen native EXP join is created offline if absent.', '',
              '[Audit script](../../../scripts/audit_superfamily_sampling.py) · [Summary and provenance](summary.json)', '']
    (output / 'README.md').write_text('\n'.join(lines))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT / 'reports/conversion_v2/superfamily_audit')
    p.add_argument('--quota', type=int, default=40)
    p.add_argument('--simulations', type=int, default=1000)
    args = p.parse_args()
    if args.quota < 1 or args.simulations < 1: p.error('Counts must be positive')
    args.output.mkdir(parents=True, exist_ok=True)
    specs = json.loads((ROOT / 'manifests/sources.json').read_text())
    revisions = {}
    for source in SOURCES:
        if source == 'expbench':
            continue
        repository = ROOT / 'external/sources' / specs[source]['repository_directory']
        revision = subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], text=True).strip()
        if revision != specs[source]['revision']:
            raise ValueError(f'{source}: checkout differs from pinned revision')
        revisions[source] = revision
    rows = inventory()
    (args.output / 'inventory.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    summary = {'seed': SEED, 'quota_per_source': args.quota, 'raw_counts': matrix(rows),
               'classification': 'Native-domain/paper-objective mapping; a reproducible screening audit, not independent human annotation.',
               'runtime_verified': False, 'model_calls': 0, 'scenarios': {}}
    for name, strict, pde_physical in [('diagnostic_plots_allowed', False, False),
                                      ('no_figure_outputs', True, False),
                                      ('pde_classified_physical', False, True)]:
        candidates = frame(rows, strict, pde_physical)
        counts = matrix(candidates)
        entry = {'eligible_distinct_task_families': counts,
                 'study_groups': {s: len({r['study_id'] for r in candidates if r['source'] == s}) for s in SOURCES},
                 'feasible': all(sum(counts[s].values()) >= args.quota for s in SOURCES)}
        if entry['feasible']:
            sample, simulation = random_samples(candidates, args.quota, args.simulations)
            selected, optimization = balanced_sample(candidates, args.quota)
            entry.update(random_sample_counts=matrix(sample), random_sampling_simulation=simulation,
                         balanced_sample_counts=matrix(selected), optimization=optimization)
            for suffix, selected_rows in [('random_sample', sample), ('balanced_sample', selected)]:
                fields = ['source', 'task_id', 'family', 'subfield', 'study_id', 'task_family_id']
                with (args.output / f'{name}.{suffix}.csv').open('w', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(selected_rows)
            assert all(sum(v.values()) == args.quota for v in entry['balanced_sample_counts'].values())
            assert len({r['task_family_id'] for r in selected}) == len(selected)
        summary['scenarios'][name] = entry
        print(name, json.dumps(entry), flush=True)
    summary['exclusion_reason_counts'] = {s: dict(Counter(reason for r in rows if r['source'] == s for reason in r['exclusion_reasons'])) for s in SOURCES}
    summary['input_provenance'] = {'sources_manifest_sha256': hashlib.sha256((ROOT/'manifests/sources.json').read_bytes()).hexdigest(),
                                 'exp_manifest_sha256': hashlib.sha256((ROOT/'manifests/expbench.json').read_bytes()).hexdigest(),
                                 'verified_repository_revisions': revisions,
                                 'inventory_sha256': hashlib.sha256((args.output/'inventory.jsonl').read_bytes()).hexdigest(),
                                 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    write_report(summary, rows, args.output)


if __name__ == '__main__':
    main()
