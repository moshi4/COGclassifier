#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import os
import platform
import re
import shutil
import subprocess as sp
from collections import defaultdict
from dataclasses import astuple, dataclass
from distutils.version import StrictVersion
from pathlib import Path
from typing import Dict, List, Optional, Union

import altair as alt
import pandas as pd
import requests

__version__ = "1.0.0"


def main():
    """COGclassifier main function"""
    # Get argument values
    args = get_args()
    query_fasta_file: Path = args.infile
    outdir: Path = args.outdir
    download_dir: Path = args.download_dir
    thread_num: int = args.thread_num
    evalue: float = args.evalue

    outdir.mkdir(exist_ok=True)
    download_dir.mkdir(exist_ok=True)

    print("# Step1: Download COG & CDD FTP data")
    # Setup COG functional category files
    cog_fun_ftp_url = "https://ftp.ncbi.nih.gov/pub/COG/COG2020/data/fun-20.tab"
    cog_def_ftp_url = "https://ftp.ncbi.nih.gov/pub/COG/COG2020/data/cog-20.def.tab"

    cog_fun_file = ftp_download(cog_fun_ftp_url, download_dir)
    cog_def_file = ftp_download(cog_def_ftp_url, download_dir)

    # Setup NCBI CDD files
    cddid_tbl_ftp_url = "https://ftp.ncbi.nih.gov/pub/mmdb/cdd/cddid.tbl.gz"
    cog_le_ftp_url = "https://ftp.ncbi.nih.gov/pub/mmdb/cdd/little_endian/Cog_LE.tar.gz"

    cddid_tbl_gzfile = ftp_download(cddid_tbl_ftp_url, download_dir)
    cddid_tbl_file = cddid_tbl_gzfile.with_suffix("")
    unpack_gzfile(cddid_tbl_gzfile, cddid_tbl_file)

    cog_le_targz_file = ftp_download(cog_le_ftp_url, download_dir)
    cog_le_dir = download_dir / "Cog_LE"
    unpack_targz_file(cog_le_targz_file, cog_le_dir)
    rpsblast_db = cog_le_dir / "Cog"

    # RPS-BLAST against COG database
    print("\n# Step2: Running RPS-BLAST against COG database.")
    rpsblast_result_file = outdir / "rpsblast_result.tsv"
    rpsblast_cmd = (
        f"rpsblast -query {query_fasta_file} -db {rpsblast_db} -outfmt 6 "
        f"-out {rpsblast_result_file} -evalue {evalue} -num_threads {thread_num} "
    )
    add_bin_path()
    rpsblast_cmd = rpsblast_cmd + "-mt_mode 1" if has_mt_mode_option() else rpsblast_cmd
    print(f"$ {rpsblast_cmd}")
    sp.run(rpsblast_cmd, shell=True)
    print("Finished RPS-BLAST search.")

    # Extract blast top-hit results
    blast_results = BlastResult.parse(rpsblast_result_file)
    top_hit_blast_results = BlastResult.extract_top_hit(blast_results)
    # top_hit_rpsblast_result_file = outdir / "top_hit_rpsblast_result.tsv"
    # BlastResult.write(top_hit_rpsblast_result_file, top_hit_blast_results)

    # Classify query sequences into COG functional category
    print("\n# Step3: Classify sequences into COG functional category.")
    cddid2cogid = get_cddid2cogid(cddid_tbl_file)
    cogid2definition = CogDefinition.parse(cog_def_file)
    letter2func_category = CogFuncCategory.parse(cog_fun_file)

    classifier_results: List[ClassifierResult] = []
    letter2count: Dict[str, int] = defaultdict(int)
    for br in top_hit_blast_results:
        queryid, cddid = br.qaccver, br.saccver.replace("CDD:", "")
        cogid = cddid2cogid[cddid]
        cog_def = cogid2definition.get(cogid)
        if cog_def is None:
            continue
        letter = cog_def.func_category[0]
        cog_fun = letter2func_category[letter]
        classifier_result = ClassifierResult(
            queryid,
            cogid,
            cddid,
            br.evalue,
            br.pident,
            cog_def.gene_name,
            cog_def.cog_name,
            letter,
            cog_fun.description,
        )
        classifier_results.append(classifier_result)
        letter2count[letter] += 1

    classifier_result_file = outdir / "classifier_result.tsv"
    ClassifierResult.write(classifier_result_file, classifier_results)

    # Summarize statistics
    all_seq_count = count_fasta_seq(query_fasta_file)
    cog_classifier_seq_count = len(classifier_results)
    classifier_ratio = (cog_classifier_seq_count / all_seq_count) * 100
    classifier_stats_file = outdir / "classifier_stats.txt"
    with open(classifier_stats_file, "w") as f:
        stats_contents = (
            f"{classifier_ratio:.2f}% ({cog_classifier_seq_count} / {all_seq_count}) "
            + "sequences classified into COG functional category.\n"
        )
        f.write(stats_contents)
    print(stats_contents + f"\nSee output directory '{outdir}' for details.")

    # Format classifier count dataframe
    df_data = []
    for fc in letter2func_category.values():
        color = f"#{fc.color}"
        df_data.append([fc.letter, letter2count[fc.letter], color, fc.description])
    df = pd.DataFrame(df_data, columns=["LETTER", "COUNT", "COLOR", "DESCRIPTION"])

    # Output classifier count result
    classifier_count_file = outdir / "classifier_count.tsv"
    df.to_csv(classifier_count_file, sep="\t", index=False)

    # Plot classifer count barchart
    barchart_fig_file = outdir / "classifier_count_barchart.html"
    plot_cog_classifier_barchart(df.copy(), barchart_fig_file)

    # Plot classifer count piechart
    piechart_fig_file = outdir / "classifier_count_piechart.html"
    plot_cog_classifier_piechart(
        df.copy(), piechart_fig_file, show_letter=True, sort=False
    )
    piechart_sort_fig_file = outdir / "classifier_count_piechart_sort.html"
    plot_cog_classifier_piechart(
        df.copy(), piechart_sort_fig_file, show_letter=True, sort=True
    )


