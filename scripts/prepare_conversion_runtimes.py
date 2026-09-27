#!/usr/bin/env python3
"""Generate reusable dependency recipes and readiness manifests; install on request."""
import argparse,ast,hashlib,json,subprocess,sys
from pathlib import Path
from importlib.metadata import distributions
from personasciencebench.registry import load_adapter
ROOT=Path(__file__).resolve().parents[1]
# Explicit import-to-distribution mapping, never install an arbitrary source string.
PACKAGES={'numpy':'numpy','pandas':'pandas','scipy':'scipy','sklearn':'scikit-learn','matplotlib':'matplotlib','seaborn':'seaborn','xarray':'xarray','netCDF4':'netCDF4','h5py':'h5py','PIL':'Pillow','networkx':'networkx','torch':'torch','tensorflow':'tensorflow','statsmodels':'statsmodels','biopsykit':'biopsykit','rdkit':'rdkit','mne':'mne','cv2':'opencv-python','skimage':'scikit-image','nibabel':'nibabel','anndata':'anndata','scanpy':'scanpy','openpyxl':'openpyxl','sympy':'sympy','tqdm':'tqdm','joblib':'joblib'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--benchmarks',nargs='+',default=['asibench']);p.add_argument('--tasks',nargs='+');p.add_argument('--install',action='store_true');p.add_argument('--existing-python',type=Path,default=ROOT/'.actor-venv');a=p.parse_args()
 output=ROOT/'data/conversion_catalog/runtime';output.mkdir(parents=True,exist_ok=True)
 versions={d.metadata['Name'].lower().replace('_','-'):d.version for d in distributions(path=[str(a.existing_python/'lib'/f'python{sys.version_info.major}.{sys.version_info.minor}'/'site-packages')])}
 records=[]
 for name in a.benchmarks:
  adapter=load_adapter(name,ROOT/'external/sources',ROOT/'manifests/sources.json')
  for task in adapter.enumerate_tasks():
   if a.tasks and task.id not in a.tasks:continue
   unknown=[];packages=[];source=[]
   if name=='scienceagentbench':
    episode=adapter.convert(task.id);script=next(Path(x.source_path) for x in episode.assets if x.id=='eval_programs');tree=ast.parse(script.read_text());modules=set()
    for n in ast.walk(tree):
     if isinstance(n,ast.Import):modules.update(x.name.split('.')[0] for x in n.names)
     elif isinstance(n,ast.ImportFrom) and n.module and not n.level:modules.add(n.module.split('.')[0])
    packages=sorted({PACKAGES[m] for m in modules if m in PACKAGES});unknown=sorted(modules-set(PACKAGES)-sys.stdlib_module_names);source=[str(script.relative_to(ROOT))]
    completeness='Evaluator imports only; dynamic dependencies and actor-chosen libraries may require additional packages.'
   else:
    meta=adapter._metadata()[task.id];packages=meta.get('runtime',{}).get('packages',[]);source=[f'external/sources/asibench/tasks/{task.id.replace(".","/")}/task_meta.yaml'];completeness='Native runtime declaration; external tools and data are separate readiness requirements.'
   requirements='\n'.join(packages)+'\n';key=hashlib.sha256(requirements.encode()).hexdigest()[:16];recipe=output/(key+'.requirements.txt');recipe.write_text(requirements)
   missing=[]
   from packaging.requirements import Requirement
   for req in packages:
    item=Requirement(req);version=versions.get(item.name.lower().replace('_','-'))
    if version is None or (item.specifier and version not in item.specifier):missing.append(req)
   runtime=a.existing_python
   if a.install and packages:
    runtime=ROOT/'external/runtime/converted'/key
    if not (runtime/'pyvenv.cfg').exists():subprocess.run(['uv','venv','--python',sys.executable,str(runtime)],check=True)
    subprocess.run(['uv','pip','install','--python',str(runtime/'bin/python'),'-r',str(recipe)],check=True)
   records.append({'benchmark':name,'task_id':task.id,'requirements_file':str(recipe.relative_to(ROOT)),'recipe_id':key,'source':source,'unmapped_imports':unknown,'missing_in_existing_environment':missing,'runtime':str(runtime),'installed_on_request':a.install,'dependency_evidence':completeness,'runtime_execution_verified':False})
 (output/'manifest.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps({'recipes':len({r['recipe_id'] for r in records}),'tasks':len(records),'unmapped':sum(bool(r['unmapped_imports']) for r in records)}))
if __name__=='__main__':main()
