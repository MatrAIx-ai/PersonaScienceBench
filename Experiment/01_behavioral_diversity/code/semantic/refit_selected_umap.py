"""Refit the two selected cases jointly for the current five-setting panel."""
from importlib.metadata import version
import numpy as np
from analyze import config,OUT,write_json,write_csv,sha
from gallery import load,local_umap

def main():
 c,rows,z=load();coords=[];projections=[]
 for case in c['manual_cases']:
  for role in c['roles']:
   ids=[i for i,r in enumerate(rows) if (r['source'],r['task_id'],r['role'])==(case['source'],case['task_id'],role)]
   assert {rows[i]['arm'] for i in ids}==set(c['arms'])
   x=z[ids].astype(float);xy,settings=local_umap(x)
   projections.append(case|{'role':role,'method':'UMAP','settings':settings,'fit_messages':len(ids),'umap_learn_version':version('umap-learn'),'input_sha256':sha(x.tobytes()),'arms':c['arms']})
   for i,point in zip(ids,xy):coords.append({k:v for k,v in rows[i].items() if k!='text'}|{'umap1':float(point[0]),'umap2':float(point[1]),'displayed':True})
 write_json(OUT/'umap.json',projections);write_csv(OUT/'selected_case_coordinates.csv',coords);write_csv(OUT/'trajectory_coordinates.csv',coords);write_json(OUT/'cases.json',c['manual_cases'])
 print('Refit four UMAP maps:',len(coords),'observed messages',flush=True)
if __name__=='__main__':main()