def ftp_download(url: str, outdir: Union[str, Path], overwrite: bool = False) -> Path:
    """Download file from FTP site

    Args:
        url (str): FTP site url for download
        outdir (Union[str, Path]): Output directory
        overwrite (bool, optional): Overwrite or not

    Returns:
        Path: Download file path
    """
    os.makedirs(outdir, exist_ok=True)
    download_file = Path(outdir) / Path(url).name
    print(f"Download '{url}'")

    if download_file.exists() and not overwrite:
        print(f"=> Already file exists '{download_file}'.")
        return download_file

    try:
        res = requests.get(url, stream=True)
        with open(download_file, "wb") as f:
            f.write(res.content)
        print(f"=> Successfully downloaded '{download_file}'.")
        return download_file
    except requests.exceptions.ConnectionError as err:
        print("Failed to download file. Please check network connection.\n", err)
        exit(1)


def unpack_gzfile(
    target_file: Union[str, Path], unpacked_file: Union[str, Path]
) -> None:
    """Unpack GZIP file

    Args:
        target_file (Union[str, Path]): Target file to unpack
        unpacked_file (Union[str, Path]): Unpacked file
    """
    with gzip.open(target_file, "rb") as f:
        content = f.read()
    with open(unpacked_file, "wb") as f:
        f.write(content)


def unpack_targz_file(target_file: Union[str, Path], outdir: Union[str, Path]) -> None:
    """Unpack TARGZ file

    Args:
        target_file (Union[str, Path]): Traget file to unpack
        outdir (Union[str, Path]): Output directory for unpacked files
    """
    shutil.unpack_archive(target_file, outdir)


def add_bin_path() -> None:
    """Add executable binary (rpsblast) path to PATH"""
    os_name = platform.system()  # 'Windows' or 'Darwin' or 'Linux'
    bin_path = Path(__file__).parent / "bin" / os_name
    env_path = f"{bin_path}:{os.environ['PATH']}"
    os.environ["PATH"] = env_path


def has_mt_mode_option() -> bool:
    """Check installed rpsblast has mt_mode option (blast >= v2.12.0)

    Returns:
        bool: mt_mode exists or not

    Notes:
        mt_mode defines multi-thread mode ('split-by-database' or 'split-by-query').
        In 'mt_mode 1'(split-by-query), multi-thread is efficiently used and fast.
        See https://www.ncbi.nlm.nih.gov/books/NBK571452/ in details.
    """

    def _get_rpsblast_version() -> str:
        output = sp.run("rpsblast -version", shell=True, capture_output=True, text=True)
        return re.match(r"rpsblast: (\d+.\d+.\d+)", output.stdout).groups()[0]

    rpsblast_version = StrictVersion(_get_rpsblast_version())
    return rpsblast_version >= StrictVersion("2.12.0")


def get_cddid2cogid(cddid_tbl_file: Union[str, Path]) -> Dict[str, str]:
    """Get CDD_ID to COG_ID dict from CDD_ID conversion table file

    Args:
        cddid_tbl_file (Union[str, Path]): CDD_ID conversion table file

    Returns:
        Dict[str, str]: CDD_ID to COG_ID conversion dict
    """
    cddid2cogid = defaultdict(str)
    with open(cddid_tbl_file) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            cddid, accid = row[0], row[1]
            if accid.startswith("COG"):
                cddid2cogid[cddid] = accid
    return cddid2cogid


