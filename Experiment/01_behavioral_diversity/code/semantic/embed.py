#!/usr/bin/env python3
"""Embed raw current messages locally with frozen Qwen weights; resumable cache."""
import argparse
import json
import os
from pathlib import Path
import time
import numpy as np
from analyze import ROOT,CACHE,config,sha,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--device',default='auto');p.add_argument('--threads',type=int,default=4);p.add_argument('--batch-tokens',type=int,default=4096);args=p.parse_args()
    import torch
    from transformers import AutoTokenizer,AutoModel
    import transformers
    torch.set_num_threads(args.threads)
    c=config();path=ROOT.parent/'huggingface_model/hub/models--Qwen--Qwen3-Embedding-0.6B/snapshots'/c['model_revision']
    if not path.exists():raise FileNotFoundError('Frozen local embedding model unavailable')
    device='cuda' if torch.cuda.is_available() else 'cpu' if args.device=='auto' else args.device
    if args.device!='auto':device=args.device
    tokenizer=AutoTokenizer.from_pretrained(path,local_files_only=True,padding_side='left')
    model=AutoModel.from_pretrained(path,local_files_only=True,dtype=torch.float32 if device=='cpu' else torch.float16,attn_implementation='sdpa').to(device).eval()
    rows=json.loads((CACHE/'messages.private.json').read_text());unique={r['text_sha256']:r['text'] for r in rows};directory=CACHE/'vectors'/c['model_revision'];directory.mkdir(parents=True,exist_ok=True)
    pending=[]
    for h,text in unique.items():
        if (directory/f'{h}.npy').exists():continue
        tokens=tokenizer(text,add_special_tokens=True,truncation=False)['input_ids']
        if len(tokens)>c['max_model_tokens']:raise ValueError(f'Message {h} exceeds frozen model context ({len(tokens)} tokens); no silent truncation')
        pending.append((h,tokens))
    pending.sort(key=lambda x:len(x[1]));start=time.monotonic();done=0
    print(json.dumps({'device':device,'unique_messages':len(unique),'pending':len(pending),'pending_tokens':sum(len(t) for _,t in pending)}),flush=True)
    while done<len(pending):
        end=done+1
        while end<len(pending) and (end-done+1)*len(pending[end][1])<=args.batch_tokens and end-done<32:end+=1
        batch=pending[done:end];encoded=tokenizer.pad([{'input_ids':ids,'attention_mask':[1]*len(ids)} for _,ids in batch],padding=True,return_tensors='pt').to(device)
        with torch.inference_mode():
            output=model(**encoded).last_hidden_state[:,-1,:]
            output=torch.nn.functional.normalize(output.float(),p=2,dim=1).cpu().numpy()
        for (h,_),vector in zip(batch,output):np.save(directory/f'{h}.npy',vector)
        done=end
        if done%128<len(batch) or done==len(pending):print(json.dumps({'embedded':done,'total':len(pending),'elapsed_s':round(time.monotonic()-start,1)}),flush=True)
    z=np.stack([np.load(directory/f"{r['text_sha256']}.npy") for r in rows]);np.savez_compressed(CACHE/'embeddings.npz',embeddings=z,hashes=np.array([r['text_sha256'] for r in rows]))
    write_json(CACHE/'embedding_provenance.json',{'model_id':c['model_id'],'revision':c['model_revision'],'torch':torch.__version__,'transformers':transformers.__version__,'device':device,'dtype':'float32' if device=='cpu' else 'float16','pooling':'last nonpadding token','l2_normalized':True,'instruction':None,'truncation':False,'unique_messages':len(unique),'message_rows':len(rows),'model_files':{n:sha((path/n).read_bytes()) for n in ['config.json','tokenizer_config.json']},'cache_key':'fixed model revision + SHA256 of exact outer-whitespace-stripped message; runtime configuration recorded'})
    print('Saved embeddings and provenance',flush=True)

if __name__=='__main__':main()
