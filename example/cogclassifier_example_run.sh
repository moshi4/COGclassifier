#!/usr/bin/bash
OUTDIR=./output
mkdir -p $OUTDIR

# Run COGclassifier for 3 species example dataset
ECOLI_OUTDIR=$OUTDIR/ecoli_cog_classifier
CYANO_OUTDIR=$OUTDIR/synechocystis_cog_classifier
MYCO_OUTDIR=$OUTDIR/mycoplasma_cog_classifier

COGclassifier -i ./input/ecoli.faa -o $ECOLI_OUTDIR
COGclassifier -i ./input/synechocystis.faa -o $CYANO_OUTDIR
COGclassifier -i ./input/mycoplasma.faa -o $MYCO_OUTDIR

# Run barchart & piechart plot script using E.coli classifier count result
COUNT_RESULT_FILE=${ECOLI_OUTDIR}/classifier_count.tsv

plot_cog_classifier_barchart -i $COUNT_RESULT_FILE \
                             -o $OUTDIR/01_barchart_default.html

plot_cog_classifier_piechart -i $COUNT_RESULT_FILE \
                             -o $OUTDIR/02_piechart_default.html \
                             --show_letter \

plot_cog_classifier_piechart -i $COUNT_RESULT_FILE \
                             -o $OUTDIR/03_piechart_default_sort.html \
                             --show_letter \
                             --sort

plot_cog_classifier_barchart -i $COUNT_RESULT_FILE \
                             -o $OUTDIR/04_barchart_full_option.html \
                             --width 300 \
                             --height 340 \
                             --bar_width 7 \
                             --y_limit 15 \
                             --percent_style \
                             --sort

plot_cog_classifier_piechart -i $COUNT_RESULT_FILE \
                             -o $OUTDIR/05_piechart_full_option.html \
                             --width 250 \
                             --height 250 \
