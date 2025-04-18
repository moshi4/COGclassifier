import shlex
import subprocess as sp
from pathlib import Path


def test_cli(cog_count_file: Path, tmp_path: Path):
    """Test plot_cog_count_barchart CLI"""
    outfile = tmp_path / "cog_count_barchart.html"
    cmd = f"plot_cog_count_barchart -i {cog_count_file} -o {outfile} --width 540 --height 340 --bar_width 15"  # noqa: E501
    cmd_args = shlex.split(cmd)
    result = sp.run(cmd_args)
    assert result.returncode == 0
    assert outfile.exists()