def count_fasta_seq(fasta_file: Union[str, Path]) -> int:
    """Count fasta sequence number

    Args:
        fasta_file (Union[str, Path]): Fasta format file

    Returns:
        int: Fasta sequence number
    """
    with open(fasta_file) as f:
        return len(list(filter(lambda l: l.startswith(">"), f.readlines())))


def plot_cog_classifier_barchart(
    df: pd.DataFrame,
    html_outfile: Union[str, Path],
    fig_width: int = 520,
    fig_height: int = 340,
    bar_width: int = 15,
    y_limit: Optional[float] = None,
    percent_style: bool = False,
    sort: bool = False,
) -> None:
    """Plot altair barchart from classifier count dataframe

    Args:
        df (pd.DataFrame): Classifier count dataframe
        html_outfile (Union[str, Path]): Barchart html file
        fig_width (int): Figure width (px)
        fig_height (int): Figure height (px)
        bar_width (int): Figure bar width (px)
        y_limit (Optional[float]): y-axis max limit value
        percent_style (bool): Plot y-axis as percent(%) instead of count number
        sort (bool): Enable descending sort by count
    """
    # Set 'percent style' or 'count style'
    if percent_style:
        yfield, ytitle, yformat = "RATIO", "Percent of Sequences COG Classified", ".0%"
        y_limit = None if y_limit is None else y_limit / 100
    else:
        yfield, ytitle, yformat = "COUNT", "Number of Sequences COG Classified", "c"

    # Set sort style (descending by count)
    df = df.sort_values("COUNT", ascending=False) if sort else df

    # Calculate count rate (%)
    df["RATIO"] = df["COUNT"] / df["COUNT"].sum()
    df["RATIO(%)"] = df["RATIO"].map("{:.2%}".format)

    # If no y_limit defined by user, set appropriate value
    y_limit = df[yfield].max() if y_limit is None else y_limit

    df["L_DESCRIPTION"] = df["LETTER"] + " : " + df["DESCRIPTION"]
    barchart = (
        alt.Chart(df, title="COG Functional Classification")
        .mark_bar()
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
        )
        .properties(width=fig_width, height=fig_height)
        .configure_title(fontSize=15)
        .configure_legend(labelLimit=0)
        .configure_axisX(labelAngle=0, tickSize=0)
        .configure_mark(
            stroke="black", width=bar_width, strokeWidth=0.15, strokeOpacity=1
        )
    )
    barchart.save(html_outfile)


