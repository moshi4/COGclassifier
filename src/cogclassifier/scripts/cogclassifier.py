# from __future__ import annotations

import logging
import os
import platform
import sys
from functools import partial
from pathlib import Path
from typing import Annotated

import typer
from typer import Option, Typer

from cogclassifier import CogClassifier, __version__, const
from cogclassifier.logger import init_logger
from cogclassifier.plot import (
    plot_cog_count_barchart,
    plot_cog_count_piechart,
)
from cogclassifier.utils import exit_handler, logging_timeit

Option = partial(Option, metavar="")

app = Typer(add_completion=False)


def version_callback(v: bool):
    """Callback function for print version"""
    if v:
        print(f"v{__version__}")
        raise typer.Exit()


@app.command(
    no_args_is_help=True,
    epilog=None,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@logging_timeit
@exit_handler
def cli(
    infile: Annotated[
        Path,
        Option(
            "-i",
            "--infile",
            help="Input query protein fasta file",
            show_default=False,
        ),
    ],
    outdir: Annotated[
        Path,
        Option(
            "-o",
            "--outdir",
            help="Output directory",
            show_default=False,
        ),
    ],
    download_dir: Annotated[
        Path,
        Option("-d", "--download_dir", help="Download COG & CDD resources directory"),
    ] = const.CACHE_DIR,
    thread_num: Annotated[
        int,
        Option("-t", "--thread_num", help="RPS-BLAST num_thread parameter"),
    ] = const.DEFAULT_CPU,
    evalue: Annotated[
        float,
        Option("-e", "--evalue", help="RPS-BLAST e-value parameter"),
    ] = 1e-2,
    quiet: Annotated[
        bool,
        Option("-q", "--quiet", help="No print log on screen"),
    ] = False,
    debug: Annotated[
        bool,
        Option("--debug", help="Print debug log", hidden=True),
    ] = False,
    _: Annotated[
        bool,
        Option(
            "-v",
            "--version",
            help="Print version information",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """A tool for classifying prokaryote protein sequences into COG functional category"""  # noqa: E501
    args = locals()
    os.makedirs(outdir, exist_ok=True)

    # Initialize logger
    log_file = outdir / "cogclassifier.log"
    init_logger(quiet=quiet, verbose=debug, log_file=log_file)
    logger = logging.getLogger(__name__)

    # Run COGclassifier
    logger.info(f"Run COGclassifier v{__version__}")
    logger.info(f"$ {Path(sys.argv[0]).name} {' '.join(sys.argv[1:])}")
    logger.info(f"Operating System: {sys.platform}")
    logger.info(f"Python Version: v{platform.python_version()}")
    for name, value in args.items():
        if name not in ("quiet", "debug", "_"):
            logger.info(f"Parameter: {name}={value}")
    cog_stats = CogClassifier(
        infile,
        download_dir=download_dir,
        thread_num=thread_num,
        evalue=evalue,
    ).run()

    # Write RPS-BLAST result
    rpsblast_file = outdir / "rpsblast.tsv"
    with open(rpsblast_file, "w") as f:
        f.write(str(cog_stats.blast_rec))
    logger.info("Write rpsblast search result")
    logger.info(f"=> {rpsblast_file}")

    # Write COG count summary
    cog_count_file = outdir / "cog_count.tsv"
    cog_stats.count_summary_df.to_csv(cog_count_file, sep="\t", index=False)
    logger.info("Write summary of COG functional category count")
    logger.info(f"=> {cog_count_file}")
    # Write COG classification result
    cog_classify_file = outdir / "cog_classify.tsv"
    cog_stats.query_classify_df.to_csv(cog_classify_file, sep="\t", index=False)
    logger.info("Write result of COG classification per query")
    logger.info(f"=> {cog_classify_file}")

    # Plot barchart
    barchart_html_file = outdir / "cog_count_barchart.html"
    barchart_png_file = barchart_html_file.with_suffix(".png")
    logger.info("Plot COG count barchart figure")
    plot_cog_count_barchart(cog_stats.count_summary_df, barchart_html_file)
    logger.info(f"=> {barchart_html_file}")
    plot_cog_count_barchart(cog_stats.count_summary_df, barchart_png_file)
    logger.info(f"=> {barchart_png_file}")
    # Plot piechart
    piechart_html_file = outdir / "cog_count_piechart.html"
    piechart_png_file = piechart_html_file.with_suffix(".png")
    props = dict(show_letter=True, sort=True)
    logger.info("Plot COG count piechart figure")
    plot_cog_count_piechart(cog_stats.count_summary_df, piechart_html_file, **props)  # type: ignore
    logger.info(f"=> {piechart_html_file}")
    plot_cog_count_piechart(cog_stats.count_summary_df, piechart_png_file, **props)  # type: ignore
    logger.info(f"=> {piechart_png_file}")


if __name__ == "__main__":
    app()
