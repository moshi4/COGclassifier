from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd


def plot_cog_count_barchart(
    data: str | Path | pd.DataFrame,
    outfile: str | Path | None = None,
    *,
    fig_width: int = 440,
    fig_height: int = 340,
    bar_width: int = 12,
    y_limit: float | None = None,
    percent_style: bool = False,
    sort: bool = False,
    dpi: int = 100,
) -> alt.Chart:
    """Plot altair barchart from COG count dataframe

    Parameters
    ----------
    data : str | Path | pd.DataFrame
        COG count file or dataframe
    outfile : str | Path | None, optional
        Barchart output file (`*.png`|`*.svg`|`*.html`)
    fig_width : int, optional
        Figure pixel width
    fig_height : int, optional
        Figure pixel height
    bar_width : int, optional
        Figure pixel bar width
    y_limit : float | None, optional
        Y-axis max limit value
    percent_style : bool, optional
        Plot y-axis as percent(%) instead of count number
    sort : bool, optional
        Enable descending sort by count
    dpi : int, option
        Figure DPI

    Returns
    -------
    barchart : alt.Chart
        Altair barchart
    """
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        df = pd.read_csv(data, sep="\t", encoding="utf-8")

    # Set 'percent style' or 'count style'
    if percent_style:
        yfield, ytitle, yformat = "RATIO", "Percent of Sequences", ".0%"
        y_limit = None if y_limit is None else y_limit / 100
    else:
        yfield, ytitle, yformat = "COUNT", "Number of Sequences", "c"

    # Set sort style (descending by count)
    df = df.sort_values("COUNT", ascending=False) if sort else df

    # Calculate count rate (%)
    df["RATIO"] = df["COUNT"] / df["COUNT"].sum()
    df["RATIO(%)"] = df["RATIO"].map("{:.2%}".format)

    # If no y_limit defined by user, set appropriate value
    ymax = df[yfield].max()
    y_limit = ymax + (ymax * 0.05) if y_limit is None else y_limit

    df["L_DESCRIPTION"] = df["LETTER"] + " : " + df["DESCRIPTION"]
    barchart = (
        alt.Chart(df, title="COG Functional Classification")
        .mark_bar(stroke="black", strokeWidth=0.2)
        .encode(
            x=alt.X("LETTER", title="Functional Category", sort=None),
            y=alt.Y(
                yfield,
                title=ytitle,
                axis=alt.Axis(format=yformat),
                scale=alt.Scale(domainMax=y_limit, clamp=True),
            ),
            tooltip=["DESCRIPTION", "LETTER", "COUNT", "RATIO(%)"],
            color=alt.Color(
                "L_DESCRIPTION",
                title="",
                scale=alt.Scale(
                    domain=df["L_DESCRIPTION"].to_list(),
                    range=df["COLOR"].to_list(),
                ),
            ),
            stroke=alt.condition(
                alt.datum[yfield] > 0, alt.value("black"), alt.value("transparent")
            ),
        )
        .properties(width=fig_width, height=fig_height)
        .configure_title(fontSize=15)
        .configure_legend(labelLimit=0)
        .configure_axisX(labelAngle=0, tickSize=0)
        .configure_mark(
            stroke="black", width=bar_width, strokeWidth=0.15, strokeOpacity=1
        )
    )
    if outfile is not None:
        if Path(outfile).suffix == ".png":
            barchart.save(outfile, ppi=dpi)
        else:
            barchart.save(outfile)

    return barchart


def plot_cog_count_piechart(
    data: str | Path | pd.DataFrame,
    outfile: str | Path | None = None,
    *,
    fig_width: int = 380,
    fig_height: int = 380,
    show_letter: bool = False,
    sort: bool = False,
    dpi: int = 100,
) -> alt.LayerChart:
    """Plot altair piechart from COG count dataframe

    Parameters
    ----------
    df : str | Path | pd.DataFrame
        COG count file or dataframe
    outfile : str | Path | None, optional
        Piechart output file (`*.png`|`*.svg`|`*.html`)
    fig_width : int, optional
        Figure pixel width
    fig_height : int, optional
        Figure pixel height
    show_letter : bool, optional
        Show letter on piechart
    sort : bool, optional
        Enable count descending sort
    dpi : int, optional
        Figure DPI

    Returns
    -------
    piechart : alt.LayerChart
        Altair piechart
    """
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        df = pd.read_csv(data, sep="\t", encoding="utf-8")

    # Remove 0 Count (no assigned category)
    df = df[df["COUNT"] != 0]

    # Set sort style ("descending by count" or "ascending by index")
    if sort:
        sort_field, sort_order = "COUNT", "descending"
        df = df.sort_values("COUNT", ascending=False)
    else:
        df = df.reset_index()
        sort_field, sort_order = "index", "ascending"

    df["L_DESCRIPTION"] = df["LETTER"] + " : " + df["DESCRIPTION"]

    df["RATIO"] = df["COUNT"] / df["COUNT"].sum() * 100
    visible_letters = []
    if show_letter:
        # Only visible 'LETTER' more than 1.0% ratio
        for ratio, letter in zip(df["RATIO"], df["LETTER"]):
            visible_letter = letter if ratio >= 1.0 else ""
            visible_letters.append(visible_letter)
    else:
        visible_letters = [""] * len(df)
    df["VISIBLE_LETTER"] = visible_letters

    # Format ratio to percentage (e.g. 10.293... -> "10.29%"")
    df["RATIO(%)"] = [f"{r:.2f}%" for r in df["RATIO"]]

    base = alt.Chart(
        df,
        title="COG Functional Classification",
    ).encode(
        theta=alt.Theta("COUNT", stack=True),
        tooltip=["DESCRIPTION", "LETTER", "COUNT", "RATIO(%)"],
        order=alt.Order(sort_field, sort=sort_order),
        color=alt.Color(
            "L_DESCRIPTION",
            title="",
            scale=alt.Scale(
                domain=df["L_DESCRIPTION"].to_list(),
                range=df["COLOR"].to_list(),
            ),
        ),
    )

    outer_radius = int(min(fig_width, fig_height) / 2)
    piechart = base.mark_arc(outerRadius=outer_radius)
    text = base.mark_text(
        radius=outer_radius - 15,
        size=10,
        stroke="black",
        strokeWidth=1.0,
        strokeOpacity=1.0,
    ).encode(text="VISIBLE_LETTER")

    piechart_with_text = (
        alt.layer(piechart + text)
        .properties(width=fig_width, height=fig_height)
        .configure_title(fontSize=15, offset=10)
        .configure_legend(labelLimit=0)
        .configure_view(strokeWidth=0)
        .configure_mark(stroke="white", strokeWidth=1.0, strokeOpacity=1.0)
    )
    if outfile is not None:
        if Path(outfile).suffix == ".png":
            piechart_with_text.save(outfile, ppi=dpi)
        else:
            piechart_with_text.save(outfile)

    return piechart_with_text