def plot_cog_classifier_piechart(
    df: pd.DataFrame,
    html_outfile: Union[str, Path],
    fig_width: int = 380,
    fig_height: int = 380,
    show_letter: bool = False,
    sort: bool = False,
) -> None:
    """Plot altair piechart from classifier count dataframe

    Args:
        df (pd.DataFrame): Classifier count dataframe
        html_outfile (Union[str, Path]): Piechart html file
        fig_width (int): Figure width (px)
        fig_height (int): Figure height (px)
        show_letter (bool): Show letter on piechart
        sort (bool): Enable count descending sort
    """
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
        for (ratio, letter) in zip(df["RATIO"], df["LETTER"]):
            visible_letter = letter if ratio >= 1.0 else ""
            visible_letters.append(visible_letter)
    else:
        visible_letters = [""] * len(df)
    df["VISIBLE_LETTER"] = visible_letters

    # Format ratio to percentage (e.g. 10.293... -> "10.29%"")
    df["RATIO(%)"] = [f"{r:.2f}%" for r in df["RATIO"]]

    base = alt.Chart(df, title="COG Functional Classification",).encode(
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
    piechart_with_text.save(html_outfile)


@dataclass
class CogDefinition:
    """COG Definition DataClass"""

    cog_id: str
    func_category: str
    cog_name: str
    gene_name: str
    func_pathway: str
    pubmed_id: str
    pdb_id: str

    @staticmethod
    def parse(cog_def_file: Union[str, Path]) -> Dict[str, CogDefinition]:
        """Parse COG definition file (cog-20.def.tab)

        Args:
            cog_def_file (Union[str, Path]): COG definition file

        Returns:
            Dict[str, CogDefinition]: COG_ID to CogDefinition dict
        """
        cog_defs = []
        with open(cog_def_file, encoding="cp1252") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                cog_defs.append(CogDefinition(*row))
        return {cd.cog_id: cd for cd in cog_defs}


@dataclass
class CogFuncCategory:
    """COG Functional Category DataClass"""

    letter: str
    color: str
    description: str

    @staticmethod
    def parse(cog_fun_file: Union[str, Path]) -> Dict[str, CogFuncCategory]:
        """Parse COG functional category file (fun-20.tab)

        Args:
            cog_fun_file (Union[str, Path]): COG functional category file

        Returns:
            Dict[str, CogFuncCategory]: A letter to CogFuncCategory dict
        """
        cog_funs = []
        with open(cog_fun_file) as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                cog_funs.append(CogFuncCategory(*row))
        return {cf.letter: cf for cf in cog_funs}


@dataclass
class BlastResult:
    """Blast Result DataClass"""

    qaccver: str  # Query Accession Version
    saccver: str  # Subject Accession Version
    pident: float  # Percent Identity
    length: int  # Alignment Length
    mismatch: int
    gapopen: int
    qstart: int
    qend: int
    sstart: int
    send: int
    evalue: float
    bitscore: float

    @staticmethod
    def parse(blast_tsv_file: Union[str, Path]) -> List[BlastResult]:
        """Parse tsv format blast result file

        Args:
            blast_tsv_file (Union[str, Path]): TSV format blast result file
        Returns:
            List[BlastResult]: BlastResult list
        """
        blast_results: List[BlastResult] = []
        with open(blast_tsv_file) as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                # Ignore header line
                if row[0].startswith("#"):
                    continue
                # Cast each row value to appropriate type
                typed_row = []
                for idx, val in enumerate(row):
                    if 0 <= idx <= 1:
                        typed_row.append(str(val))
                    elif 3 <= idx <= 9:
                        typed_row.append(int(val))
                    else:
                        typed_row.append(float(val))

                blast_results.append(BlastResult(*typed_row))

        return blast_results

    @staticmethod
    def extract_top_hit(blast_results: List[BlastResult]) -> List[BlastResult]:
        """Extract top hit blast results (no duplicated query info)

        Args:
            blast_results (List[BlastResult]): Blast search results

        Returns:
            List[BlastResult]: Top hit blast results
        """
        top_hits = []
        top_hit_blast_results = []
        for br in blast_results:
            if br.qaccver in top_hits:
                continue
            top_hits.append(br.qaccver)
            top_hit_blast_results.append(br)
        return top_hit_blast_results

    @staticmethod
    def write(
        blast_tsv_outfile: Union[str, Path], blast_results: List[BlastResult]
    ) -> None:
        """Write BlastResult list with TSV format

        Args:
            blast_tsv_outfile (Union[str, Path]): Output tsv file
            blast_results (List[BlastResult]): Blast results to write
        """
        output_contents = ""
        for br in blast_results:
            output_contents += "\t".join([str(e) for e in astuple(br)]) + "\n"
        with open(blast_tsv_outfile, "w") as f:
            f.write(output_contents)


@dataclass
class ClassifierResult:
    """Classifier Result DataClass"""

    queryid: str
    cogid: str
    cddid: str
    evalue: float
    pident: float
    gene_name: str
    cog_name: str
    letter: str
    description: str

    @staticmethod
    def write(
        result_tsv_outfile: Union[str, Path], classifier_results: List[ClassifierResult]
    ) -> None:
        """Write ClassifierResult list with TSV format

        Args:
            result_tsv_outfile (Union[str, Path]): Output tsv file
            classifier_results (List[ClassifierResult]): Classifier results to write
        """
        header = (
            "QUERY_ID\tCOG_ID\tCDD_ID\tEVALUE\tIDENTITY\tGENE_NAME\t"
            + "COG_NAME\tCOG_LETTER\tCOG_DESCRIPTION"
        )
        output_contents = ""
        for cr in classifier_results:
            output_contents += "\t".join([str(e) for e in astuple(cr)]) + "\n"

        with open(result_tsv_outfile, "w") as f:
            f.write(header + "\n")
            f.write(output_contents)


def get_args() -> argparse.Namespace:
    """Get arguments

    Returns:
        argparse.Namespace: Argument values
    """
    description = "Classify prokaryote protein sequences into COG functional category"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-i",
        "--infile",
        required=True,
        type=Path,
        help="Input query protein fasta file",
        metavar="",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        required=True,
        type=Path,
        help="Output directory",
        metavar="",
    )
    default_dl_dir = "./cog_download"
    parser.add_argument(
        "-d",
        "--download_dir",
        type=Path,
        help=f"Download COG & CDD FTP data directory (Default: '{default_dl_dir}')",
        default=default_dl_dir,
        metavar="",
    )
    cpu_count = os.cpu_count()
    default_thread_num = cpu_count - 1 if cpu_count is not None else 1
    parser.add_argument(
        "-t",
        "--thread_num",
        type=int,
        help=f"RPS-BLAST num_thread parameter (Default: {default_thread_num})",
        default=default_thread_num,
        metavar="",
    )
    default_evalue = 1e-2
    parser.add_argument(
        "-e",
        "--evalue",
        type=float,
        help=f"RPS-BLAST e-value parameter (Default: {default_evalue})",
        default=default_evalue,
        metavar="",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"COGclassifier: v{__version__}",
        help="Print version information",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
