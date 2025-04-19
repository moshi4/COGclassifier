from functools import partial
from pathlib import Path
from typing import Annotated

from typer import Option, Typer

from cogclassifier.plot import plot_cog_count_piechart

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
            help="Output piechart figure file (*.png|*.svg|*.html)",
            show_default=False,
        ),
    ],
    width: Annotated[
        int,
        Option("--width", help="Figure pixel width"),
    ] = 380,
    height: Annotated[
        int,
        Option("--height", help="Figure pixel height"),
    ] = 380,
    show_letter: Annotated[
        bool,
        Option("--show_letter", help="Show functional category lettter on piechart"),
    ] = False,
    sort: Annotated[
        bool,
        Option("--sort", help="Enable descending sort by number count"),
    ] = False,
    dpi: Annotated[
        int,
        Option("--dpi", help="Figure DPI"),
    ] = 100,
) -> None:
    """Plot COGclassifier count piechart figure"""
    plot_cog_count_piechart(
        infile,
        outfile,
        fig_width=width,
        fig_height=height,
        show_letter=show_letter,
        sort=sort,
        dpi=dpi,
    )


if __name__ == "__main__":
    app()
