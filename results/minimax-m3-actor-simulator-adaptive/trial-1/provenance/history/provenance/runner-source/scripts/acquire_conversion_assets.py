#!/usr/bin/env python3
"""Acquire pinned public Bix capsules and selected ASI instances without per-case edits."""
import argparse,json,hashlib,shutil,urllib.request
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from huggingface_hub import HfApi
from personasciencebench.adapters.base import sha256
from personasciencebench.registry import load_adapter
from personasciencebench.adapters.bixbench import DATASET_REVISION
ROOT=Path(__file__).resolve().parents[1]
def bixbench():
    adapter=load_adapter('bixbench',ROOT/'external/sources',ROOT/'manifests/sources.json')
    capsules={r['capsule_uuid']:r['question_id'] for r in adapter._rows()}
    info=HfApi().dataset_info('futurehouse/BixBench',revision=DATASET_REVISION,files_metadata=True)
    files={s.rfilename:s for s in info.siblings}
    out=ROOT/'data/conversion_catalog';out.mkdir(parents=True,exist_ok=True)
    def one(item):
        capsule,task=item;name=f'CapsuleFolder-{capsule}.zip';meta=files[name];target=adapter.source.assets/name
        expected=meta.lfs.sha256 if meta.lfs else None
        result={'capsule':capsule,'archive':name,'revision':DATASET_REVISION,'expected_sha256':expected}
        try:
            if not target.exists():
                partial=target.with_suffix('.zip.download')
                with urllib.request.urlopen(f'https://huggingface.co/datasets/futurehouse/BixBench/resolve/{DATASET_REVISION}/{name}',timeout=180) as response,partial.open('wb') as stream:shutil.copyfileobj(response,stream,1024*1024)
                if expected and sha256(partial)!=expected:raise ValueError('Downloaded capsule hash mismatch')
                partial.replace(target)
            if expected and sha256(target)!=expected:raise ValueError('Acquired capsule hash mismatch')
            result['archive_sha256']=sha256(target)
            result['input_files']=len(adapter.prepare_assets(task));result['status']='prepared'
        except Exception as e:result.update(status='blocked',error_type=type(e).__name__,error=str(e))
        return result
    results=[]
    with ThreadPoolExecutor(max_workers=6) as pool:
        for f in as_completed([pool.submit(one,item) for item in capsules.items()]):
            results.append(f.result());(out/'bixbench_acquisition.json').write_text(json.dumps(results,indent=2)+'\n')
            print(results[-1]['capsule'],results[-1]['status'],flush=True)
    print(json.dumps({'capsules':len(results),'prepared':sum(r['status']=='prepared' for r in results)}))
def main():
    p=argparse.ArgumentParser();p.add_argument('benchmark',choices=['bixbench','asibench']);p.add_argument('--tasks',nargs='+');a=p.parse_args()
    if a.benchmark=='bixbench':bixbench()
    else:
        from ai4sci_bench.hf.pull import pull_instances
        m=json.loads((ROOT/'manifests/sources.json').read_text())['asibench']
        r=pull_instances('seed31415',output_dir=ROOT/'external/sources/_assets/asibench/instances',tasks=a.tasks,revision=m['dataset_revision'])
        print(json.dumps({'acquired':r.instance_ids,'cached':r.skipped}))
if __name__=='__main__':main()
