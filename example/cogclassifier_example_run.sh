#!/usr/bin/bash
OUTDIR=./output
mkdir -p $OUTDIR

# Run COGclassifier for 3 species example dataset
ECOLI_OUTDIR=$OUTDIR/ecoli_cog
CYANO_OUTDIR=$OUTDIR/synechocystis_cog
MYCO_OUTDIR=$OUTDIR/mycoplasma_cog

COGclassifier -i ./input/ecoli.faa -o $ECOLI_OUTDIR
COGclassifier -i ./input/synechocystis.faa -o $CYANO_OUTDIR
COGclassifier -i ./input/mycoplasma.faa -o $MYCO_OUTDIR

# Classification count dataset
COUNT_RESULT_FILE=${ECOLI_OUTDIR}/cog_count.tsv

CUSTOM_DIR=${OUTDIR}/customize
CUSTOM_COUNT_RESULT_FILE01=${CUSTOM_DIR}/cog_count_add_no_classify.tsv
CUSTOM_COUNT_RESULT_FILE02=${CUSTOM_DIR}/cog_count_change_color.tsv
mkdir -p $CUSTOM_DIR

# Run barchart plot script using E.coli classifier count result
plot_cog_count_barchart -i $COUNT_RESULT_FILE \
                           -o ${OUTDIR}/01_barchart_default.html

plot_cog_count_barchart -i $COUNT_RESULT_FILE \
                           -o ${OUTDIR}/02_barchart_adjust_figsize.html \
                           --width 280 \
                           --height 340 \
                           --bar_width 8

plot_cog_count_barchart -i $COUNT_RESULT_FILE \
                           -o ${OUTDIR}/03_barchart_percent_style.html \
                           --percent_style

plot_cog_count_barchart -i $COUNT_RESULT_FILE \
                           -o ${OUTDIR}/04_barchart_fix_yaxis.html \
                           --percent_style \
                           --y_limit 20

plot_cog_count_barchart -i $COUNT_RESULT_FILE \
                           -o ${OUTDIR}/05_barchart_descending_sort.html \
                           --sort

plot_cog_count_barchart -i $CUSTOM_COUNT_RESULT_FILE01 \
                           -o ${OUTDIR}/06_barchart_custom_add_no_classify.html

plot_cog_count_barchart -i $CUSTOM_COUNT_RESULT_FILE02 \
                           -o ${OUTDIR}/07_barchart_custom_change_color.html

# Run piechart plot script using E.coli classifier count result
plot_cog_count_piechart -i $COUNT_RESULT_FILE \
                           -o ${OUTDIR}/01_piechart_default.html \

plot_cog_count_piechart -i $COUNT_RESULT_FILE \
                           -o ${OUTDIR}/02_piechart_adjust_figsize.html \
                           --width 250 \
                           --height 250

plot_cog_count_piechart -i $COUNT_RESULT_FILE \
                           -o ${OUTDIR}/03_piechart_descending_sort.html \
                           --sort

plot_cog_count_piechart -i $COUNT_RESULT_FILE \
                           -o ${OUTDIR}/04_piechart_show_letter.html \
                           --show_letter

plot_cog_count_piechart -i $CUSTOM_COUNT_RESULT_FILE01 \
                           -o ${OUTDIR}/05_piechart_custom_add_no_classify.html \
                           --show_letter
