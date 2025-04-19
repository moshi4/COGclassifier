import shlex
import subprocess as sp
from pathlib import Path


def test_cli_html(cog_count_file: Path, tmp_path: Path):
    """Test plot_cog_count_piechart CLI (HTML format)"""
    outfile = tmp_path / "cog_count_barchart.html"
    cmd = f"plot_cog_count_piechart -i {cog_count_file} -o {outfile} --width 380 --height 380 --show_letter --sort"  # noqa: E501
    cmd_args = shlex.split(cmd)
    result = sp.run(cmd_args)
    assert result.returncode == 0
    assert outfile.exists()


def test_cli_png(cog_count_file: Path, tmp_path: Path):
    """Test plot_cog_count_piechart CLI (PNG format)"""
    outfile = tmp_path / "cog_count_barchart.png"
    cmd = f"plot_cog_count_piechart -i {cog_count_file} -o {outfile} --width 380 --height 380 --show_letter --sort"  # noqa: E501
    cmd_args = shlex.split(cmd)
    result = sp.run(cmd_args)
    assert result.returncode == 0
    assert outfile.exists()
