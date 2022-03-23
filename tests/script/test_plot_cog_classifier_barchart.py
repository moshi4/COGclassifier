import subprocess as sp
from pathlib import Path

import pandas as pd
from cogclassifier.cogclassifier import plot_cog_classifier_barchart


def test_barchart_plot_default(classifier_count_file: Path, tmp_path: Path):
    """Test barchart plot with default_parameter"""
    html_outfile = tmp_path / "out.html"
    plot_cog_classifier_barchart(
        df=pd.read_csv(classifier_count_file, sep="\t"),
        html_outfile=html_outfile,
        fig_width=520,
        fig_height=340,
        bar_width=15,
    )
    assert html_outfile.exists()


def test_barchart_plot_not_default(classifier_count_file: Path, tmp_path: Path):
    """Test barchart plot with not-default_parameter"""
    html_outfile = tmp_path / "out.html"
    plot_cog_classifier_barchart(
        df=pd.read_csv(classifier_count_file, sep="\t"),
        html_outfile=html_outfile,
        fig_width=300,
        fig_height=340,
        bar_width=8,
        y_limit=15,
        percent_style=True,
        sort=True,
    )
    assert html_outfile.exists()


def test_barchart_plot_from_cli(classifier_count_file: Path, tmp_path: Path):
    """Test barchart plot from CLI"""
    html_outfile = tmp_path / "out.html"
    cmd = (
        f"plot_cog_classifier_barchart -i {classifier_count_file} -o {html_outfile} "
        + "--width 300 --height 340 --bar_width 8 --y_limit 15 --percent_style --sort"
    )
    sp.run(cmd, shell=True)
    assert html_outfile.exists()
