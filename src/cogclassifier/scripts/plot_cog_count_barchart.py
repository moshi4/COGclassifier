from functools import partial
from pathlib import Path
from typing import Annotated, Optional

import pandas as pd
from typer import Option, Typer

from cogclassifier.plot import plot_cog_count_barchart

Option = partial(Option, metavar="")

app = Typer(add_completion=False)


@app.command(
    no_args_is_help=True,
    epilog=None,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
def cli(
    infile: Annotated[
        Path,
        Option(
            "-i",
            "--infile",
            help="Input COG count result file ('cog_count.tsv')",
            show_default=False,
        ),
    ],
    outfile: Annotated[
        Path,
        Option(
            "-o",
            "--outfile",
            help="Output barchart html file (must be '*.html')",
            show_default=False,
        ),
    ],
    width: Annotated[
        int,
        Option("--width", help="Figure pixel width"),
    ] = 540,
    height: Annotated[
        int,
        Option("--height", help="Figure pixel height"),
    ] = 340,
    bar_width: Annotated[
        int,
        Option("--bar_width", help="Figure bar width"),
    ] = 15,
    y_limit: Annotated[
        Optional[int],
        Option("--y_limit", help="Y-axis max limit value", show_default=False),
    ] = None,
    percent_style: Annotated[
        bool,
        Option("--percent_style", help="Plot percent style instead of number count"),
    ] = False,
    sort: Annotated[
        bool,
        Option("--sort", help="Enable descending sort by number count"),
    ] = False,
) -> None:
    """Plot COGclassifier count barchart figure"""
    plot_cog_count_barchart(
        pd.read_csv(infile, sep="\t"),
        outfile,
        fig_width=width,
        fig_height=height,
        bar_width=bar_width,
        y_limit=y_limit,
        percent_style=percent_style,
        sort=sort,
    )


if __name__ == "__main__":
    app()
