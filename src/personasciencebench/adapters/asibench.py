"""Pinned ASI B3 + researcher-held B2 guidance; native isolated local scoring."""
from functools import cache
import json,re,shutil,subprocess
from pathlib import Path,PurePosixPath
import yaml
from personasciencebench.adapters.base import Adapter,sha256,check_submission
from personasciencebench.schema import Asset,Episode,EvaluationResult,EvaluatorSpec,Fact,Provenance,PublicContext,ResearcherContext,TaskSummary

POLICY='asi-b3-collaborative-b2-v1'
class ASIBenchAdapter(Adapter):
    name='asibench'
    @cache
    def _metadata(self):
        ids=json.loads((self.source.repository/'config/public_scorers.json').read_text())['formal_tasks']
        records={}
        for tid in ids:
            path=self.source.repository/'tasks'/tid.replace('.','/')/'task_meta.yaml'
            if not path.exists():path=path.with_name('task.yaml')
            records[tid]=yaml.safe_load(path.read_text())
        return records
    def enumerate_tasks(self):
        return [TaskSummary(id=k,study_id=k,domain=v['domain'],title=v['name'],source_locator=f'tasks/{k.replace(".","/")}/task_meta.yaml') for k,v in self._metadata().items()]
    def pilot_task_ids(self):return ['materials.relaxation_mode_recovery','math.nnls_modulus_deblur']
    def convert(self,task_id):
        meta=self._metadata()[task_id]; instance=self.source.assets/'instances'/(task_id+'__seed31415')
        prompt=instance/'prompt_b3.md'; guidance=instance/'prompt_b2.md'
        if not prompt.is_file():raise ValueError('Acquire native prompt set before conversion')
        facts=[]
        if guidance.is_file():
            text=guidance.read_text()
            # Only explicitly named methodological sections; no raw B1 dump.
            headings=list(re.finditer(r'(?m)^#{1,6}\s+([^\n]+)\n',text))
            for i,h in enumerate(headings):
                title=h.group(1).lower()
                if not any(x in title for x in ['method','approach','guidance','algorithm']):continue
                end=headings[i+1].start() if i+1<len(headings) else len(text)
                value=text[h.end():end].strip()
                if not value or re.search(r'\b(reference result|expected answer|gold answer)\b',value,re.I):continue
                facts.append(Fact(id=f'{task_id}.guidance_{i}',topic='methodological_guidance',text=value,kind='optional_advice',review_status='automated',source=Provenance(source_path=f'{instance.name}/prompt_b2.md',revision=self.source.dataset_revision,locator=f'chars={h.end()}:{end}',sha256=sha256(guidance))))
        data=instance/'data';assets=[]
        if data.is_dir():
            for path in sorted(data.rglob('*')):
                if path.is_file():
                    rel=path.relative_to(data).as_posix()
                    assets.append(Asset(id=rel,source_path=str(path.resolve()),target_path='data/'+rel,sha256=sha256(path)))
        else:
            assets.append(Asset(id='native_data',source_path=str(data.resolve()),target_path='data',kind='directory',acquisition='Acquire this pinned seed31415 instance'))
        assets.append(Asset(id='native_reference',source_path=str((instance/'reference').resolve()),target_path='reference',kind='directory',visibility='evaluator',acquisition='Acquire this pinned seed31415 reference'))
        outputs=[x['name'] for x in meta.get('output',{}).get('files',[])]
        return Episode(id='asibench:'+task_id,benchmark=self.name,source_task_id=task_id,study_id=task_id,domain=meta['domain'],source_revision=self.source.revision,review_status='automated',
            public=PublicContext(question=prompt.read_text(),context='Complete the native B3 task with optional researcher methodological consultation. Preserve all scientific constraints and output requirements.',
                submission={'required_artifacts':outputs,'artifact_keys':'Use each exact native relative output path as its artifacts dictionary key. Include every required file.','answer':'Describe the completed work and evidence.'},
                environment={'input_paths':[a.target_path for a in assets if a.visibility=='actor'],'native_runtime':meta.get('runtime',{}),'runtime_policy':'CPU scientific Python; task-specific availability recorded at preparation'},researcher_topics=[f.topic for f in facts]),
            researcher=ResearcherContext(facts=facts,unknowns=['Reference results, hidden evaluator state, and unstated study facts.']),assets=assets,
            evaluator=EvaluatorSpec(kind='native_isolated_local',version=POLICY,entrypoint='personasciencebench.adapters.asibench:ASIBenchAdapter.evaluate',reference={'instance_dir':str(instance.resolve()),'task_id':task_id},config={'official':False,'seed':31415,'native_scoring_unchanged':True}),
            conversion={'version':POLICY,'dataset_revision':self.source.dataset_revision,'prompt_sha256':sha256(prompt),'condition':'B3 plus B2 methodological consultation; not autonomous B3','context_status':'method_guidance' if facts else 'no_permitted_guidance','runtime_verified':False})
    def evaluate(self,episode,submission,judge=None):
        check_submission(episode,submission)
        if not submission.artifacts:return EvaluationResult(status='missing_submission',evaluator_version=POLICY)
        # Separate evaluator process/workspace; it cannot alter the sealed originals.
        sealed=Path(next(iter(submission.artifacts.values()))).parent
        work=sealed.parent/'asi_native_evaluation';work.mkdir(exist_ok=False)
        pred=work/'prediction';pred.mkdir()
        for name,source in submission.artifacts.items():
            rel=PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe ASI artifact key')
            dest=pred/str(rel);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        instance=Path(episode.evaluator.reference['instance_dir']);shutil.copytree(instance,work/instance.name)
        if (instance/'data').exists():shutil.copytree(instance/'data',pred/'data',dirs_exist_ok=True)
        shutil.copytree(self.source.repository/'ai4sci_bench',work/'ai4sci_bench')
        task_dir=work/'native/tasks'/episode.source_task_id.replace('.','/')
        shutil.copytree(self.source.repository/'tasks'/episode.source_task_id.replace('.','/'),task_dir)
        shutil.copytree(self.source.repository/'config',work/'native/config')
        native_result={'task_id':episode.source_task_id,'instance_id':instance.name,'prompt_level':'b3','status':'completed','agent_output':{'status':'completed','persisted_outputs':{'dir':'prediction'}}}
        (work/'run_result.json').write_text(json.dumps(native_result))
        manifest={'schema_version':2,'benchmark':'ASI-Bench','seed':31415,'task_id':episode.source_task_id,'instance_id':instance.name,'prompt_level':'b3',
            'run_result':'/workspace/run_result.json','prediction_dir':'/workspace/prediction','instance_dir':'/workspace/'+instance.name,'tasks_dir':'/workspace/native/tasks','task_bundle_revision':self.source.revision,'harness':POLICY,'model':getattr(judge,'model',None),'sandbox':'bubblewrap-separated-evaluator'}
        (work/'manifest.json').write_text(json.dumps(manifest))
        (work/'evaluate.py').write_text('import json\nfrom ai4sci_bench.benchflow import score_seed31415_manifest\nr=score_seed31415_manifest(json.load(open("manifest.json")))\njson.dump(r,open("native_score.json","w"),indent=2)\n')
        from personasciencebench.runtime import Sandbox
        runtime=Path(__file__).resolve().parents[3]/'.venv'
        receipt=Sandbox(work,runtime).execute('PYTHONPATH=/workspace python evaluate.py',timeout_seconds=1800)
        (work/'execution.json').write_text(json.dumps(receipt,indent=2))
        output=work/'native_score.json'
        if not output.exists():return EvaluationResult(status='error',evaluator_version=POLICY,errors=['Native ASI evaluator failed'],details={'receipt':receipt})
        result=json.loads(output.read_text())
        return EvaluationResult(status='error' if result['scorer_internal_error'] else 'scored',evaluator_version=POLICY,
            metrics={'score':result['score'],'max_score':result['max_score']},details={'official':False,'native_result':result,'evaluator_directory':str(work)})
