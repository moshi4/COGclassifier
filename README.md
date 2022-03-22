# COGclassifier

![Python3](https://img.shields.io/badge/Language-Python3-steelblue)
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

COGclassifier is implemented in Python3 (Tested on Ubuntu20.04)

Install PyPI stable version with pip:

    pip install cogclassifier

COGclassifier requires `RPS-BLAST` for COG database search.  
Download latest BLAST executable binary from [NCBI FTP site](https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/) and add to PATH.

> :warning:
> 'mt_mode' option has been added since v2.12.0 or newer versions of BLAST.
> 'mt_mode=1' option setting makes effective use of multi-threading and is faster, so it is recommended that you install the latest version.
> See NCBI's article [Threading By Query](https://www.ncbi.nlm.nih.gov/books/NBK571452/) for details.

## Workflow

1. Download COG & CDD resources

2. RPS-BLAST query sequences against COG database

3. Classify query sequences into COG functional category

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
  COGclassifier uses `Altair` visualization library for plotting html format charts.  
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
Each script can plot the following feature charts. See [wiki](https://github.com/moshi4/COGclassifier/wiki) for details.

- Features of **plot_cog_classifier_barchart** script  
  
  - Adjust figure width, height, barwidth
  - Plot charts with percentage style instead of count number style
  - Fix maximum value of Y-axis  
  - Descending sort by count number or not  
  - Plot charts from user-customized `classifier_count.tsv`

- Features of **plot_cog_classifier_piechart** script  

  - Adjust figure width, height
  - Descending sort by count number or not
  - Show letter on piechart or not
  - Plot charts from user-customized `classifier_count.tsv`
