import argparse
from pathlib import Path
from typing import Optional

import pandas as pd
from cogclassifier.COGclassifier import plot_cog_classifier_barchart


def main():
    """Plot barchart from COGclassifier count results"""
    # Get argument values
    args = get_args()
    infile: Path = args.infile
    outfile: Path = args.outfile
    width: int = args.width
    height: int = args.height
    bar_width: int = args.bar_width
    y_limit: Optional[int] = args.y_limit
    percent_style: bool = args.percent_style
    sort: bool = args.sort

    # Plot barchart
    plot_cog_classifier_barchart(
        df=pd.read_csv(infile, sep="\t"),
        html_outfile=outfile,
        fig_width=width,
        fig_height=height,
        bar_width=bar_width,
        y_limit=y_limit,
        percent_style=percent_style,
        sort=sort,
    )


def get_args() -> argparse.Namespace:
    """Get arguments

    Returns:
        argparse.Namespace: Argument values
    """
    parser = argparse.ArgumentParser(
        description="Plot barchart of COGclassifier count results",
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
    default_width = 520
    parser.add_argument(
        "--width",
        type=int,
        help=f"Fig width [px] (Default: {default_width})",
        default=default_width,
        metavar="",
    )
    default_height = 340
    parser.add_argument(
        "--height",
        type=int,
        help=f"Fig height [px] (Default: {default_height})",
        default=default_height,
        metavar="",
    )
    default_bar_width = 15
    parser.add_argument(
        "--bar_width",
        type=int,
        help=f"Fig bar width [px] (Default: {default_bar_width})",
        default=default_bar_width,
        metavar="",
    )
    default_y_limit = None
    parser.add_argument(
        "--y_limit",
        type=int,
        help="Y-axis max limit value (Default: 'Auto')",
        default=default_y_limit,
        metavar="",
    )
    parser.add_argument(
        "--percent_style",
        help="Plot y-axis as percent style instead of number count (Default: OFF)",
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
