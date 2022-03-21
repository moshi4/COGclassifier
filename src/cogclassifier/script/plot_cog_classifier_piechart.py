import argparse
from pathlib import Path

import pandas as pd
from cogclassifier.COGclassifier import plot_cog_classifier_piechart


def main():
    """Plot piechart from COGclassifier count results"""
    # Get argument values
    args = get_args()
    infile: Path = args.infile
    outfile: Path = args.outfile
    width: int = args.width
    height: int = args.height
    show_letter: bool = args.show_letter
    sort: bool = args.sort

    # Plot piechart
    plot_cog_classifier_piechart(
        df=pd.read_csv(infile, sep="\t"),
        html_outfile=outfile,
        fig_width=width,
        fig_height=height,
        show_letter=show_letter,
        sort=sort,
    )


def get_args() -> argparse.Namespace:
    """Get arguments

    Returns:
        argparse.Namespace: Argument values
    """
    parser = argparse.ArgumentParser(
        description="Plot piechart of COGclassifier count results",
    )

    parser.add_argument(
        "-i",
        "--infile",
        required=True,
        type=Path,
        help="Input COGclassifier count results file ('classifier_count.tsv')",
        metavar="I",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        required=True,
        type=Path,
        help="Output plot result html file (must be '*.html')",
        metavar="O",
    )
    default_width = 380
    parser.add_argument(
        "--width",
        type=int,
        help=f"Fig width [px] (Default: {default_width})",
        default=default_width,
        metavar="",
    )
    default_height = 380
    parser.add_argument(
        "--height",
        type=int,
        help=f"Fig height [px] (Default: {default_height})",
        default=default_height,
        metavar="",
    )
    parser.add_argument(
        "--show_letter",
        help="Show functional category letter on piechart (Default: OFF)",
        action="store_true",
    )
    parser.add_argument(
        "--sort",
        help="Enable descending sort by number count (Default: OFF)",
        action="store_true",
    )

    args = parser.parse_args()

    if args.outfile.suffix != ".html":
        err_msg = f"Output file extension must be '.html' ({args.outfile})"
        parser.error(err_msg)

    return args


if __name__ == "__main__":
    main()
