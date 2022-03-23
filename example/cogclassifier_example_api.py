#!/usr/env/bin python3
import os

from cogclassifier import cogclassifier

query_fasta_file = "./input/ecoli.faa"
outdir = "./output/ecoli_cog_classifier"
os.makedirs(outdir, exist_ok=True)

cpu_num = os.cpu_count()
thread_num = cpu_num - 1 if cpu_num is not None else 1

cogclassifier.run(
    query_fasta_file=query_fasta_file,
    outdir=outdir,
    thread_num=thread_num,
    evalue=1e-2,
)
