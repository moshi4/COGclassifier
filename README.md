# COGclassifier

![Python3](https://img.shields.io/badge/Language-Python3-steelblue)
![OS](https://img.shields.io/badge/OS-Windows_|_MacOS_|_Linux-steelblue)
![License](https://img.shields.io/badge/License-MIT-steelblue)
[![Latest PyPI version](https://img.shields.io/pypi/v/cogclassifier.svg)](https://pypi.python.org/pypi/cogclassifier)  

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Workflow](#workflow)
- [Command Usage](#command-usage)
- [Output Contents](#output-contents)
- [Customize charts](#customize-charts)

## Overview

COG(Cluster of Orthologous Genes) is a database that plays an important role in the annotation, classification, and analysis of microbial gene function.
Functional annotation, classification, and analysis of each gene in newly sequenced bacterial genomes using the COG database is a common task.
However, there was no COG functional classification command line software that is user-friendly and capable of producing publication-ready figures.
Therefore, I developed COGclassifier to fill this need.
COGclassifier can automatically perform the processes from searching query sequences into the COG database, to annotation and classification of gene functions, to generation of publication-ready figures (See figure below).

![ecoli_barchart_fig](https://raw.githubusercontent.com/moshi4/COGclassifier/main/images/ecoli/classifier_count_barchart.png)  
Fig.1: Barchart of COG funcitional category classification result for E.coli

![ecoli_piechart_sort_fig](https://raw.githubusercontent.com/moshi4/COGclassifier/main/images/ecoli/classifier_count_piechart_sort.png)  
Fig.2: Piechart of COG funcitional category classification result for E.coli

## Installation

COGclassifier is implemented in Python3.

Install PyPI stable version with pip:

    pip install cogclassifier

Install latest development version with pip:

    pip install git+https://github.com/moshi4/COGclassifier.git

COGclassifier use `RPS-BLAST` for COG database search.  
RPS-BLAST(v2.13.0) is packaged in [src/cogclassifier/bin](https://github.com/moshi4/COGclassifier/tree/main/src/cogclassifier/bin) directory.  

## Workflow

Description of COGclassifier's automated workflow.

### 1. Download COG & CDD resources

Download 4 required COG & CDD files from FTP site.

- `fun-20.tab` (<https://ftp.ncbi.nih.gov/pub/COG/COG2020/data/fun-20.tab>)  
    Descriptions of COG functional categories.  

    <details>
    <summary>Show more information</summary>

    > Tab-delimited plain text file with descriptions of COG functional categories  
    > Columns:  
    >  
    > 1\. Functional category ID (one letter)  
    > 2\. Hexadecimal RGB color associated with the functional category  
    > 3\. Functional category description  
    > Each line corresponds to one functional category. The order of the categories is meaningful (reflects a hierarchy of functions; determines the order of display)  
    >
    > (From <https://ftp.ncbi.nih.gov/pub/COG/COG2020/data/Readme.2020-11-25.txt>)

    </details>

- `cog-20.def.tab` (<https://ftp.ncbi.nih.gov/pub/COG/COG2020/data/cog-20.def.tab>)  
    COG descriptions such as 'COG ID', 'COG functional category', 'COG name', etc...  

    <details>
    <summary>Show more information</summary>

    > Tab-delimited plain text file with COG descriptions  
    > Columns:  
    >  
    > 1\. COG ID  
    > 2\. COG functional category (could include multiple letters in the order of importance)  
    > 3\. COG name  
    > 4\. Gene associated with the COG (optional)  
    > 5\. Functional pathway associated with the COG (optional)  
    > 6\. PubMed ID, associated with the COG (multiple entries are semicolon-separated; optional)  
    > 7\. PDB ID of the structure associated with the COG (multiple entries are semicolon-separated; optional)  
    > Each line corresponds to one COG. The order of the COGs is arbitrary (displayed in the lexicographic order)  
    >
    > (From <https://ftp.ncbi.nih.gov/pub/COG/COG2020/data/Readme.2020-11-25.txt>)

    </details>

- `cddid.tbl.gz` (<https://ftp.ncbi.nih.gov/pub/mmdb/cdd/>)  
    Summary information about the CD(Conserved Domain) model.  

    <details>
    <summary>Show more information</summary>

    >"cddid.tbl.gz" contains summary information about the CD models in this
    >distribution, which are part of the default "cdd" search database and are
    >indexed in NCBI's Entrez database. This is a tab-delimited text file, with a
    >single row per CD model and the following columns:  
    >  
    >PSSM-Id (unique numerical identifier)  
    >CD accession (starting with 'cd', 'pfam', 'smart', 'COG', 'PRK' or "CHL')  
    >CD "short name"  
    >CD description  
    >PSSM-Length (number of columns, the size of the search model)  
    >
    > (From <https://ftp.ncbi.nih.gov/pub/mmdb/cdd/README>)

    </details>

- `Cog_LE.tar.gz` (<https://ftp.ncbi.nih.gov/pub/mmdb/cdd/little_endian/>)  
    COG database, a part of CDD(Conserved Domain Database), for RPS-BLAST search

### 2. RPS-BLAST search against COG database

Run query sequences RPS-BLAST against COG database [Default: E-value = 1e-2].
Best-hit (=lowest e-value) blast result is extracted and
best-hit COG database results are used in next functional classification step.

### 3. Classify query sequences into COG functional category

From best-hit results, extract COG functional category relationships as described below.  

1. Best-hit results -> CDD ID
2. CDD ID -> COG ID (From `cddid.tbl`)
3. COG ID -> COG Functional Category Letter (From `cog-20.def.tab`)
4. COG Functional Category Letter -> COG Functional Category Definition (From `fun-20.tab`)

> :warning:
> If functional category with multiple letters exists, first letter is treated as functional category
> (e.g. COG4862 has `KTN` multiple letters. A letter `K` is treated as functional category).

Using the above information, the number of query sequences classified into each COG functional category is calculated and
functional annotation and classification results are output.

## Command Usage

### Basic Command

    COGclassifier -i [query protein fasta file] -o [output directory]

### Options

    -h, --help            show this help message and exit
    -i , --infile         Input query protein fasta file
    -o , --outdir         Output directory
    -d , --download_dir   Download COG & CDD FTP data directory (Default: './cog_download')
    -t , --thread_num     RPS-BLAST num_thread parameter (Default: MaxThread - 1)
    -e , --evalue         RPS-BLAST e-value parameter (Default: 0.01)
    -v, --version         Print version information

### Example Command

Classify E.coli protein sequences into COG functional category ([ecoli.faa](https://github.com/moshi4/COGclassifier/blob/main/example/input/ecoli.faa?raw=true)):  

    COGclassifier -i ./example/input/ecoli.faa -o ./ecoli_cog_classifier

## Output Contents

COGclassifier outputs 4 result text files and 3 html format chart files.  

- **`rpsblast_result.tsv`** ([example](https://github.com/moshi4/COGclassifier/blob/main/example/output/mycoplasma_cog_classifier/rpsblast_result.tsv))  

  RPS-BLAST against COG database result (format = `outfmt 6`).  

- **`classifier_result.tsv`** ([example](https://github.com/moshi4/COGclassifier/blob/main/example/output/mycoplasma_cog_classifier/classifier_result.tsv))  

  Query sequences classified into COG functional category result.  
  This file contains all classified query sequences and associated COG information.  

    <details>
    <summary>Table of detailed tsv format information (9 columns)</summary>

    | Columns          | Contents                               | Example Value                       |
    | ---------------- | -------------------------------------- | ----------------------------------- |
    | QUERY_ID         | Query ID                               | NP_414544.1                         |
    | COG_ID           | COG ID of RPS-BLAST top hit result     | COG0083                             |
    | CDD_ID           | CDD ID of RPS-BLAST top hit result     | 223161                              |
    | EVALUE           | RPS-BLAST top hit evalue               | 2.5e-150                            |
    | IDENTITY         | RPS-BLAST top hit identity             | 45.806                              |
    | GENE_NAME        | Abbreviated gene name                  | ThrB                                |
    | COG_NAME         | COG gene name                          | Homoserine kinase                   |
    | COG_LETTER       | Letter of COG functional category      | E                                   |
    | COG_DESCRIPTION  | Description of COG functional category | Amino acid transport and metabolism |

    </details>

- **`classifier_count.tsv`** ([example](https://github.com/moshi4/COGclassifier/blob/main/example/output/ecoli_cog_classifier/classifier_count.tsv))  
  
  Count classified sequences per COG functional category result.  

    <details>
    <summary>Table of detailed tsv format information (4 columns)</summary>

    | Columns     | Contents                                | Example Value                                   |
    | ------------| --------------------------------------- | ----------------------------------------------- |
    | LETTER      | Letter of COG functional category       | J                                               |
    | COUNT       | Count of COG classified sequence        | 259                                             |
    | COLOR       | Symbol color of COG functional category | #FCCCFC                                         |
    | DESCRIPTION | Description of COG functional category  | Translation, ribosomal structure and biogenesis |

    </details>

- **`classifier_stats.txt`** ([example](https://github.com/moshi4/COGclassifier/blob/main/example/output/ecoli_cog_classifier/classifier_stats.txt))  

  The percentages of the classified sequences are described as example below.  
  > 86.35% (3575 / 4140) sequences classified into COG functional category.

- **`classifier_count_barchart.html`**  

  Barchart of COG funcitional category classification result.  
  COGclassifier uses [`Altair`](https://altair-viz.github.io/) visualization library for plotting html format charts.  
  In web browser, Altair charts interactively display tooltips and can export image as PNG or SVG format.

  ![classifier_count_barchart](https://raw.githubusercontent.com/moshi4/COGclassifier/main/images/vega-lite_functionality.png)

- **`classifier_count_piechart.html`**  

  Piechart of COG funcitional category classification result.  
  Functional category with percentages less than 1% don't display letter on piechart.  

  ![classifier_count_piechart](https://raw.githubusercontent.com/moshi4/COGclassifier/main/images/ecoli/classifier_count_piechart.png)

- **`classifier_count_piechart_sort.html`**  

  Piechart with descending sort by count.  
  Functional category with percentages less than 1% don't display letter on piechart.  

  ![classifier_count_piechart](https://raw.githubusercontent.com/moshi4/COGclassifier/main/images/ecoli/classifier_count_piechart_sort.png)

## Customize charts

COGclassifier also provides barchart & piechart plotting scripts to customize charts appearence.
Each script can plot the following feature charts from `classifier_count.tsv`. See [wiki](https://github.com/moshi4/COGclassifier/wiki) for details.

- Features of **plot_cog_classifier_barchart** script  
  
  - Adjust figure width, height, barwidth
  - Plot charts with percentage style instead of count number style
  - Fix maximum value of Y-axis  
  - Descending sort by count number or not  
  - Plot charts from user-customized 'classifier_count.tsv'

- Features of **plot_cog_classifier_piechart** script  

  - Adjust figure width, height
  - Descending sort by count number or not
  - Show letter on piechart or not
  - Plot charts from user-customized 'classifier_count.tsv'
