import shlex
import subprocess as sp
from pathlib import Path


def test_cli(example_fasta_file: Path, tmp_path: Path):
    """Test COGclassifier CLI"""
    cmd = f"COGclassifier -i {example_fasta_file} -o {tmp_path} --thread_num 1 --evalue 1e-2"  # noqa: E501
    cmd_args = shlex.split(cmd)
    result = sp.run(cmd_args)
    assert result.returncode == 0
    outfile_names = [
        "rpsblast.tsv",
        "cog_count.tsv",
        "cog_classify.tsv",
        "cog_count_barchart.html",
        "cog_count_piechart.html",
        "cogclassifier.log",
    ]
    for outfile_name in outfile_names:
        outfile = tmp_path / outfile_name
        assert outfile.exists()
