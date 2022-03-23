import os
import subprocess as sp
from glob import glob
from pathlib import Path

from cogclassifier import cogclassifier


def test_run(
    example_fasta_file: Path,
    cog_download_dir: Path,
    tmp_path: Path,
    remove_small_download_files,
):
    """Test COGclassifier workflow"""
    cpu_num = os.cpu_count()
    thread_num = 1 if cpu_num is None or cpu_num == 1 else cpu_num - 1

    cogclassifier.run(
        query_fasta_file=example_fasta_file,
        outdir=tmp_path,
        download_dir=cog_download_dir,
        thread_num=thread_num,
        evalue=1e-2,
    )

    # Check properly generate 7 result files
    assert len(glob(str(tmp_path / "*"))) == 7


def test_run_from_cli(
    example_fasta_file: Path,
    cog_download_dir: Path,
    tmp_path: Path,
    remove_small_download_files,
):
    """Test COGclassifier workflow from CLI"""
    cpu_num = os.cpu_count()
    thread_num = 1 if cpu_num is None or cpu_num == 1 else cpu_num - 1

    cmd = (
        f"COGclassifier -i {example_fasta_file} -o {tmp_path} -d {cog_download_dir} "
        + f"-t {thread_num} -e 1e-2"
    )
    sp.run(cmd, shell=True)

    # Check properly generate 7 result files
    assert len(glob(str(tmp_path / "*"))) == 7
