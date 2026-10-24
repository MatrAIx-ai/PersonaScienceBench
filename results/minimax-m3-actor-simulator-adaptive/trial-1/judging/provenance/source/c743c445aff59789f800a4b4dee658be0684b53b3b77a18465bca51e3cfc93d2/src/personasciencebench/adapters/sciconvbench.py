"""Automated import of native scientific clarification tasks and intended specs."""
from functools import cache
import json
from personasciencebench.adapters.base import Adapter,sha256
from personasciencebench.schema import Episode,EvaluatorSpec,Fact,Provenance,PublicContext,ResearcherContext,TaskSummary
POLICY='sciconv-native-clarification-persona-v1'
DOMAINS={'fluids':'fluid_mechanics','foam':'fluid_mechanics','pde':'partial_differential_equations','matSci':'materials_science','matToolUse':'materials_science','solMech':'solid_mechanics','solToolUse':'solid_mechanics'}
class SciConvBenchAdapter(Adapter):
    name='sciconvbench'
    @cache
    def _rows(self):
        records={}
        for domain in DOMAINS:
            for mode in ['disambiguation','inconsistency']:
                p=self.source.repository/domain/f'{mode}_{domain}.json'
                for row in json.loads(p.read_text()):
                    tid=f'{domain}/{mode}/{row["id"]}'
                    if tid in records:raise ValueError('Duplicate native case ID')
                    records[tid]=(row,p,domain,mode)
        return records
    def enumerate_tasks(self):
        return [TaskSummary(id=k,study_id=f'{d}:{r["id"]}',domain=DOMAINS[d],title=k,source_locator=str(p.relative_to(self.source.repository))) for k,(r,p,d,m) in self._rows().items()]
    def pilot_task_ids(self):return ['fluids/disambiguation/case_001','pde/inconsistency/case_001']
    def convert(self,task_id):
        row,path,domain,mode=self._rows()[task_id]
        request=row['incomplete_user_req' if mode=='disambiguation' else 'inconsistent_prompt']
        complete=row['complete_user_req' if mode=='disambiguation' else 'correct_prompt']
        issues=row['missing_entities' if mode=='disambiguation' else 'inconsistencies']
        if not request.strip() or not complete.strip() or not issues:raise ValueError('Missing native request, intended specification, or issue annotations')
        if len(request)>20000:raise ValueError('Native paper prompt-length exclusion (>20000 characters)')
        return Episode(id='sciconvbench:'+task_id,benchmark=self.name,source_task_id=task_id,study_id=f'{domain}:{row["id"]}',domain=DOMAINS[domain],source_revision=self.source.revision,track='specification',review_status='automated',
            public=PublicContext(question=request,context='Clarify the scientific task and submit its final specification. Scientific execution is outside this track.',submission={'answer':'Final scientific task specification'},environment={'native_max_questions':10}),
            researcher=ResearcherContext(facts=[Fact(id=task_id+'.intended_specification',topic='intended_task',text=complete,kind='fixed_requirement',review_status='automated',source=Provenance(source_path=str(path.relative_to(self.source.repository)),revision=self.source.revision,locator=f'id={row["id"]}/'+('complete_user_req' if mode=='disambiguation' else 'correct_prompt'),sha256=sha256(path)))],unknowns=['Details absent from the intended specification.']),
            evaluator=EvaluatorSpec(kind='native_dialogue_judges',version=POLICY,reference={'native_row':row,'mode':mode,'domain':domain},config={'native_prompt_and_parser_preserved':True,'judge_model':'configured_at_run_time'}),
            conversion={'version':POLICY,'source_sha256':sha256(path),'population':'Native source pool with paper length cap; no filtering based on previous models successes','native_protocol':'up to 10 questions then forced final specification','researcher_reference_semantics':'Intended user requirements, not scientific solver answers'})
